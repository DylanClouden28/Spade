import json
from datetime import timedelta
from requests import Session

from Universal_Database.Spade.config import Settings
from Universal_Database.Spade.data_fetcher import (
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
                OBJECT_TYPE="payload"
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

    def gp(self, **kwargs) -> Optional[GpDataList]:
        """
        Fetches the newest general perturbation (GP) element sets.

        This method retrieves data from the 'gp' class on Space-Track.org.
        It uses a 2-hour cache to avoid excessive API calls. The data is
        returned as a typed list of dictionaries.

        The default query is for all non-decayed objects, updated within the
        last 30 days, and sorted by NORAD_CAT_ID and EPOCH to get the
        latest record for each object.

        Args:
            **kwargs: Override or add filters for the Space-Track API.
                      Keys should match the API documentation (e.g., 'COUNTRY_CODE').
                      Example: `gp(COUNTRY_CODE='US', RCS_SIZE='LARGE')`

        Returns:
            Optional[GpDataList]: A list of GP data objects with accurate
                                  types, or None if an error occurs.
        """
        if not self.session:
            raise RuntimeError(
                "Session not available. Use this client within a 'with' statement."
            )

        filePrefix = "GP_ALL_"
        cached_file = isCacheAvaliable(filePrefix, timedelta(hours=2), self.settings)
        if cached_file:
            print(f"Using cached GP file: {cached_file}")
            with open(cached_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # --- CORRECTED DEFAULT FILTERS ---
        # These now match the recommended best-practice query.
        filters = {
            "DECAY_DATE": "null-val",
            "EPOCH": ">now-30",
            "orderby": "NORAD_CAT_ID,EPOCH",
            "format": "json",
        }
        # User-provided kwargs will override the defaults
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
