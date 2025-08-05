from datetime import datetime
import json
import os
from peewee import (
    Model,
    SqliteDatabase,
    CharField,
    TextField,
    DateTimeField,
    FloatField,
    IntegerField,
    DateField,
    Check,
    BooleanField,
)

"""
This file contains the models that define the database structure for sqlite.

The package 'peewee' is used as its an ORM which allows the database to be used as if it were a python object. 

The database structure is defined with classes that extend/inherit properties from 'peewee'. 

The main table that is used is called 'USC' which is Universal Satellite Characteristics. The USC table has information from space track (US space force) and DISCOS (ESA)
"""


# Initialize the database connection.
dirname = os.path.dirname(__file__)
# Join with the database file name
filename = os.path.join(dirname, "database.db")
db = SqliteDatabase(filename)


# Custom Field for JSON data
# This handles the serialization/deserialization automatically.
class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)
        return None


# Define the base model.
# All other models will inherit from this, as they use the same DB.
class BaseModel(Model):
    class Meta:
        database = db


class GP(BaseModel):
    """
    General Perturbation (GP) data model for Space-Track.org OMM JSON responses.
    Maps directly to the GpData TypedDict structure with an additional
    'created_at' timestamp field.
    """

    # --- Other Data (OMM Header and Derived Properties) ---
    CCSDS_OMM_VERS = CharField()
    COMMENT = TextField()
    CREATION_DATE = DateTimeField(null=True)
    ORIGINATOR = CharField()
    OBJECT_NAME = CharField(null=True)
    OBJECT_ID = CharField(null=True)  # e.g., International Designator like '98067A'
    CENTER_NAME = CharField()
    REF_FRAME = CharField()
    TIME_SYSTEM = CharField()
    MEAN_ELEMENT_THEORY = CharField()

    # --- TLE Data (Raw Lines and Parsed Elements) ---
    # Raw TLE Lines
    TLE_LINE0 = CharField(null=True)  # Satellite Name/Common Name
    TLE_LINE1 = CharField(null=True)  # Raw TLE Line 1 string
    TLE_LINE2 = CharField(null=True)  # Raw TLE Line 2 string

    # Parsed TLE Elements
    NORAD_CAT_ID = IntegerField(index=True)
    CLASSIFICATION_TYPE = CharField(
        null=True, constraints=[Check("CLASSIFICATION_TYPE IN ('U', 'C', 'S')")]
    )
    EPOCH = CharField(null=True)  # Epoch year and day of year
    MEAN_MOTION_DOT = FloatField(null=True)  # First derivative of mean motion
    MEAN_MOTION_DDOT = FloatField(null=True)  # Second derivative of mean motion
    BSTAR = FloatField(null=True)  # B* drag term
    EPHEMERIS_TYPE = IntegerField(null=True)  # Typically 0
    ELEMENT_SET_NO = IntegerField(null=True)  # Incremented when a new TLE is generated

    INCLINATION = FloatField(null=True)  # Inclination in degrees
    RA_OF_ASC_NODE = FloatField(
        null=True
    )  # Right Ascension of Ascending Node in degrees
    ECCENTRICITY = FloatField(null=True)  # Eccentricity, decimal point assumed
    ARG_OF_PERICENTER = FloatField(null=True)  # Argument of Perigee in degrees
    MEAN_ANOMALY = FloatField(null=True)  # Mean Anomaly in degrees
    MEAN_MOTION = FloatField(null=True)  # Mean Motion in revolutions per day
    REV_AT_EPOCH = IntegerField(null=True)  # Revolution number at epoch

    # --- Other Data (Additional Object Properties & Database IDs) ---
    SEMIMAJOR_AXIS = FloatField(null=True)  # Derived (from Mean Motion)
    PERIOD = FloatField(null=True)  # Derived (from Mean Motion)
    APOAPSIS = FloatField(null=True)  # Derived (from Eccentricity, Semimajor Axis)
    PERIAPSIS = FloatField(null=True)  # Derived (from Eccentricity, Semimajor Axis)
    OBJECT_TYPE = CharField(null=True)
    RCS_SIZE = CharField(
        null=True, constraints=[Check("RCS_SIZE IN ('SMALL', 'MEDIUM', 'LARGE')")]
    )
    COUNTRY_CODE = CharField(null=True)
    LAUNCH_DATE = DateField(null=True)
    SITE = CharField(null=True)  # Launch Site
    DECAY_DATE = DateField(null=True)
    FILE = IntegerField(null=True)  # Space-Track.org specific ID
    GP_ID = IntegerField(unique=True)  # Space-Track.org specific GP ID

    # --- Additional Fields ---
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "GP"


