import os

# Settings will load env variables from .env file and you can import this class to use anywhere


class Settings:
    """
    Central object for all settings. Loads values from env file
    """

    def __init__(self):

        # URLS
        self.SPACE_TRACKER_AUTH_URL = "https://www.space-track.org/ajaxauth/login"
        self.SPACE_TRACKER_FULL_CATLOG = "https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/xml"

        # Path to folder with downloaded data
        dirname = os.path.dirname(__file__)
        self.DOWNLOADED_DATA_PATH = os.path.join(dirname, "downloaded_data/")
        self.DATE_FORMAT = "%Y_%m_%d-%I_%M_%S_%p"

        # From .env file
        self.SPACE_TRACKER_USERNAME: str = self._get_required_env(
            "SPACE_TRACKER_USERNAME"
        )
        self.SPACE_TRACKER_PASSWORD: str = self._get_required_env(
            "SPACE_TRACKER_PASSWORD"
        )

    def _get_required_env(self, var_name: str) -> str:
        value = os.environ.get(var_name)
        if value is None:
            raise ValueError(f"Missing required environment variable: {var_name}")
        return value


settings = Settings()  # Import settings object
