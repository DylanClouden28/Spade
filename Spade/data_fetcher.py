from datetime import datetime, timedelta
from typing import List, Optional
import requests
from requests import Session, Response
from requests.exceptions import HTTPError
import os
from dotenv import load_dotenv
from os.path import join, isfile

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
        res.raise_for_status()
        return res

    except HTTPError as e:
        status_code = e.response.status_code
        print(f"There was a problem making request to the url: {url}")
        print("HTTP Status Code: ", status_code)
        print(e.response.text)
        return None
    except:
        print(f"There was a problem making request to the url: {url}")
        return None


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
