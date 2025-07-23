from typing import (
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
