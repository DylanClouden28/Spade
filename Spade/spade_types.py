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
