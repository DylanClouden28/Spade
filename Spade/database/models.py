from datetime import datetime
import json
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
)

"""
This file contains the models that define the database structure for sqlite.

The package 'peewee' is used as its an ORM which allows the database to be used as if it were a python object. 

The database structure is defined with classes that extend/inherit properties from 'peewee'. 

The main table that is used is called 'USC' which is Universal Satellite Characteristics. The USC table has information from space track (US space force) and DISCOS (ESA)
"""


# Initialize the database connection.
db = SqliteDatabase("database.db")


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
