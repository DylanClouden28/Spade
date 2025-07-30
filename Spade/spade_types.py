from typing import (
    Literal,
    TypedDict,
    Optional,
    Dict,
    List,
    cast,
)


### For DISCOS OBJECT LIST TYPE
from typing import Dict, List, Literal, Optional, TypedDict, Union, Any


class OrbitAttributes(TypedDict, total=False):
    """Attributes for an initial orbit resource."""

    epoch: Optional[str]  # string or null <date>
    sma: Optional[float]  # number or null, Semi-major axis (m)
    ecc: Optional[float]  # number or null, Eccentricity
    inc: Optional[float]  # number or null, Inclination (deg)
    raan: Optional[float]  # number or null, Right ascension of the ascending node (deg)
    aPer: Optional[float]  # number or null, Argument of periapsis (deg)
    mAno: Optional[float]  # number or null, Mean anomaly (deg)
    frame: str  # string, Reference frame


class ResourceLinks(TypedDict):
    """Links object for a JSON:API resource."""

    self: str


class Orbit(TypedDict):
    """A JSON:API resource object representing a single initial orbit."""

    id: str
    type: Literal["initialOrbit"]
    attributes: OrbitAttributes
    # The provided schema for an orbit's relationships is generic.
    # This can be made more specific if the relationships are known.
    relationships: Dict[str, Any]
    links: ResourceLinks


class PaginationLinks(TypedDict, total=False):
    """Links object for a paginated JSON:API response."""

    first: str
    last: str
    next: Optional[str]
    prev: Optional[str]


class SingleInitialOrbitResponse(TypedDict):
    """The full response for a GET request to a single initial orbit."""

    data: Orbit
    links: PaginationLinks
    included: Optional[List[Any]]
    meta: Optional[Dict[str, Any]]


class ResourceIdentifier(TypedDict):
    """A JSON:API resource identifier object."""

    id: str
    type: str


class RelationshipLinks(TypedDict, total=False):
    """Links object within a JSON:API relationship."""

    self: str
    related: str


# A relationship's `data` can be null, a single identifier, or a list of them.
RelationshipDataToOne = Optional[ResourceIdentifier]
RelationshipDataToMany = List[ResourceIdentifier]


class RelationshipObject(TypedDict, total=False):
    """A complete JSON:API relationship object with links and data."""

    links: RelationshipLinks
    data: Union[RelationshipDataToOne, RelationshipDataToMany]
    meta: Optional[Dict[str, Any]]


class ObjectAttributes(TypedDict, total=False):
    cosparId: Optional[str]  # International Designator (string)
    vimpelId: Optional[int]  # JSC Vimpel sequence number (int or null)
    satno: Optional[
        int
    ]  # Satellite Catalogue Number assigned by USSPACECOM (int or null)
    name: Optional[str]  # Object name (string or null)
    objectClass: Optional[str]  # Object class/category (string)
    mass: Optional[float]  # Mass in kilograms (kg) (float or null)
    shape: Optional[str]  # Coarse description of object shape (string or null)
    width: Optional[float]  # Width in meters (m) (float or null)
    height: Optional[float]  # Height in meters (m) (float or null)
    depth: Optional[float]  # Depth in meters (m) (float or null)
    diameter: Optional[float]  # Diameter in meters (m) (float or null)
    span: Optional[
        float
    ]  # Largest dimension including appendices in meters (m) (float or null)
    xSectMax: Optional[
        float
    ]  # Computed maximum cross section in square meters (m^2) (float or null)
    xSectMin: Optional[
        float
    ]  # Computed minimum cross section in square meters (m^2) (float or null)
    xSectAvg: Optional[
        float
    ]  # Computed average cross section in square meters (m^2) (float or null)
    firstEpoch: Optional[str]  # First epoch (string or null, <date-time>)
    mission: Optional[str]  # Mission description (string or null)
    predDecayDate: Optional[str]  # Predicted decay date (string or null, <date-time>)
    active: Optional[bool]  # Whether the object is active (boolean or null)
    cataloguedFragments: Optional[int]  # Number of catalogued fragments (int or null)
    onOrbitCataloguedFragments: Optional[
        int
    ]  # Number of catalogued fragments still on orbit (int or null)


class ObjectRelationships(TypedDict):
    """
    Updated relationships for a DISCOS object, using the detailed
    RelationshipObject type.
    """

    launch: RelationshipObject
    reentry: RelationshipObject
    initialOrbits: RelationshipObject
    destinationOrbits: RelationshipObject
    states: RelationshipObject
    operators: RelationshipObject
    tags: RelationshipObject
    constellations: RelationshipObject


