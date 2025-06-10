from typing import Literal, Optional, List
from datetime import datetime, date

"""
This file defines classes that represent the structure of satellite data being stored. Any data from different sources will have to map to the classes in this file
"""


class USC:
    """Represents the Universal Satellite Characteristics (USC).

    This class is designed to be a comprehensive container for satellite data,
    aggregating information from various sources like TLEs, OMMs, and external
    databases into a single, unified structure.
    """

    def __init__(
        self,
        ### Core TLE Data ###
        SATELLITE_NAME: str,  # Object Name
        NORAD_CAT_ID: str,
        CLASSIFICATION: Literal[
            "U", "C", "S"
        ],  # U: unclassified, C: classified, S: secret
        INTERNATIONAL_DESIGNATOR,
        EPOCH: datetime,
        MEAN_MOTION_DOT: float,  # First Derivative of Mean Motion
        MEAN_MOTION_DDOT: float,  # Second Derivative of Mean Motion
        B_STAR: float,  # B* Drag Term
        ELEMENT_SET_NUM: int,
        INCLINATION: float,
        RA_OF_ASC_NODE: float,  # Right Ascension of Ascending Node
        ECCENTRICITY: float,
        ARG_OF_PERIGEE: float,  # argument of periapsis (also called argument of perifocus or argument of pericenter)
        MEAN_ANOMALY: float,
        MEAN_MOTION: float,
        REV_AT_EPOCH: int,  # Revolution Number at Epoch
        EPHEMERIS_TYPE: int = 0,  # always zero; only used in undistributed TLE data
        ###              ###
        ### OMM Metadata ###
        CENTER_NAME: Optional[str] = None,  # The body being orbited
        TIME_SYSTEM: Optional[str] = None,  # Time System (e.g., UTC)
        MEAN_ELEMENT_THEORY: Optional[str] = None,  # Propagator model (e.g., SGP4)
        # User Defined / Derived Parameters
        SEMIMAJOR_AXIS: Optional[float] = None,
        PERIOD: Optional[float] = None,  # Orbital period in minutes
        APOAPSIS: Optional[float] = None,  # Altitude at apoapsis in km
        PERIAPSIS: Optional[float] = None,  # Altitude at periapsis in km
        OBJECT_TYPE: Optional[str] = None,  # e.g., PAYLOAD, ROCKET BODY
        RCS_SIZE: Optional[
            Literal["SMALL", "MEDIUM", "LARGE"]
        ] = None,  # Radar Cross-Section
        COUNTRY_CODE: Optional[str] = None,  # Originating country
        LAUNCH_DATE: Optional[date] = None,
        SITE: Optional[str] = None,  # Launch site code
        DECAY_DATE: Optional[date] = None,
        # Physical Characteristics (from external sources)
        DRY_MASS: Optional[float] = None,  # Dry mass in kilograms (kg)
        WET_MASS: Optional[float] = None,  # Wet mass (launch mass) in kg
        # General Import Data
        SOURCES: List[
            str
        ] = [],  # A list of sources on where this data came from (e.g., Space Tracker, CelesTrak)
    ):
        self.SATELLITE_NAME = SATELLITE_NAME
        self.NORAD_CAT_ID = NORAD_CAT_ID
        self.CLASSIFICATION = CLASSIFICATION
        self.INTERNATIONAL_DESIGNATOR = INTERNATIONAL_DESIGNATOR
        self.EPOCH = EPOCH
        self.MEAN_MOTION_DOT = MEAN_MOTION_DOT
        self.MEAN_MOTION_DDOT = MEAN_MOTION_DDOT
        self.B_STAR = B_STAR
        self.ELEMENT_SET_NUM = ELEMENT_SET_NUM
        self.INCLINATION = INCLINATION
        self.RA_OF_ASC_NODE = RA_OF_ASC_NODE
        self.ECCENTRICITY = ECCENTRICITY
        self.ARG_OF_PERIGEE = ARG_OF_PERIGEE
        self.MEAN_ANOMALY = MEAN_ANOMALY
        self.MEAN_MOTION = MEAN_MOTION
        self.REV_AT_EPOCH = REV_AT_EPOCH
        self.EPHEMERIS_TYPE = EPHEMERIS_TYPE
        self.CENTER_NAME = CENTER_NAME
        self.TIME_SYSTEM = TIME_SYSTEM
        self.MEAN_ELEMENT_THEORY = MEAN_ELEMENT_THEORY
        self.SEMIMAJOR_AXIS = SEMIMAJOR_AXIS
        self.PERIOD = PERIOD
        self.APOAPSIS = APOAPSIS
        self.PERIAPSIS = PERIAPSIS
        self.OBJECT_TYPE = OBJECT_TYPE
        self.RCS_SIZE = RCS_SIZE
        self.COUNTRY_CODE = COUNTRY_CODE
        self.LAUNCH_DATE = LAUNCH_DATE
        self.SITE = SITE
        self.DECAY_DATE = DECAY_DATE
        self.DRY_MASS = DRY_MASS
        self.WET_MASS = WET_MASS
        self.SOURCES = SOURCES
