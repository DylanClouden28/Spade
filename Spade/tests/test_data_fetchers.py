from datetime import timedelta
import unittest
from unittest.mock import MagicMock
from Spade.data_fetcher import (
    get_auth_space_tracker,
    isCacheAvaliable,
    fetch_api,
    fetch_full_catlog_ST,
)
from requests import Session
from Spade.config import settings
import os


class TestGetAuthSpaceTracker(unittest.TestCase):

    def test_bad_login_fails_smoothly(self):
        mock_settings = MagicMock()
        mock_settings.SPACE_TRACKER_AUTH_URL = (
            "https://www.space-track.org/ajaxauth/login"
        )
        mock_settings.SPACE_TRACKER_USERNAME = "badusername"
        mock_settings.SPACE_TRACKER_PASSWORD = "badpassword"
        session = Session()
        loginSuccess = get_auth_space_tracker(session, mock_settings)
        self.assertFalse(loginSuccess)

    def test_correct_login(self):
        session = Session()
        loginSuccess = get_auth_space_tracker(session, settings)
        self.assertTrue(loginSuccess)


class TestisCacheAvaliable(unittest.TestCase):

    def test_bad_fileprefix_returns_None(self):
        result = isCacheAvaliable("asdfasdfsf", timedelta(days=2), settings)
        self.assertIsNone(result)

    def test_finds_single_file(self):
        mock_settings = MagicMock()
        dirname = os.path.dirname(__file__)
        mock_settings.DOWNLOADED_DATA_PATH = os.path.join(
            dirname, "testFiles/test_Downloaded_Data_Cache"
        )
        mock_settings.DATE_FORMAT = "%Y_%m_%d-%I_%M_%S_%p"
        result = isCacheAvaliable(
            "TEST_RESULT_", timedelta(weeks=100000), mock_settings
        )
        if result is None:
            self.assertIsNotNone(None)
            return
        cotainsFile = (
            True if "TEST_RESULT_2025_06_11-01_46_37_PM.json" in result else False
        )
        self.assertTrue(cotainsFile)

    def test_finds_latest_file(self):
        mock_settings = MagicMock()
        dirname = os.path.dirname(__file__)
        mock_settings.DOWNLOADED_DATA_PATH = os.path.join(
            dirname, "testFiles/test_Downloaded_Data_Cache"
        )
        mock_settings.DATE_FORMAT = "%Y_%m_%d-%I_%M_%S_%p"
        result = isCacheAvaliable(
            "OTHER_RESULT_", timedelta(weeks=100000), mock_settings
        )
        if result is None:
            self.assertIsNotNone(None)
            return
        cotainsFile = (
            True if "OTHER_RESULT_2025_06_11-01_46_37_PM.json" in result else False
        )
        self.assertTrue(cotainsFile)


class Testfetch_api(unittest.TestCase):
    def test_fails_smoothly(self):
        session = Session()
        res = fetch_api(session, "https://asdfasdfadsasdsadsadsassfsdgfs.com")
        self.assertIsNone(res)

    def test_works(self):
        session = Session()
        res = fetch_api(session, "https://google.com")
        self.assertIsNotNone(res)


class Testfetch_full_catlog_ST(unittest.TestCase):
    def test_greater_than_10k_objects(self):
        fileName = fetch_full_catlog_ST(settings)
        self.assertIsNotNone(fileName)