class DiscosObject(TypedDict):
    """
    Updated DISCOS object type using the more specific ResourceLinks.
    """

    id: str
    type: Literal["object"]
    attributes: ObjectAttributes
    relationships: ObjectRelationships
    links: ResourceLinks


DiscosObjectList = List[DiscosObject]


class Pagination(TypedDict):
    totalPages: int
    currentPage: int
    pageSize: int


class ResponsePagination(TypedDict):
    pagination: Pagination


# The `included` field can contain various resource types. We define a Union
# for them. Add other included types (e.g., Launch, Reentry) here as needed.
IncludedResource = Union[Orbit]


class DiscosObjectListResponse(TypedDict):
    """
    The response for a list of DISCOS objects, now including the optional
    `included` field to handle sideloaded data from the `?include` parameter.
    """

    data: DiscosObjectList
    links: PaginationLinks
    meta: ResponsePagination
    included: Optional[List[IncludedResource]]


######################################
######################################
######################################

# Types for space track


class GpData(TypedDict):
    """
    Represents a single General Perturbation (GP) data object from
    Space-Track.org, in OMM JSON format. The types are derived from the
    official Space-Track database schema.
    "https://www.space-track.org/basicspacedata/modeldef/class/gp/format/html"
    """

    # --- Other Data (OMM Header and Derived Properties) ---
    # These fields typically represent general metadata or OMM (Orbit Mean-Element Message)
    # header information not directly part of the TLE set itself, or derived
    # physical properties calculated from the TLE elements.
    CCSDS_OMM_VERS: str
    COMMENT: str
    CREATION_DATE: Optional[str]
    ORIGINATOR: str
    OBJECT_NAME: Optional[str]
    OBJECT_ID: Optional[str]  # e.g., International Designator like '98067A'
    CENTER_NAME: str
    REF_FRAME: str
    TIME_SYSTEM: str
    MEAN_ELEMENT_THEORY: str

    # --- TLE Data (Raw Lines and Parsed Elements) ---
    # These fields are either the raw TLE lines or elements directly
    # parsed from the TLE lines 1 and 2, along with metadata intrinsically
    # defining the TLE itself.

    # Raw TLE Lines
    TLE_LINE0: Optional[str]  # Satellite Name/Common Name
    TLE_LINE1: Optional[str]  # Raw TLE Line 1 string
    TLE_LINE2: Optional[str]  # Raw TLE Line 2 string

    # Parsed TLE Elements
    NORAD_CAT_ID: int
    CLASSIFICATION_TYPE: Optional[str]  # U, C, or S
    EPOCH: Optional[str]  # Epoch year and day of year
    MEAN_MOTION_DOT: Optional[float]  # First derivative of mean motion
    MEAN_MOTION_DDOT: Optional[float]  # Second derivative of mean motion
    BSTAR: Optional[float]  # B* drag term
    EPHEMERIS_TYPE: Optional[int]  # Typically 0
    ELEMENT_SET_NO: Optional[int]  # Incremented when a new TLE is generated

    INCLINATION: Optional[float]  # Inclination in degrees
    RA_OF_ASC_NODE: Optional[float]  # Right Ascension of Ascending Node in degrees
    ECCENTRICITY: Optional[float]  # Eccentricity, decimal point assumed
    ARG_OF_PERICENTER: Optional[float]  # Argument of Perigee in degrees
    MEAN_ANOMALY: Optional[float]  # Mean Anomaly in degrees
    MEAN_MOTION: Optional[float]  # Mean Motion in revolutions per day
    REV_AT_EPOCH: Optional[int]  # Revolution number at epoch

    # --- Other Data (continued: Additional Object Properties & Database IDs) ---
    # These fields represent additional object properties, derived orbital
    # characteristics, or historical/administrative information
    # that are not directly contained within or defining the TLE lines.
    SEMIMAJOR_AXIS: Optional[float]  # Derived (from Mean Motion)
    PERIOD: Optional[float]  # Derived (from Mean Motion)
    APOAPSIS: Optional[float]  # Derived (from Eccentricity, Semimajor Axis)
    PERIAPSIS: Optional[float]  # Derived (from Eccentricity, Semimajor Axis)
    OBJECT_TYPE: Optional[str]
    RCS_SIZE: Optional[str]  # Radar Cross Section Size
    COUNTRY_CODE: Optional[str]
    LAUNCH_DATE: Optional[str]
    SITE: Optional[str]  # Launch Site
    DECAY_DATE: Optional[str]
    FILE: Optional[int]  # Space-Track.org specific ID
    GP_ID: int  # Space-Track.org specific GP (General Perturbation) ID


GpDataList = List[GpData]


