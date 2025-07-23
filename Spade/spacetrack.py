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

from typing import Any, List, Optional, TypeVar, TypedDict, cast

from Spade.spade_types import (
    AnnouncementDataList,
    BoxscoreDataList,
    CdmPublicDataList,
    DecayDataList,
    GpDataList,
    GpHistoryDataList,
    LaunchSiteDataList,
    SatcatChangeDataList,
    SatcatDataList,
    SatcatDebutDataList,
    TipDataList,
)

T = TypeVar("T")


class SpaceTrackClient:
    """
    A client for interacting with the Space-Track.org API.

    This client is designed to be used as a context manager to handle
    authentication and session lifecycle automatically.

    It a wrapper around public spaceTrack Data defined here
    https://www.space-track.org/documentation#/api

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

    def _fetch_spacetrack_data(
        self, endpoint_class: str, **kwargs: str
    ) -> Optional[List[T]]:
        """
        A generic helper to fetch data from a Space-Track endpoint.

        This method is generic over the return type `T`.

        Args:
            endpoint_class (str): The name of the query class (e.g., 'gp').
            **kwargs (str): Filters for the Space-Track API.

        Returns:
            Optional[List[T]]: A list of data objects of type T, or None.
        """
        if not self.session:
            raise RuntimeError(
                "Session not available. Use this client within a 'with' statement."
            )

        sorted_items = sorted(kwargs.items())
        query_identifier = "_".join([f"{k}-{v}" for k, v in sorted_items])
        sanitized_identifier = re.sub(r"[^\w-]", "_", query_identifier)
        filePrefix = f"{endpoint_class.upper()}_{sanitized_identifier}_"

        cached_file = isCacheAvaliable(filePrefix, timedelta(hours=2), self.settings)
        if cached_file:
            print(f"Using cached {endpoint_class} file: {cached_file}")
            with open(cached_file, "r", encoding="utf-8") as f:
                # Cast the loaded JSON to the expected generic list type
                return cast(List[T], json.load(f))

        filters: dict[str, str] = {"format": "json"}
        filters.update(kwargs)
        path_segments = [
            item for pair in filters.items() for item in (pair[0], str(pair[1]))
        ]
        url = f"{self.settings.SPACE_TRACKER_BASE_URL}/{endpoint_class}/{'/'.join(path_segments)}"

        print(f"Fetching fresh {endpoint_class} data from Space-Track: {url}")
        response = fetch_api(self.session, url=url)

        if response is None:
            print(f"Fetching {endpoint_class} data from Space-Track failed.")
            return None

        saveFile(
            settings=self.settings,
            filePrefix=filePrefix,
            content=response.content,
            fileExtension=".json",
        )

        # Cast the response JSON to the expected generic list type

        return cast(List[T], response.json())

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
        return self._fetch_spacetrack_data(endpoint_class="gp", **kwargs)

    def satcat_debut(self, **kwargs: str) -> Optional[SatcatDebutDataList]:
        """
        Fetches new satellite catalog records from Space-Track.org.

        This method retrieves data from the 'satcat_debut' class. It uses a
        2-hour cache to avoid excessive API calls. The cache filename is
        generated based on the query parameters.

        All query parameters must be provided as keyword arguments. These
        arguments are passed directly to the Space-Track API. Refer to the
        Space-Track API documentation for a full list of available filters
        for the 'satcat_debut' class.

        Args:
            **kwargs (str): Filters for the Space-Track API. Keys should
                            match the API documentation (e.g., 'DEBUT').
                            Example: `satcat_debut(DEBUT='>now-7')`

        Returns:
            Optional[SatcatDebutDataList]: A list of satcat debut objects with
                                           accurate types, or None if an error
                                           occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="satcat_debut", **kwargs)

    def announcement(self, **kwargs: str) -> Optional[AnnouncementDataList]:
        """
        Fetches current announcements from Space-Track.org.

        This method retrieves data from the 'announcement' class. It uses a
        2-hour cache.

        Args:
            **kwargs (str): Filters for the Space-Track API.
                            Example: `announcement(announcement_type='GENERAL')`

        Returns:
            Optional[AnnouncementDataList]: A list of announcement objects,
                                            or None if an error occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="announcement", **kwargs)

    def boxscore(self, **kwargs: str) -> Optional[BoxscoreDataList]:
        """
        Fetches the boxscore of man-made objects in orbit, grouped by country.

        This method retrieves data from the 'boxscore' class. It uses a
        2-hour cache.

        Args:
            **kwargs (str): Filters for the Space-Track API.
                            Example: `boxscore(COUNTRY='US')`

        Returns:
            Optional[BoxscoreDataList]: A list of boxscore objects,
                                        or None if an error occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="boxscore", **kwargs)

    def cdm_public(self, **kwargs: str) -> Optional[CdmPublicDataList]:
        """
        Fetches publicly available Conjunction Data Messages (CDM).

        This method retrieves data from the 'cdm_public' class. It uses a
        2-hour cache.

        Args:
            **kwargs (str): Filters for the Space-Track API.
                            Example: `cdm_public(CREATED='>now-24hours')`

        Returns:
            Optional[CdmPublicDataList]: A list of CDM objects,
                                         or None if an error occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="cdm_public", **kwargs)

    def decay(self, **kwargs: str) -> Optional[DecayDataList]:
        """
        Fetches predicted and historical decay information for objects.

        This method retrieves data from the 'decay' class. It uses a
        2-hour cache.

        Args:
            **kwargs (str): Filters for the Space-Track API.
                            Example: `decay(NORAD_CAT_ID='48274', PRECEDENCE='1')`

        Returns:
            Optional[DecayDataList]: A list of decay records,
                                     or None if an error occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="decay", **kwargs)

    def gp_history(self, **kwargs: str) -> Optional[GpHistoryDataList]:
        """
        Fetches ALL historical SGP4 keplerian element sets.

        NOTE: Access to this archival data is significantly slower.
        This method retrieves data from the 'gp_history' class. It uses a
        2-hour cache.

        Args:
            **kwargs (str): Filters for the Space-Track API.
                            Example: `gp_history(NORAD_CAT_ID='25544')`

        Returns:
            Optional[GpHistoryDataList]: A list of historical GP data objects,
                                         or None if an error occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="gp_history", **kwargs)

    def launch_site(self, **kwargs: str) -> Optional[LaunchSiteDataList]:
        """
        Fetches a list of launch sites found in satellite catalog records.

        This method retrieves data from the 'launch_site' class. It uses a
        2-hour cache.

        Args:
            **kwargs (str): Filters for the Space-Track API.
                            Example: `launch_site(SITE_CODE='KSC')`

        Returns:
            Optional[LaunchSiteDataList]: A list of launch site objects,
                                          or None if an error occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="launch_site", **kwargs)

    def satcat(self, **kwargs: str) -> Optional[SatcatDataList]:
        """
        Fetches Satellite Catalog Information.

        The "CURRENT" predicate indicates the most current catalog record
        with a 'Y'. All older records for that object will have an 'N'.
        This method retrieves data from the 'satcat' class. It uses a
        2-hour cache.

        Args:
            **kwargs (str): Filters for the Space-Track API.
                            Example: `satcat(CURRENT='Y', COUNTRY='US')`

        Returns:
            Optional[SatcatDataList]: A list of satcat objects,
                                      or None if an error occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="satcat", **kwargs)

    def satcat_change(self, **kwargs: str) -> Optional[SatcatChangeDataList]:
        """
        Fetches history showing changes for objects in the satellite catalog.

        Includes changes in INTLDES, NORAD_CAT_ID, SATNAME, COUNTRY, LAUNCH, or DECAY.
        This method retrieves data from the 'satcat_change' class. It uses a
        2-hour cache.

        Args:
            **kwargs (str): Filters for the Space-Track API.
                            Example: `satcat_change(NORAD_CAT_ID='25544',
                                                   CHANGE_MADE='>now-60days')`

        Returns:
            Optional[SatcatChangeDataList]: A list of satcat change records,
                                            or None if an error occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="satcat_change", **kwargs)

    def tip(self, **kwargs: str) -> Optional[TipDataList]:
        """
        Fetches Tracking and Impact Prediction (TIP) Messages.

        This method retrieves data from the 'tip' class. It uses a
        2-hour cache.

        Args:
            **kwargs (str): Filters for the Space-Track API.
                            Example: `tip(NORAD_CAT_ID='48274')`

        Returns:
            Optional[TipDataList]: A list of TIP messages,
                                   or None if an error occurs.
        """
        return self._fetch_spacetrack_data(endpoint_class="tip", **kwargs)