class SatcatDebut(BaseModel):
    """
    Satellite Catalog Debut data model for Space-Track.org satcat_debut endpoint.
    Maps directly to the SatcatDebutData TypedDict structure.
    """

    # Basic identification fields
    INTLDES = CharField()  # International Designator
    NORAD_CAT_ID = IntegerField(null=True, index=True)
    OBJECT_TYPE = CharField(null=True)
    SATNAME = CharField()
    DEBUT = DateField(null=True)  # Debut date
    COUNTRY = CharField()
    LAUNCH = DateField(null=True)  # Launch date
    SITE = CharField(null=True)  # Launch site
    DECAY = DateField(null=True)  # Decay date

    # Orbital parameters
    PERIOD = FloatField(null=True)  # Orbital period in minutes
    INCLINATION = FloatField(null=True)  # Inclination in degrees
    APOGEE = IntegerField(null=True)  # Apogee in kilometers
    PERIGEE = IntegerField(null=True)  # Perigee in kilometers

    # Additional information
    COMMENT = TextField(null=True)
    COMMENTCODE = IntegerField(null=True)
    RCSVALUE = IntegerField()  # Radar Cross Section value
    RCS_SIZE = CharField(
        null=True, constraints=[Check("RCS_SIZE IN ('SMALL', 'MEDIUM', 'LARGE')")]
    )
    FILE = IntegerField(unique=True)  # Space-Track.org specific ID

    # Launch information
    LAUNCH_YEAR = IntegerField()
    LAUNCH_NUM = IntegerField()
    LAUNCH_PIECE = CharField()

    # Current status
    CURRENT = CharField()

    # Object identification
    OBJECT_NAME = CharField()
    OBJECT_ID = CharField()
    OBJECT_NUMBER = IntegerField(null=True)

    # Additional fields
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "SATCAT_DEBUT"


class DiscosObjectDB(BaseModel):
    """
    Peewee model for storing data from the ESA DISCOS API `objects` endpoint.
    This model is based on the `DiscosObject` TypedDict structure.
    """

    # The unique ID from DISCOS API, used as the primary key.
    id = CharField(primary_key=True)

    # --- Fields from ObjectAttributes ---
    cosparId = CharField(null=True, index=True)  # International Designator
    vimpelId = IntegerField(null=True)
    satno = IntegerField(null=True, index=True)  # NORAD Catalog Number
    name = CharField(null=True)
    objectClass = CharField(null=True)
    mass = FloatField(null=True)  # In kg
    shape = CharField(null=True)
    width = FloatField(null=True)  # In meters
    height = FloatField(null=True)  # In meters
    depth = FloatField(null=True)  # In meters
    diameter = FloatField(null=True)  # In meters
    span = FloatField(null=True)  # In meters
    xSectMax = FloatField(null=True)  # In m^2
    xSectMin = FloatField(null=True)  # In m^2
    xSectAvg = FloatField(null=True)  # In m^2
    firstEpoch = DateTimeField(null=True)
    mission = TextField(null=True)
    predDecayDate = DateTimeField(null=True)
    active = BooleanField(null=True)
    cataloguedFragments = IntegerField(null=True)
    onOrbitCataloguedFragments = IntegerField(null=True)

    # --- Fields from top-level DiscosObject ---
    # Store the complex relationships object as a JSON string for flexibility.
    relationships = JSONField(null=True)

    # --- Additional Fields ---
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "DISCOS_OBJECTS"