class SatcatDebutData(TypedDict):
    """
    Represents a single record from the Space-Track satcat_debut endpoint.
    https://www.space-track.org/basicspacedata/modeldef/class/satcat_debut/format/html
    """

    INTLDES: str
    NORAD_CAT_ID: Optional[int]
    OBJECT_TYPE: Optional[str]
    SATNAME: str
    DEBUT: Optional[str]
    COUNTRY: str
    LAUNCH: Optional[str]
    SITE: Optional[str]
    DECAY: Optional[str]
    PERIOD: Optional[float]
    INCLINATION: Optional[float]
    APOGEE: Optional[int]
    PERIGEE: Optional[int]
    COMMENT: Optional[str]
    COMMENTCODE: Optional[int]
    RCSVALUE: int
    RCS_SIZE: Optional[str]
    FILE: int
    LAUNCH_YEAR: int
    LAUNCH_NUM: int
    LAUNCH_PIECE: str
    CURRENT: str
    OBJECT_NAME: str
    OBJECT_ID: str
    OBJECT_NUMBER: Optional[int]


SatcatDebutDataList = List[SatcatDebutData]


class AnnouncementData(TypedDict):
    """
    Represents a single announcement record from the Space-Track.org API.
    https://www.space-track.org/basicspacedata/modeldef/class/announcement/format/html
    """

    announcement_type: str
    announcement_text: str
    announcement_start: str  # datetime in string format
    announcement_end: str  # datetime in string format


AnnouncementDataList = List[AnnouncementData]


class BoxscoreData(TypedDict):
    """
    Represents a single boxscore record from the Space-Track.org API,
    accounting for man-made objects in orbit, grouped by country.
    https://www.space-track.org/basicspacedata/modeldef/class/boxscore/format/html
    """

    COUNTRY: str
    SPADOC_CD: Optional[str]
    ORBITAL_TBA: Optional[int]
    ORBITAL_PAYLOAD_COUNT: Optional[int]
    ORBITAL_ROCKET_BODY_COUNT: Optional[int]
    ORBITAL_DEBRIS_COUNT: Optional[int]
    ORBITAL_TOTAL_COUNT: Optional[int]
    DECAYED_PAYLOAD_COUNT: Optional[int]
    DECAYED_ROCKET_BODY_COUNT: Optional[int]
    DECAYED_DEBRIS_COUNT: Optional[int]
    DECAYED_TOTAL_COUNT: Optional[int]
    COUNTRY_TOTAL: int


BoxscoreDataList = List[BoxscoreData]


class CdmPublicData(TypedDict):
    """
    Represents a single public Conjunction Data Message (CDM) record
    from the Space-Track.org API.
    https://www.space-track.org/basicspacedata/modeldef/class/cdm_public/format/html
    """

    CDM_ID: int
    CREATED: Optional[str]  # datetime(6)
    EMERGENCY_REPORTABLE: Optional[str]  # char(1)
    TCA: Optional[str]  # datetime(6)
    MIN_RNG: Optional[float]
    PC: Optional[float]
    SAT_1_ID: Optional[int]
    SAT_1_NAME: Optional[str]
    SAT1_OBJECT_TYPE: Optional[str]
    SAT1_RCS: Optional[str]
    SAT_1_EXCL_VOL: Optional[str]
    SAT_2_ID: Optional[int]
    SAT_2_NAME: Optional[str]
    SAT2_OBJECT_TYPE: Optional[str]
    SAT2_RCS: Optional[str]
    SAT_2_EXCL_VOL: Optional[str]


CdmPublicDataList = List[CdmPublicData]


class DecayData(TypedDict):
    """
    Represents a single decay prediction or historical record from the
    Space-Track.org API.
    https://www.space-track.org/basicspacedata/modeldef/class/decay/format/html
    """

    NORAD_CAT_ID: Optional[int]
    OBJECT_NUMBER: Optional[int]
    OBJECT_NAME: str
    INTLDES: str
    OBJECT_ID: str
    RCS: int
    RCS_SIZE: Optional[str]
    COUNTRY: str
    MSG_EPOCH: Optional[str]  # datetime in string format
    DECAY_EPOCH: Optional[str]  # datetime in string format
    SOURCE: str
    MSG_TYPE: str
    PRECEDENCE: int


DecayDataList = List[DecayData]


