from typing import Literal, Optional
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
        Satellite_Name: str,  # Object Name
        NORAD_CAT_ID: str,
        Classification: Literal[
            "U", "C", "S"
        ],  # U: unclassified, C: classified, S: secret
        International_Designator,
        EPOCH: datetime,
        MEAN_MOTION_DOT: float,  # First Derivative of Mean Motion
        MEAN_MOTION_DDOT: float,  # Second Derivative of Mean Motion
        B_STAR: float,  # B* Drag Term
        Element_Set_NUM: int,
        Inclination: float,
        RA_OF_ASC_NODE: float,  # Right Ascension of Ascending Node
        ECCENTRICITY: float,
        ARG_OF_PERIGEE: float,  # argument of periapsis (also called argument of perifocus or argument of pericenter)
        MEAN_ANOMALY: float,
        MEAN_MOTION: float,
        REV_AT_EPOCH: int,  # Revolution Number at Epoch
        Ephemeris_Type: int = 0,  # always zero; only used in undistributed TLE data
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
    ):
        pass
