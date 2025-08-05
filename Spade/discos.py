from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re
from datetime import datetime, timedelta, timezone
import sys
import threading
import time
from typing import Any, Dict, List, Optional, TypedDict, cast

from requests import Response, Session

from Spade.config import Settings
from Spade.data_fetcher import fetch_DISCOS, isCacheAvaliable, saveFile
from Spade.config import settings
from Spade.spade_types import DiscosObjectList, DiscosObjectListResponse


class DiscosClient:
    """
    A thread-safe client for the ESA DISCOS API with built-in rate limit handling.
    ... (rest of docstring)
    """

    def __init__(self, settings: Settings):
        """
        Initializes the DiscosClient.
        """
        self.settings = settings
        self.session: Optional[Session] = None

        # --- Thread-safe rate limit state ---
        self._rate_limit_lock = threading.Lock()
        # The number of requests left in the current window.
        self._rate_limit_remaining: Optional[int] = None
        # The epoch time when the rate limit window resets.
        self._rate_limit_reset_time: Optional[float] = None
        # The total number of requests allowed in a window.
        self._rate_limit_total: Optional[int] = None

    def __enter__(self):
        """Enters the context manager, creating a session."""
        self.session = Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exits the context manager, closing the session."""
        if self.session:
            self.session.close()

    def _fetch_with_rate_limit_handling(
        self, url: str, params: Optional[Dict[str, str]]
    ) -> Optional[Response]:
        """
        Makes a GET request to the DISCOS API, handling rate limits proactively
        and reactively. This method is thread-safe.
        """
        if not self.session:
            raise RuntimeError("Session not available.")

        headers = {"Authorization": f"Bearer {self.settings.DISCOS_TOKEN}"}

        while True:  # Loop to allow for retries after a 429 error
            with self._rate_limit_lock:
                # --- Proactive Check ---
                # Check if we have rate limit info and if we've run out of requests
                if (
                    self._rate_limit_remaining is not None
                    and self._rate_limit_remaining < 2  # Leave a buffer of 1
                    and self._rate_limit_reset_time is not None
                ):
                    wait_time = self._rate_limit_reset_time - time.time()
                    if wait_time > 0:
                        print(
                            f"[RATE_LIMIT] Approaching limit. Waiting for {wait_time:.2f} seconds..."
                        )
                        # Release the lock before sleeping to not block other threads
                        # that might just want to read the state.
                        # In this simple case, it's fine to hold, but this is better practice.
                        time.sleep(wait_time + 0.1)  # Add a small buffer

            try:
                res = self.session.get(url, params=params, headers=headers, timeout=30)

                # --- Update rate limit state from headers after every call ---
                with self._rate_limit_lock:
                    limit_header_str = res.headers.get("X-RateLimit-Limit")
                    if limit_header_str is not None:
                        self._rate_limit_total = int(limit_header_str)

                    remaining_header_str = res.headers.get("X-RateLimit-Remaining")
                    if remaining_header_str is not None:
                        self._rate_limit_remaining = int(remaining_header_str)

                    reset_header_str = res.headers.get("X-RateLimit-Reset")
                    if reset_header_str is not None:
                        self._rate_limit_reset_time = float(reset_header_str)

                    remaining_display = (
                        self._rate_limit_remaining
                        if self._rate_limit_remaining is not None
                        else "N/A"
                    )
                    total_display = (
                        self._rate_limit_total
                        if self._rate_limit_total is not None
                        else "N/A"
                    )
                    print(
                        f"[API_CALL] {res.status_code} {res.request.path_url} | Rate Limit: {remaining_display}/{total_display}"
                    )

                # --- Reactive Check ---
                if res.status_code == 429:
                    retry_after = int(res.headers.get("Retry-After", "5"))
                    print(
                        f"[RATE_LIMIT] Hit 429. Obeying 'Retry-After' header. Waiting {retry_after} seconds."
                    )
                    time.sleep(retry_after)
                    continue  # Retry the request

                res.raise_for_status()  # Raise HTTPError for other bad responses (4xx or 5xx)
                return res

            except Exception as e:
                print(f"An unexpected error occurred for URL {url}: {e}")
                return None

    def _fetch_discos_data(
        self, endpoint: str, params: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generic helper to fetch data from a DISCOS endpoint with caching.
        Now uses the internal rate-limited fetcher.
        """

        param_items = sorted(params.items()) if params else []
        query_identifier = "_".join([f"{k}-{v}" for k, v in param_items])
        sanitized_identifier = re.sub(r"[^\w-]", "_", query_identifier)
        filePrefix = f"DISCOS_{endpoint.replace('/', '_')}_{sanitized_identifier}_"

        cached_file = isCacheAvaliable(filePrefix, timedelta(weeks=2), settings)
        if cached_file:
            # print(f"Using cached DISCOS file: {cached_file}")
            with open(cached_file, "r", encoding="utf-8") as f:
                return json.load(f)

        url = f"{self.settings.DISCOS_BASE_URL}{endpoint}"
        print(f"Fetching fresh data from DISCOS: {url} with params: {params}")

        # This now calls our new rate-limited method instead of the old one
        response = self._fetch_with_rate_limit_handling(url=url, params=params)

        if response is None:
            print(f"Fetching data from {url} failed after handling retries.")
            return None

        saveFile(
            settings=self.settings,
            filePrefix=filePrefix,
            content=response.content,
            fileExtension=".json",
        )
        return response.json()

    def get_objects_page(
        self,
        page_number: int,
        page_size: int,
        filter_str: Optional[str] = None,
    ) -> Optional[DiscosObjectListResponse]:
        """
        Retrieve a single page of DISCOS objects.
        """
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be in the range 1-100")

        params = {"page[size]": str(page_size), "page[number]": str(page_number)}
        if filter_str:
            params["filter"] = filter_str

        return cast(
            Optional[DiscosObjectListResponse],
            self._fetch_discos_data("/api/objects", params),
        )

    def get_all_objects(
        self,
        page_size: int = 100,
        only_active: bool = True,
        max_workers: int = 10,
    ) -> Optional[DiscosObjectList]:
        """
        Retrieve every DISCOS object, transparently paging through the API
        using multiple threads with integrated rate-limit handling and a
        single-line progress indicator.
        """
        filter_query = "active=true" if only_active else None

        # print("Fetching page 1 to determine total work...")
        first_page_data = self.get_objects_page(
            page_number=1, page_size=page_size, filter_str=filter_query
        )

        if (
            not first_page_data
            or "data" not in first_page_data
            or "meta" not in first_page_data
        ):
            print("Initial request failed or was malformed. Aborting.")
            return None

        total_pages = first_page_data["meta"]["pagination"]["totalPages"]
        print(f"\tTotal pages to fetch: {total_pages}")

        if total_pages <= 1:
            return first_page_data["data"]

        # --- Start of changes for progress tracking ---
        all_objects: DiscosObjectList = first_page_data["data"]
        pages_to_fetch = range(2, total_pages + 1)
        completed_count = 1  # We've already completed page 1
        progress_lock = threading.Lock()

        def print_progress():
            # This function formats and prints the progress bar
            progress = completed_count / total_pages
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = "█" * filled_length + "-" * (bar_length - filled_length)
            percent = f"{progress:.1%}"
            # Use \r to return to the start of the line, and flush to ensure
            # it's written to the console immediately.
            sys.stdout.write(
                f"\rFetching pages: |{bar}| {completed_count}/{total_pages} ({percent}) "
            )
            sys.stdout.flush()

        print_progress()  # Initial progress display

        worker_func = lambda p: self.get_objects_page(
            page_number=p, page_size=page_size, filter_str=filter_query
        )

        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Use executor.submit and as_completed for real-time progress
                futures = {executor.submit(worker_func, p): p for p in pages_to_fetch}

                for future in as_completed(futures):
                    page_num = futures[future]
                    try:
                        page_data = future.result()
                        if page_data and "data" in page_data:
                            all_objects.extend(page_data["data"])
                        else:
                            # Log specific page failures without breaking progress
                            print(
                                f"\nWarning: Failed to retrieve or parse data for page {page_num}."
                            )
                    except Exception as e:
                        print(f"\nAn error occurred fetching page {page_num}: {e}")

                    # --- Thread-safe progress update ---
                    with progress_lock:
                        completed_count += 1
                        print_progress()

        except Exception as e:
            print(f"\nAn error occurred during threaded execution: {e}")
            return None

        # Print a newline to move off the progress bar line
        print("\nAll pages fetched. Aggregating results...")
        print(f"Successfully aggregated {len(all_objects)} total objects.")
        return all_objects
