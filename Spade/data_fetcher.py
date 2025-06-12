from copy import deepcopy
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import requests
from requests import Session, Response
from requests.exceptions import HTTPError
import os
from dotenv import load_dotenv
from os.path import join, isfile
from Spade.types import DiscosObjectList, DiscosObjectListResponse
from pathlib import Path

from Spade.config import Settings

"""
This file contains functions that will download files from different sources like spaceTracker
"""


def downloadedFileList(path: str) -> List[str]:
    """
    Returns a list of all filenames in the path variable.
    """
    if not os.path.isdir(path):
        return []
    onlyfiles = [f for f in os.listdir(path) if isfile(join(path, f))]
    return onlyfiles


def isCacheAvaliable(
    fileprefix: str, max_cache_age: timedelta, settings: Settings
) -> Optional[str]:
    """
    Checks if a cached file exists that is newer than the maximum allowed age.

    It finds the *most recent* file matching the prefix and checks if its age
    is less than max_cache_age.

    Args:
        fileprefix (str): The prefix of the file to look for.
        max_cache_age (timedelta): The maximum duration a file can be considered
                                   "fresh". For example, timedelta(hours=2) or
                                   timedelta(days=1).

    Returns:
        Optional[str]: The full path to the newest valid cache file, or None
                       if no file is found within the specified age limit.
    """
    cutoff_time = datetime.now() - max_cache_age

    most_recent_file: Optional[str] = None
    most_recent_time = cutoff_time

    for filename in downloadedFileList(settings.DOWNLOADED_DATA_PATH):
        if filename.startswith(fileprefix):
            try:
                base_name = os.path.splitext(filename)[0]
                timestamp_str = base_name[len(fileprefix) :]
                file_datetime = datetime.strptime(timestamp_str, settings.DATE_FORMAT)

                if file_datetime > most_recent_time:
                    most_recent_time = file_datetime
                    most_recent_file = filename

            except (ValueError, IndexError):
                print(f"Could not parse date from filename: {filename}")
                continue

    if most_recent_file:
        return join(settings.DOWNLOADED_DATA_PATH, most_recent_file)

    return None


def get_auth_space_tracker(session: Session, settings: Settings) -> bool:
    """
    Requests auth cookies from space tracker
    Args:
        session (Session): A requests session that you want to be logged in
        username (str): The username you want to login with
        password (str): The password you want to login with
    """
    try:
        res = session.post(
            settings.SPACE_TRACKER_AUTH_URL,
            data={
                "identity": settings.SPACE_TRACKER_USERNAME,
                "password": settings.SPACE_TRACKER_PASSWORD,
            },
        )
        res.raise_for_status()
        return True
    except HTTPError as e:
        status_code = e.response.status_code
        print("Space Tracker Auth was not succesful")
        print("HTTP Status Code: ", status_code)
        print(e.response.text)
        return False


def fetch_api(session: Session, url: str, params=None, headers=None) -> Response | None:
    """
    Makes `GET` request to  with provded URL. Make sure session is logged in before calling this function or headers have token included.
    Args:
        session (Session): A requests session that is already logged in
        url (str): The Url you wish to make a request to
    Returns:
        Response (Response | None):
            - A `requests.Response` object containing the Space-Track full catalog
              data if the request is successful (HTTP status 200).
            - `None` if an `HTTPError` occurs during the request, indicating a
              problem with the API call or authentication.
    """

    try:
        res = session.get(url, params=params, headers=headers)
        res.raise_for_status()
        return res

    except HTTPError as e:
        status_code = e.response.status_code
        print(f"There was a problem making request to the url: {url}")
        print("HTTP Status Code: ", status_code)
        print(e.response.text)
        return None
    except Exception as e:
        print(f"There was a unkown problem making request to the url: {url}")
        print(f"The expection was: {e}")
        return None


def fetch_DISCOS(url: str, settings: Settings, params=None) -> Response | None:
    headers = {
        "Authorization": f"Bearer {settings.DISCOS_TOKEN}",
        "DiscosWeb-Api-Version": "2",
    }

    session = Session()
    return fetch_api(session=session, url=url, params=params, headers=headers)


def fetch_object_list_DISCOS(
    settings: Settings, params: Dict[str, str]
) -> DiscosObjectListResponse | None:
    """
    Retrieve a list of DISCOS objects.

    Args:
        settings (Settings): A settings object required to make api calls
        params (Params): A Dictonary for requesting page size and page numbers
    Returns
    -------
    DiscosObjectList | None
        - A fully-typed list of DISCOS objects when the request succeeds.
        - None if the request fails.
    """
    url = settings.DISCOS_BASE_URL + "/api/objects"
    res = fetch_DISCOS(url, settings, params)
    if res is None:
        print("There was an Error fetching object list from DISCOS")
        return None

    objectList = res.json()
    return objectList