# New types for gp_history
class GpHistoryData(TypedDict):
    """
    Represents a single historical General Perturbation (GP) data object
    from Space-Track.org, similar to GpData but for historical records.
    https://www.space-track.org/basicspacedata/modeldef/class/gp_history/format/html
    """

    CCSDS_OMM_VERS: str
    COMMENT: str
    CREATION_DATE: Optional[str]
    ORIGINATOR: str
    OBJECT_NAME: Optional[str]
    OBJECT_ID: Optional[str]
    CENTER_NAME: str
    REF_FRAME: str
    TIME_SYSTEM: str
    MEAN_ELEMENT_THEORY: str
    EPOCH: Optional[str]  # datetime(6)
    MEAN_MOTION: Optional[float]
    ECCENTRICITY: Optional[float]
    INCLINATION: Optional[float]
    RA_OF_ASC_NODE: Optional[float]
    ARG_OF_PERICENTER: Optional[float]
    MEAN_ANOMALY: Optional[float]
    EPHEMERIS_TYPE: Optional[int]
    CLASSIFICATION_TYPE: Optional[str]
    NORAD_CAT_ID: int
    ELEMENT_SET_NO: Optional[int]
    REV_AT_EPOCH: Optional[int]
    BSTAR: Optional[float]
    MEAN_MOTION_DOT: Optional[float]
    MEAN_MOTION_DDOT: Optional[float]
    SEMIMAJOR_AXIS: Optional[float]
    PERIOD: Optional[float]
    APOAPSIS: Optional[float]
    PERIAPSIS: Optional[float]
    OBJECT_TYPE: Optional[str]
    RCS_SIZE: Optional[str]
    COUNTRY_CODE: Optional[str]
    LAUNCH_DATE: Optional[str]
    SITE: Optional[str]
    DECAY_DATE: Optional[str]
    FILE: Optional[int]
    GP_ID: int
    TLE_LINE0: Optional[str]
    TLE_LINE1: Optional[str]
    TLE_LINE2: Optional[str]


GpHistoryDataList = List[GpHistoryData]


class LaunchSiteData(TypedDict):
    """
    Represents a single launch site record from the Space-Track.org API.
    https://www.space-track.org/basicspacedata/modeldef/class/launch_site/format/html
    """

    SITE_CODE: str
    LAUNCH_SITE: str


LaunchSiteDataList = List[LaunchSiteData]


class SatcatData(TypedDict):
    """
    Represents a single satellite catalog record from the Space-Track.org API.
    https://www.space-track.org/basicspacedata/modeldef/class/satcat/format/html
    """

    INTLDES: str
    NORAD_CAT_ID: Optional[int]
    OBJECT_TYPE: Optional[str]
    SATNAME: str
    COUNTRY: str
    LAUNCH: Optional[str]  # date in string format
    SITE: Optional[str]
    DECAY: Optional[str]  # date in string format
    PERIOD: Optional[float]
    INCLINATION: Optional[float]
    APOGEE: Optional[int]
    PERIGEE: Optional[int]
    COMMENT: Optional[str]
    COMMENTCODE: Optional[int]
    RCSVALUE: int
    RCS_SIZE: Optional[str]
    FILE: int
    LAUNCH_YEAR: int
    LAUNCH_NUM: int
    LAUNCH_PIECE: str
    CURRENT: Literal["Y", "N"]  # 'Y' or 'N'
    OBJECT_NAME: str
    OBJECT_ID: str
    OBJECT_NUMBER: Optional[int]


SatcatDataList = List[SatcatData]


class SatcatChangeData(TypedDict):
    """
    Represents a single satellite catalog change record from the
    Space-Track.org API.
    https://www.space-track.org/basicspacedata/modeldef/class/satcat_change/format/html
    """

    NORAD_CAT_ID: Optional[int]
    OBJECT_NUMBER: Optional[int]
    CURRENT_NAME: str
    PREVIOUS_NAME: Optional[str]
    CURRENT_INTLDES: str
    PREVIOUS_INTLDES: Optional[str]
    CURRENT_COUNTRY: str
    PREVIOUS_COUNTRY: Optional[str]
    CURRENT_LAUNCH: Optional[str]  # date in string format
    PREVIOUS_LAUNCH: Optional[str]  # date in string format
    CURRENT_DECAY: Optional[str]  # date in string format
    PREVIOUS_DECAY: Optional[str]  # date in string format
    CHANGE_MADE: Optional[str]  # datetime in string format


SatcatChangeDataList = List[SatcatChangeData]


class TipData(TypedDict):
    """
    Represents a single Tracking and Impact Prediction (TIP) message
    record from the Space-Track.org API.
    https://www.space-track.org/basicspacedata/modeldef/class/tip/format/html
    """

    NORAD_CAT_ID: Optional[int]
    MSG_EPOCH: str  # datetime in string format
    INSERT_EPOCH: str  # datetime in string format
    DECAY_EPOCH: str  # datetime in string format
    WINDOW: int
    REV: int
    DIRECTION: Optional[
        Literal["ascending", "descending"]
    ]  # 'ascending' or 'descending'
    LAT: float
    LON: float
    INCL: float
    NEXT_REPORT: int
    ID: int
    HIGH_INTEREST: Optional[Literal["Y", "N"]]  # 'Y' or 'N'
    OBJECT_NUMBER: Optional[int]


TipDataList = List[TipData]
