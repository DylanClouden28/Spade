from datetime import datetime, date
import unittest
import os
from Spade.models import USC
from Spade.importers import spaceTrackXML, XMLtoUSC, convert_types_XML

"""
This file contains tests for importers.
"""

expectedFirstUSC = USC(
    SATELLITE_NAME="VANGUARD 1",
    NORAD_CAT_ID="5",
    CLASSIFICATION="U",
    INTERNATIONAL_DESIGNATOR="1958-002B",
    EPOCH=datetime(2025, 6, 8, 15, 45, 48, 574080),
    MEAN_MOTION_DOT=0.00000038,
    MEAN_MOTION_DDOT=0.0,
    B_STAR=0.000022681,
    ELEMENT_SET_NUM=999,
    INCLINATION=34.2624,
    RA_OF_ASC_NODE=27.2113,
    ECCENTRICITY=0.18418470,
    ARG_OF_PERIGEE=254.3563,
    MEAN_ANOMALY=84.7117,
    MEAN_MOTION=10.85926524,
    REV_AT_EPOCH=40267,
    EPHEMERIS_TYPE=0,
    CENTER_NAME="EARTH",
    TIME_SYSTEM="UTC",
    MEAN_ELEMENT_THEORY="SGP4",
    SEMIMAJOR_AXIS=8613.934,
    PERIOD=132.606,
    APOAPSIS=3822.354,
    PERIAPSIS=649.244,
    OBJECT_TYPE="PAYLOAD",
    RCS_SIZE="SMALL",
    COUNTRY_CODE="US",
    LAUNCH_DATE=date(1958, 3, 17),
    SITE="AFETR",
    DECAY_DATE=None,
    SOURCES=[],
)

expectedLastUSC = USC(
    SATELLITE_NAME="TBA - TO BE ASSIGNED",
    NORAD_CAT_ID="270438",
    CLASSIFICATION="U",
    INTERNATIONAL_DESIGNATOR="UNKNOWN",
    EPOCH=datetime(2025, 6, 8, 17, 16, 30, 74592),
    MEAN_MOTION_DOT=0.00001142,
    MEAN_MOTION_DDOT=0.0,
    B_STAR=0.00049035846,
    ELEMENT_SET_NUM=999,
    INCLINATION=88.9278,
    RA_OF_ASC_NODE=314.5867,
    ECCENTRICITY=0.02170756,
    ARG_OF_PERIGEE=259.4467,
    MEAN_ANOMALY=98.2201,
    MEAN_MOTION=14.12410113,
    REV_AT_EPOCH=4079,
    EPHEMERIS_TYPE=0,
    CENTER_NAME="EARTH",
    TIME_SYSTEM="UTC",
    MEAN_ELEMENT_THEORY="SGP4",
    SEMIMAJOR_AXIS=7229.273,
    PERIOD=101.953,
    APOAPSIS=1008.068,
    PERIAPSIS=694.208,
    OBJECT_TYPE="UNKNOWN",
    RCS_SIZE=None,
    COUNTRY_CODE=None,
    LAUNCH_DATE=None,
    SITE=None,
    DECAY_DATE=None,
    SOURCES=[],
)


class TestSpaceTrackXML(unittest.TestCase):

    def test_returns_list(self):
        dirname = os.path.dirname(__file__)
        testFile = os.path.join(dirname, "testFiles/testSpaceTrack.xml")
        listUSCs = spaceTrackXML(testFile)
        self.assertGreater(len(listUSCs), 0)

    def test_first_element(self):
        dirname = os.path.dirname(__file__)
        testFile = os.path.join(dirname, "testFiles/testSpaceTrack.xml")
        listUSCs = spaceTrackXML(testFile)
        self.assertEqual(expectedFirstUSC, listUSCs[0])

    def test_last_element(self):
        dirname = os.path.dirname(__file__)
        testFile = os.path.join(dirname, "testFiles/testSpaceTrack.xml")
        listUSCs = spaceTrackXML(testFile)
        self.assertEqual(expectedLastUSC, listUSCs[-1])


class TestXMLtoUSC(unittest.TestCase):

    def test_returns_something(self):
        dirname = os.path.dirname(__file__)
        testFile = os.path.join(dirname, "testFiles/testSpaceTrack.xml")
        listUSCs = XMLtoUSC(testFile, "./omm/body/segment", XML_TO_USC_MAP)
        self.assertGreater(len(listUSCs), 0)

    def test_first_element(self):
        dirname = os.path.dirname(__file__)
        testFile = os.path.join(dirname, "testFiles/testSpaceTrack.xml")
        listUSCs = XMLtoUSC(testFile, "./omm/body/segment", XML_TO_USC_MAP)

        self.assertEqual(expectedFirstUSC, listUSCs[0])

    def test_last_element(self):
        dirname = os.path.dirname(__file__)
        testFile = os.path.join(dirname, "testFiles/testSpaceTrack.xml")
        listUSCs = XMLtoUSC(testFile, "./omm/body/segment", XML_TO_USC_MAP)

        self.assertEqual(expectedLastUSC, listUSCs[-1])