def fetch_all_objects_DISCOS(
    settings: Settings,
    page_size: int = 100,
) -> DiscosObjectList | None:
    """
    Retrieve every DISCOS object, transparently paging through the API.

    Parameters
    ----------
    settings : Settings
        Your application settings with DISCOS credentials.
    page_size : int, default 100
        The number of records to request per page (max supported by API).

    Returns
    -------
    DiscosObjectList | None
        A list containing all objects, or None upon request failure.
    """
    if page_size < 1 or page_size > 100:
        raise ValueError("page_size must be in the range 1-100")

    all_objects: DiscosObjectList = []

    page_number: int = 1
    total_pages: int | None = None
    print("Fetching all objects DISCOS")
    while total_pages is None or total_pages >= page_number:
        print(f"\tOn page {page_number}/{'?' if total_pages is None else total_pages}")
        page_params = {
            "page[size]": str(page_size),
            "page[number]": str(page_number),
            # "filter": "ne(objectClass,Unknown)",
        }

        page_data = fetch_object_list_DISCOS(settings, page_params)
        if page_data is None or page_data["data"] is None or page_data["meta"] is None:
            print(f"response was not formatted properly: {page_data}")
            return None

        total_pages = page_data["meta"]["pagination"]["totalPages"]
        print(f"\tTotal Pages is {total_pages}")
        if total_pages is None:
            print("Could not extract total pages")
            return None

        all_objects.extend(page_data["data"])
        print(f"\tAfter page {page_number}, {len(all_objects)} number of objects")

        page_number += 1

    return all_objects


def save_discos_objects(
    settings: Settings,
    page_size: int = 100,
) -> str | None:
    """
    Fetch every DISCOS object and write the result to disk as JSON.

    Parameters
    ----------
    settings : Settings
        Your application settings with DISCOS credentials.
    file_path : str | Path, default "discos_objects.json"
        Where to save the JSON file.
    params : Optional[Dict[str, str]]
        Extra query parameters forwarded to the API.
    page_size : int, default 100
        Page size to use while downloading the objects.

    Returns
    -------
    str | None
        The resolved file path on success as string, or None if the fetch fails.
    """
    filePrefix = "DISCOS_ALL_"

    data = fetch_all_objects_DISCOS(
        settings=settings,
        page_size=page_size,
    )

    if data is None:
        print("Saving aborted: could not download DISCOS objects.")
        return None

    try:
        datestr = datetime.now().strftime(settings.DATE_FORMAT)
        newFileName = settings.DOWNLOADED_DATA_PATH + filePrefix + datestr + ".json"
        with open(newFileName, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(data)} objects to {newFileName}")
        return newFileName
    except Exception as e:
        print(f"Error writing full catlog to a file, error: {e}")


def fetch_full_catlog_ST(settings: Settings) -> str | None:
    """
    Makes request to space tracker to download OMM (XML) file. Places file into downloaded_data folder for later use
    Returns:
        string (str | None):
                - A `str` containing the file path of the newly created data
                - `None` if there was a errror fetching the catlog
    """
    filePrefix = "FULL_CATLOG_"

    # First check if we can used cached file
    avaliableFile = isCacheAvaliable(filePrefix, timedelta(hours=2), settings)
    if avaliableFile:
        return avaliableFile

    session = Session()

    if (
        settings.SPACE_TRACKER_USERNAME is None
        or settings.SPACE_TRACKER_PASSWORD is None
    ):
        print("Error with grabbing username and password from env file")
        return None

    loginSuccess = get_auth_space_tracker(session, settings)
    if not loginSuccess:
        print("Error logging in, not fetching catlog")
        return None
    response = fetch_api(session, settings.SPACE_TRACKER_FULL_CATLOG)
    if response is None:
        print("Fetching Full Space Tracker Catlog failed")
        return None
    try:
        datestr = datetime.now().strftime(settings.DATE_FORMAT)
        newFileName = settings.DOWNLOADED_DATA_PATH + filePrefix + datestr + ".XML"
        with open(newFileName, "wb") as f:
            f.write(response.content)
        return newFileName
    except Exception as e:
        print(f"Error writing full catlog to a file, error: {e}")
