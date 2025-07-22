import json
from datetime import timedelta
import re
from requests import Session

from Spade.config import Settings
from Spade.data_fetcher import (
    fetch_api,
    get_auth_space_tracker,
    isCacheAvaliable,
    saveFile,
)

from typing import List, Optional, TypedDict


class GpData(TypedDict):
    """
    Represents a single General Perturbation (GP) data object from
    Space-Track.org, in OMM JSON format. The types are derived from the
    official Space-Track database schema.
    "https://www.space-track.org/basicspacedata/modeldef/class/gp/format/html"
    """

    CCSDS_OMM_VERS: str
    COMMENT: str
    CREATION_DATE: Optional[str]
    ORIGINATOR: str
    OBJECT_NAME: Optional[str]
    OBJECT_ID: Optional[str]
    CENTER_NAME: str
    REF_FRAME: str
    TIME_SYSTEM: str
    MEAN_ELEMENT_THEORY: str
    EPOCH: Optional[str]
    MEAN_MOTION: Optional[float]
    ECCENTRICITY: Optional[float]
    INCLINATION: Optional[float]
    RA_OF_ASC_NODE: Optional[float]
    ARG_OF_PERICENTER: Optional[float]
    MEAN_ANOMALY: Optional[float]
    EPHEMERIS_TYPE: Optional[int]
    CLASSIFICATION_TYPE: Optional[str]
    NORAD_CAT_ID: int
    ELEMENT_SET_NO: Optional[int]
    REV_AT_EPOCH: Optional[int]
    BSTAR: Optional[float]
    MEAN_MOTION_DOT: Optional[float]
    MEAN_MOTION_DDOT: Optional[float]
    SEMIMAJOR_AXIS: Optional[float]
    PERIOD: Optional[float]
    APOAPSIS: Optional[float]
    PERIAPSIS: Optional[float]
    OBJECT_TYPE: Optional[str]
    RCS_SIZE: Optional[str]
    COUNTRY_CODE: Optional[str]
    LAUNCH_DATE: Optional[str]
    SITE: Optional[str]
    DECAY_DATE: Optional[str]
    FILE: Optional[int]
    GP_ID: int
    TLE_LINE0: Optional[str]
    TLE_LINE1: Optional[str]
    TLE_LINE2: Optional[str]


# Type alias for a list of GP data objects
GpDataList = List[GpData]


class SpaceTrackClient:
    """
    A client for interacting with the Space-Track.org API.

    This client is designed to be used as a context manager to handle
    authentication and session lifecycle automatically.

    Example:
        from Spade.config import settings

        with SpaceTrackClient(settings) as st_client:
            # Fetch all active payloads from the US
            us_payloads = st_client.gp(
                COUNTRY_CODE="US",
                OBJECT_TYPE="payload",
                DECAY_DATE="null-val"
            )
            if us_payloads:
                print(f"Found {len(us_payloads)} active US payloads.")
    """

    def __init__(self, settings: Settings):
        """
        Initializes the SpaceTrackClient.

        Args:
            settings (Settings): The application settings object containing
                                 credentials and configuration.
        """
        self.settings = settings
        self.session: Optional[Session] = None

    def __enter__(self):
        """
        Enters the context manager, creating and authenticating a session.
        """
        self.session = Session()
        if not get_auth_space_tracker(self.session, self.settings):
            raise ConnectionError("Failed to authenticate with Space-Track.org")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the context manager, closing the session.
        """
        if self.session:
            self.session.close()

    def gp(self, **kwargs: str) -> Optional[GpDataList]:
        """
        Fetches general perturbation (GP) element sets from Space-Track.org.

        This method retrieves data from the 'gp' class. It uses a 2-hour
        cache to avoid excessive API calls. The cache filename is generated
        based on the query parameters, ensuring that different queries are
        cached separately.

        All query parameters must be provided as keyword arguments. These
        arguments are passed directly to the Space-Track API. Refer to the
        Space-Track API documentation for a full list of available filters
        for the 'gp' class.

        Args:
            **kwargs (str): Filters for the Space-Track API. Keys should
                            match the API documentation (e.g., 'COUNTRY_CODE').
                            Example: `gp(DECAY_DATE='null-val', EPOCH='>now-30')`

        Returns:
            Optional[GpDataList]: A list of GP data objects with accurate
                                  types, or None if an error occurs.
        """
        if not self.session:
            raise RuntimeError(
                "Session not available. Use this client within a 'with' statement."
            )

        # --- Create a dynamic cache key from kwargs ---
        # Sort kwargs by key to ensure consistent filenames
        sorted_items = sorted(kwargs.items())
        # Create a string representation, e.g., "COUNTRY_CODE-US_OBJECT_TYPE-PAYLOAD"
        query_identifier = "_".join([f"{k}-{v}" for k, v in sorted_items])

        # Sanitize the string to be a valid filename component.
        # Replace any character that is not a word character (a-z, A-Z, 0-9, _)
        # or a hyphen with an underscore.
        sanitized_identifier = re.sub(r"[^\w-]", "_", query_identifier)

        # Combine the base prefix with the sanitized identifier.
        filePrefix = f"GP_{sanitized_identifier}_"

        cached_file = isCacheAvaliable(filePrefix, timedelta(hours=2), self.settings)
        if cached_file:
            print(f"Using cached GP file: {cached_file}")
            with open(cached_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # Start with the mandatory format, then add user-provided filters.
        filters: dict[str, str] = {"format": "json"}
        filters.update(kwargs)

        path_segments = []
        for key, value in filters.items():
            path_segments.extend([key, str(value)])

        url = f"{self.settings.SPACE_TRACKER_GP_URL}/{'/'.join(path_segments)}"

        print(f"Fetching fresh GP data from Space-Track: {url}")
        response = fetch_api(self.session, url=url)

        if response is None:
            print("Fetching GP data from Space-Track failed.")
            return None

        saveFile(
            settings=self.settings,
            filePrefix=filePrefix,
            content=response.content,
            fileExtension=".json",
        )

        return response.json()
