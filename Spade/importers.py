import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
from Spade.models import USC
from datetime import datetime, date

from Spade.types import DiscosObjectList


def convert_types(raw_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    helper to convert raw string values from XML to correct Python types
    """
    typed = raw_params.copy()
    for key, value in typed.items():

        if value is None or value == "":
            typed[key] = None
            continue

        match key:

            case (
                "MEAN_MOTION_DOT"
                | "MEAN_MOTION_DDOT"
                | "B_STAR"
                | "INCLINATION"
                | "RA_OF_ASC_NODE"
                | "ECCENTRICITY"
                | "ARG_OF_PERIGEE"
                | "MEAN_ANOMALY"
                | "MEAN_MOTION"
                | "SEMIMAJOR_AXIS"
                | "PERIOD"
                | "APOAPSIS"
                | "PERIAPSIS"
            ):
                typed[key] = float(value)

            case "ELEMENT_SET_NUM" | "REV_AT_EPOCH" | "EPHEMERIS_TYPE":
                typed[key] = int(value)

            case "EPOCH":
                typed[key] = datetime.fromisoformat(value)

            case "LAUNCH_DATE" | "DECAY_DATE":
                typed[key] = date.fromisoformat(value)

            case _:
                pass

    return typed


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


def XMLtoUSC(
    filename: str,
    item_location: str,
    standard_map: Dict[str, str],
    user_defined_map: Optional[Dict[str, str]] = user_defined_map,
    user_defined_path: Optional[str] = "./data/userDefinedParameters",
) -> List[USC]:
    """
    Generic helper to parse an XML file into a list of USC objects based on maps.

    Args:
        filename: Path to the XML file.
        item_location: The XPath to find iterable elements (e.g., './body/segment').
        standard_map: Maps USC attributes to their direct XPath from the item.
        user_defined_map: Maps USC attributes to the 'parameter' attribute value
                          in user-defined tags.
        user_defined_path: The path from the item to the user-defined container tag.

    Returns:
        A list of populated USC objects.
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML file '{filename}': {e}")
        return []

    usc_items: List[USC] = []

    for item in root.findall(item_location):
        raw_params: Dict[str, Any] = {}

        # 1. Process standard, path-based parameters
        for usc_attr, xml_path in standard_map.items():
            element = item.find(xml_path)
            if element is not None and element.text is not None:
                raw_params[usc_attr] = element.text.strip()

        # 2. Process special user-defined parameters if maps are provided
        if user_defined_map and user_defined_path:
            for user_def_element in item.findall(f"{user_defined_path}/USER_DEFINED"):
                param_key = user_def_element.get("parameter")
                if param_key in user_defined_map:
                    usc_attr = user_defined_map[param_key]
                    raw_params[usc_attr] = (
                        user_def_element.text.strip() if user_def_element.text else None
                    )

        # 3. Convert types and create the USC object
        try:
            typed_params = convert_types(raw_params)
            usc_items.append(USC(**typed_params))
        except (KeyError, TypeError, ValueError) as e:
            norad_id = raw_params.get("NORAD_CAT_ID", "UNKNOWN")
            print(
                f"Could not create USC for NORAD ID {norad_id}. "
                f"Missing data or type error: {e}"
            )

    return usc_items


def spaceTrackXML(filename):
    """
    Parses a Space-Track.org OMM XML file and returns a list of USC objects.

    Args:
        filename: The path to the XML file.

    Returns:
        A list of USC objects, each populated with data for a single satellite.
    """

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

    return XMLtoUSC(filename, "./omm/body/segment", XML_TO_USC_MAP)


def jsonToUSC(filename: str, attribute_map: Dict[str, str]) -> List[USC]:
    with open(filename, "r") as f:
        data: DiscosObjectList = json.load(f)

    if not isinstance(data, list):
        raise TypeError("JSON file content must be a list of objects.")

    usc_items: List[USC] = []

    for item in data:
        raw_params: Dict[str, Any] = {}
        attributes = item["attributes"]
        for usc_key, json_key in attribute_map.items():
            if json_key in attributes:
                raw_params[usc_key] = attributes[json_key]

        try:
            typed_params = convert_types(raw_params)
            usc_items.append(USC(**typed_params))
        except (KeyError, TypeError, ValueError) as e:
            norad_id = raw_params.get("NORAD_CAT_ID", "UNKNOWN")
            print(
                f"Could not create USC for NORAD ID {norad_id}. "
                f"Missing data or type error: {e}"
            )

    return usc_items


def parseDISCOSJSON(filename: str) -> List[USC]:
    JSON_To_USC_Map = {
        "SATELLITE_NAME": "name",
        "INTERNATIONAL_DESIGNATOR": "cosparId",
        "OBJECT_TYPE": "objectClass",
        "DRY_MASS": "mass",
        "SHAPE": "shape",
        "WIDTH": "width",
        "HEIGHT": "height",
        "DEPTH": "depth",
        "DIAMETER": "diameter",
        "SPAN": "span",
        "X_SECT_MAX": "xSectMax",
        "X_SECT_MIN": "xSectMin",
        "X_SECT_AVG": "xSectAvg",
        "MISSION_DESC": "mission",
    }

    return jsonToUSC(filename, JSON_To_USC_Map)
