from datetime import datetime
import requests
from requests import Session, Response
from requests.exceptions import HTTPError
import os

"""
This file contains functions that will download files from different sources like spaceTracker
"""
# URLS
SPACE_TRACKER_AUTH_URL = "https://www.space-track.org/auth/login"
SPACE_TRACKER_FULL_CATLOG = "https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/xml"

# Grabs user and pass from .env file
SPACE_TRACKER_USERNAME = os.environ["SPACE_TRACKER_USERNAME"]
SPACE_TRACKER_PASSWORD = os.environ["SPACE_TRACKER_PASSWORD"]

# Path to folder with downloaded data
dirname = os.path.dirname(__file__)
DOWNLOADED_DATA = os.path.join(dirname, "downloaded_data/")


def get_auth_space_tracker(session: Session):
    """
    Requests auth cookies from space tracker
    Args:
        session (Session): A requests session that you want to be logged in
    """
    try:
        session.post(
            SPACE_TRACKER_AUTH_URL,
            data={
                "identity": SPACE_TRACKER_USERNAME,
                "password": SPACE_TRACKER_PASSWORD,
            },
        )

    except HTTPError as e:
        status_code = e.response.status_code
        print("Space Tracker Auth was not succesful")
        print("HTTP Status Code: ", status_code)
        print(e.response.text)


def fetch_api(session: Session, url: str) -> Response | None:
    """
    Makes `GET` request to  with provded URL. Make sure session is logged in before calling this function.
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
        res = session.get(
            url,
        )
        return res

    except HTTPError as e:
        status_code = e.response.status_code
        print(f"There was a problem making request to the url: {url}")
        print("HTTP Status Code: ", status_code)
        print(e.response.text)
        return None


def fetch_full_catlog_ST() -> str | None:
    """
    Makes request to space tracker to download OMM (XML) file. Places file into downloaded_data folder for later use
    Returns:
        string (str | None):
                - A `str` containing the file path of the newly created data
                - `None` if there was a errror fetching the catlog
    """
    session = Session()

    get_auth_space_tracker(session)
    response = fetch_api(session, SPACE_TRACKER_FULL_CATLOG)
    if response is None:
        print("Fetching Full Space Tracker Catlog failed")
        return None
    try:
        datestr = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        newFileName = DOWNLOADED_DATA + "FULL_CATLOG_" + datestr
        with open(newFileName, "wb") as f:
            f.write(response.content)
        return newFileName
    except Exception as e:
        print(f"Error writing full catlog to a file, error: {e}")
