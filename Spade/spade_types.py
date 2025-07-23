from typing import (
    Literal,
    TypedDict,
    Optional,
    Dict,
    List,
    cast,
)


### For DISCOS OBJECT LIST TYPE
class _Links(TypedDict):
    self: str
    related: Optional[str]


class _Relationship(TypedDict):
    links: _Links


class Pagination(TypedDict):
    totalPages: int
    currentPage: int
    pageSize: int


class ResponsePagination(TypedDict):
    pagination: Pagination


class ObjectRelationships(TypedDict):
    launch: _Relationship
    reentry: _Relationship
    initialOrbits: _Relationship
    destinationOrbits: _Relationship
    states: _Relationship
    operators: _Relationship
    tags: _Relationship
    constellations: _Relationship


class ObjectAttributes(TypedDict, total=False):
    cosparId: Optional[str]
    vimpelId: Optional[int]
    satno: Optional[int]
    name: Optional[str]
    objectClass: Optional[str]
    mass: Optional[float]
    shape: Optional[str]
    width: Optional[float]
    height: Optional[float]
    depth: Optional[float]
    diameter: Optional[float]
    span: Optional[float]
    xSectMax: Optional[float]
    xSectMin: Optional[float]
    xSectAvg: Optional[float]
    firstEpoch: Optional[str]
    mission: Optional[str]
    predDecayDate: Optional[str]
    active: Optional[bool]
    cataloguedFragments: Optional[int]
    onOrbitCataloguedFragments: Optional[int]


class DiscosObject(TypedDict):
    id: str
    type: str
    attributes: ObjectAttributes
    relationships: ObjectRelationships
    links: _Links


DiscosObjectList = List[DiscosObject]


class DiscosObjectListResponse(TypedDict):
    data: DiscosObjectList
    links: _Links
    meta: ResponsePagination


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
    EPOCH: Optional[str]
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
