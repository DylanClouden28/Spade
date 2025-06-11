from datetime import datetime, timedelta
from typing import List, Optional
import requests
from requests import Session, Response
from requests.exceptions import HTTPError
import os
from dotenv import load_dotenv
from os.path import join, isfile

"""
This file contains functions that will download files from different sources like spaceTracker
"""
# URLS
SPACE_TRACKER_AUTH_URL = "https://www.space-track.org/ajaxauth/login"
SPACE_TRACKER_FULL_CATLOG = "https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/xml"

# Grabs user and pass from .env file
load_dotenv()
SPACE_TRACKER_USERNAME = os.getenv("SPACE_TRACKER_USERNAME")
SPACE_TRACKER_PASSWORD = os.getenv("SPACE_TRACKER_PASSWORD")

# Path to folder with downloaded data
dirname = os.path.dirname(__file__)
DOWNLOADED_DATA_PATH = os.path.join(dirname, "downloaded_data/")
DATE_FORMAT = "%Y_%m_%d-%I_%M_%S_%p"


def downloadedFileList(path: str) -> List[str]:
    """
    Returns a list of all filenames in the path variable.
    """
    if not os.path.isdir(path):
        return []
    onlyfiles = [f for f in os.listdir(path) if isfile(join(path, f))]
    return onlyfiles


def isCacheAvaliable(fileprefix: str, max_cache_age: timedelta) -> Optional[str]:
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

    for filename in downloadedFileList(DOWNLOADED_DATA_PATH):
        if filename.startswith(fileprefix):
            try:
                base_name = os.path.splitext(filename)[0]
                timestamp_str = base_name[len(fileprefix) :]
                file_datetime = datetime.strptime(timestamp_str, DATE_FORMAT)

                if file_datetime > most_recent_time:
                    most_recent_time = file_datetime
                    most_recent_file = filename

            except (ValueError, IndexError):
                print(f"Could not parse date from filename: {filename}")
                continue

    if most_recent_file:
        return join(DOWNLOADED_DATA_PATH, most_recent_file)

    return None


def get_auth_space_tracker(session: Session, username: str, password: str):
    """
    Requests auth cookies from space tracker
    Args:
        session (Session): A requests session that you want to be logged in
        username (str): The username you want to login with
        password (str): The password you want to login with
    """
    try:
        session.post(
            SPACE_TRACKER_AUTH_URL,
            data={
                "identity": username,
                "password": password,
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
    filePrefix = "FULL_CATLOG_"

    # First check if we can used cached file
    avaliableFile = isCacheAvaliable(filePrefix, timedelta(hours=2))
    if avaliableFile:
        return avaliableFile

    session = Session()

    if SPACE_TRACKER_USERNAME is None or SPACE_TRACKER_PASSWORD is None:
        print("Error with grabbing username and password from env file")
        return None

    get_auth_space_tracker(session, SPACE_TRACKER_USERNAME, SPACE_TRACKER_PASSWORD)
    response = fetch_api(session, SPACE_TRACKER_FULL_CATLOG)
    if response is None:
        print("Fetching Full Space Tracker Catlog failed")
        return None
    try:
        datestr = datetime.now().strftime(DATE_FORMAT)
        newFileName = DOWNLOADED_DATA_PATH + filePrefix + datestr + ".XML"
        with open(newFileName, "wb") as f:
            f.write(response.content)
        return newFileName
    except Exception as e:
        print(f"Error writing full catlog to a file, error: {e}")
