import unittest
from Spade.data_fetcher import get_auth_space_tracker
from requests import Session


class TestGetAuthSpaceTracker(unittest.TestCase):

    def test_bad_login_fails_smoothly(self):
        session = Session()
        get_auth_space_tracker(session, "badusername", "badpassword")
        print(session.cookies)

    def test_correct_login(self):
        self.assertTrue(False)


class isCacheAvaliable(unittest.TestCase):

    def test_bad_fileprefix_returns_None(self):
        self.assertTrue(False)

    def test_finds_single_file(self):
        self.assertTrue(False)

    def test_finds_latest_file(self):
        self.assertTrue(False)


class downloadedFileList(unittest.TestCase):

    def test_invalid_path_returns_empty(self):
        self.assertTrue(False)

    def test_properly_lists_dir(self):
        self.assertTrue(False)


class fetch_api(unittest.TestCase):
    def test_fails_smoothly(self):
        self.assertTrue(False)


class fetch_full_catlog_ST(unittest.TestCase):
    def test_greater_than_10k_objects(self):
        self.assertTrue(False)