class convertTypesXML(unittest.TestCase):

    def test_simple_string(self):
        test_dict = {"SATELLITE_NAME": "VANGUARD 1"}
        typed_dict = convert_types_XML(test_dict)
        self.assertDictEqual(test_dict, typed_dict)

    def test_float_conversion(self):
        raw_dict = {
            "MEAN_MOTION": "10.85926524",
            "ECCENTRICITY": "0.18418470",
            "INCLINATION": "34.2624",
        }
        expected_dict = {
            "MEAN_MOTION": 10.85926524,
            "ECCENTRICITY": 0.18418470,
            "INCLINATION": 34.2624,
        }
        typed_dict = convert_types_XML(raw_dict)
        self.assertDictEqual(typed_dict, expected_dict)

    def test_int_conversion(self):
        raw_dict = {
            "ELEMENT_SET_NUM": "999",
            "REV_AT_EPOCH": "40267",
        }
        expected_dict = {
            "ELEMENT_SET_NUM": 999,
            "REV_AT_EPOCH": 40267,
        }
        typed_dict = convert_types_XML(raw_dict)
        self.assertDictEqual(typed_dict, expected_dict)

    def test_datetime_conversion(self):
        raw_dict = {
            "EPOCH": "2025-06-08T15:45:48.574080",
        }
        expected_dict = {"EPOCH": datetime(2025, 6, 8, 15, 45, 48, 574080)}
        typed_dict = convert_types_XML(raw_dict)
        self.assertDictEqual(typed_dict, expected_dict)

    def test_date_conversion(self):
        raw_dict = {
            "LAUNCH_DATE": "1958-03-17",
        }
        expected_dict = {"LAUNCH_DATE": date(1958, 3, 17)}
        typed_dict = convert_types_XML(raw_dict)
        self.assertDictEqual(typed_dict, expected_dict)

    def test_unkown_value(self):
        raw_dict = {
            "35adsfasdf": "1958-03-17",
            "lksjfs": "1324234",
        }
        expected_dict = {
            "35adsfasdf": "1958-03-17",
            "lksjfs": "1324234",
        }
        typed_dict = convert_types_XML(raw_dict)
        self.assertDictEqual(typed_dict, expected_dict)

    pass


XML_TO_USC_MAP = {
    "SATELLITE_NAME": "./metadata/OBJECT_NAME",
    "INTERNATIONAL_DESIGNATOR": "./metadata/OBJECT_ID",
    "CENTER_NAME": "./metadata/CENTER_NAME",
    "TIME_SYSTEM": "./metadata/TIME_SYSTEM",
    "MEAN_ELEMENT_THEORY": "./metadata/MEAN_ELEMENT_THEORY",
    "EPOCH": "./data/meanElements/EPOCH",
    "MEAN_MOTION": "./data/meanElements/MEAN_MOTION",
    "ECCENTRICITY": "./data/meanElements/ECCENTRICITY",
    "INCLINATION": "./data/meanElements/INCLINATION",
    "RA_OF_ASC_NODE": "./data/meanElements/RA_OF_ASC_NODE",
    "ARG_OF_PERIGEE": "./data/meanElements/ARG_OF_PERICENTER",
    "MEAN_ANOMALY": "./data/meanElements/MEAN_ANOMALY",
    "EPHEMERIS_TYPE": "./data/tleParameters/EPHEMERIS_TYPE",
    "CLASSIFICATION": "./data/tleParameters/CLASSIFICATION_TYPE",
    "NORAD_CAT_ID": "./data/tleParameters/NORAD_CAT_ID",
    "ELEMENT_SET_NUM": "./data/tleParameters/ELEMENT_SET_NO",
    "REV_AT_EPOCH": "./data/tleParameters/REV_AT_EPOCH",
    "B_STAR": "./data/tleParameters/BSTAR",
    "MEAN_MOTION_DOT": "./data/tleParameters/MEAN_MOTION_DOT",
    "MEAN_MOTION_DDOT": "./data/tleParameters/MEAN_MOTION_DDOT",
}

user_defined_map = {
    "SEMIMAJOR_AXIS": "SEMIMAJOR_AXIS",
    "PERIOD": "PERIOD",
    "APOAPSIS": "APOAPSIS",
    "PERIAPSIS": "PERIAPSIS",
    "OBJECT_TYPE": "OBJECT_TYPE",
    "RCS_SIZE": "RCS_SIZE",
    "COUNTRY_CODE": "COUNTRY_CODE",
    "LAUNCH_DATE": "LAUNCH_DATE",
    "SITE": "SITE",
    "DECAY_DATE": "DECAY_DATE",
}


if __name__ == "__main__":
    unittest.main()
