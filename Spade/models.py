from typing import Literal, Optional, List
from datetime import datetime, date
from dataclasses import dataclass, field

"""
This file defines classes that represent the structure of satellite data being stored. Any data from different sources will have to map to the classes in this file
"""


@dataclass
class USC:
    """Represents the Universal Satellite Characteristics (USC).

    This class is designed to be a comprehensive container for satellite data,
    aggregating information from various sources like TLEs, OMMs, and external
    databases into a single, unified structure.
    """

    ### Core TLE Data ###


@dataclass
class USC:
    """Represents the Universal Satellite Characteristics (USC).

    This class is designed to be a comprehensive container for satellite data,
    aggregating information from various sources like TLEs, OMMs, and external
    databases into a single, unified structure.
    """

    ### Core TLE Data ###
    INTERNATIONAL_DESIGNATOR: str  # Object_ID or cosparId
    SATELLITE_NAME: Optional[str] = None  # Object Name
    NORAD_CAT_ID: Optional[str] = None
    CLASSIFICATION: Optional[Literal["U", "C", "S"]] = (
        None  # U: unclassified, C: classified, S: secret
    )
    EPOCH: Optional[datetime] = None
    MEAN_MOTION_DOT: Optional[float] = None  # First Derivative of Mean Motion
    MEAN_MOTION_DDOT: Optional[float] = None  # Second Derivative of Mean Motion
    B_STAR: Optional[float] = None  # B* Drag Term
    ELEMENT_SET_NUM: Optional[int] = None
    INCLINATION: Optional[float] = None
    RA_OF_ASC_NODE: Optional[float] = None  # Right Ascension of Ascending Node
    ECCENTRICITY: Optional[float] = None
    ARG_OF_PERIGEE: Optional[float] = (
        None  # argument of periapsis (also called argument of perifocus or argument of pericenter)
    )
    MEAN_ANOMALY: Optional[float] = None
    MEAN_MOTION: Optional[float] = None
    REV_AT_EPOCH: Optional[int] = None  # Revolution Number at Epoch
    EPHEMERIS_TYPE: Optional[int] = (
        0  # Note: 0 is a valid default, no need for `field` unless mutable
    )
    ###              ###
    ### OMM Metadata ###
    CENTER_NAME: Optional[str] = None  # The body being orbited
    TIME_SYSTEM: Optional[str] = None  # Time System (e.g., UTC)
    MEAN_ELEMENT_THEORY: Optional[str] = None  # Propagator model (e.g., SGP4)
    # User Defined / Derived Parameters
    SEMIMAJOR_AXIS: Optional[float] = None
    PERIOD: Optional[float] = None  # Orbital period in minutes
    APOAPSIS: Optional[float] = None  # Altitude at apoapsis in km
    PERIAPSIS: Optional[float] = None  # Altitude at periapsis in km
    OBJECT_TYPE: Optional[str] = None  # e.g., PAYLOAD, ROCKET BODY
    RCS_SIZE: Optional[Literal["SMALL", "MEDIUM", "LARGE"]] = (
        None  # Radar Cross-Section
    )
    COUNTRY_CODE: Optional[str] = None  # Originating country
    LAUNCH_DATE: Optional[date] = None
    SITE: Optional[str] = None  # Launch site code
    DECAY_DATE: Optional[date] = None
    # Physical Characteristics (From ESA DISCOS)
    DRY_MASS: Optional[float] = None  # Dry mass in kilograms (kg)
    WET_MASS: Optional[float] = None  # Wet mass (launch mass) in kg
    SHAPE: Optional[str] = None  # (e.g 	Sphere, Cyl, Hex Cyl + 2 Pan)
    WIDTH: Optional[float] = None  # meters
    HEIGHT: Optional[float] = None  # meters
    DEPTH: Optional[float] = None  # meters
    DIAMETER: Optional[float] = None  # meters
    SPAN: Optional[float] = None  # meters
    X_SECT_MAX: Optional[float] = None  # Maximum Cross Section meters^2
    X_SECT_MIN: Optional[float] = None  # Minimum Cross Section meters^2
    X_SECT_AVG: Optional[float] = None  # Average Cross Section meters^2
    MISSION_DESC: Optional[str] = (
        None  # Mission Description (e.g 	Amateur Technology, Defense Technology	)
    )
    # General Import Data
    SOURCES: List[str] = field(
        default_factory=list
    )  # A list of sources on where this data came from (e.g., Space Tracker, CelesTrak, DISCOS)
