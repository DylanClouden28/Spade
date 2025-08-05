import json
import sqlite3
import os

from Spade.models import USC
from Spade.database.models import GP, DiscosObjectDB, SatcatDebut, db

from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from peewee import (
    IntegrityError,
    fn,
    Model,
    DateTimeField,
    DateField,
    CompositeKey,
    IntegerField,
)

from Spade.spade_types import GpData, SatcatDebutData


class USCDatabaseHelper:

    def __init__(self, db_name="database.db") -> None:
        self.TABLE_NAME = "USC"
        self.DB_NAME = db_name
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, db_name)
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def _table_exists(self, table_name):
        """Checks if a table exists in the SQLite database."""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return self.cursor.fetchone() is not None

    def initializeTable(self):
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
            -- Core TLE Data
            INTERNATIONAL_DESIGNATOR TEXT PRIMARY KEY NOT NULL,
            SATELLITE_NAME TEXT,
            NORAD_CAT_ID TEXT,
            CLASSIFICATION TEXT CHECK(CLASSIFICATION IS NULL OR CLASSIFICATION IN ('U', 'C', 'S')),
            EPOCH TIMESTAMP,
            MEAN_MOTION_DOT REAL,
            MEAN_MOTION_DDOT REAL,
            B_STAR REAL,
            ELEMENT_SET_NUM INTEGER,
            INCLINATION REAL,
            RA_OF_ASC_NODE REAL,
            ECCENTRICITY REAL,
            ARG_OF_PERIGEE REAL,
            MEAN_ANOMALY REAL,
            MEAN_MOTION REAL,
            REV_AT_EPOCH INTEGER,
            EPHEMERIS_TYPE INTEGER,

            -- OMM Metadata
            CENTER_NAME TEXT,
            TIME_SYSTEM TEXT,
            MEAN_ELEMENT_THEORY TEXT,

            -- User Defined / Derived Parameters
            SEMIMAJOR_AXIS REAL,
            PERIOD REAL,
            APOAPSIS REAL,
            PERIAPSIS REAL,
            OBJECT_TYPE TEXT,
            RCS_SIZE TEXT CHECK(RCS_SIZE IS NULL OR RCS_SIZE IN ('SMALL', 'MEDIUM', 'LARGE')),
            COUNTRY_CODE TEXT,
            LAUNCH_DATE DATE,
            SITE TEXT,
            DECAY_DATE DATE,
            -- Additional Metadata
            DEBUT TIMESTAMP,

            -- Physical Characteristics
            DRY_MASS REAL,
            WET_MASS REAL,
            SHAPE TEXT,
            WIDTH REAL,
            HEIGHT REAL,
            DEPTH REAL,
            DIAMETER REAL,
            SPAN REAL,
            X_SECT_MAX REAL,
            X_SECT_MIN REAL,
            X_SECT_AVG REAL,
            MISSION_DESC TEXT,

            -- Sources of data (List stored as JSON Text)
            SOURCES TEXT
        );
        """
        self.cursor.execute(create_table_sql)
        self.saveDB()
        table_existed_before = self._table_exists(self.TABLE_NAME)
        if not table_existed_before:
            print(f"Table `{self.TABLE_NAME}` initialized successfully.")

    def insertUSC(self, usc_data: USC):

        # Combines json data on update
        sources_query = f"""
        (
            SELECT json_group_array(value)
            FROM (
                SELECT value FROM json_each(COALESCE({self.TABLE_NAME}.SOURCES, '[]'))
                UNION
                SELECT value FROM json_each(excluded.SOURCES)
            )
        )"""

        sql_query = f"""
        INSERT INTO {self.TABLE_NAME} (
            INTERNATIONAL_DESIGNATOR, SATELLITE_NAME, NORAD_CAT_ID, CLASSIFICATION,
            EPOCH, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, B_STAR, ELEMENT_SET_NUM,
            INCLINATION, RA_OF_ASC_NODE, ECCENTRICITY, ARG_OF_PERIGEE,
            MEAN_ANOMALY, MEAN_MOTION, REV_AT_EPOCH, EPHEMERIS_TYPE,
            CENTER_NAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, SEMIMAJOR_AXIS,
            PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE,
            LAUNCH_DATE, SITE, DECAY_DATE, DEBUT, DRY_MASS, WET_MASS, SHAPE, WIDTH,
            HEIGHT, DEPTH, DIAMETER, SPAN, X_SECT_MAX, X_SECT_MIN, X_SECT_AVG,
            MISSION_DESC, SOURCES
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?
        )
        ON CONFLICT(INTERNATIONAL_DESIGNATOR) DO UPDATE SET
            SATELLITE_NAME = COALESCE({self.TABLE_NAME}.SATELLITE_NAME, excluded.SATELLITE_NAME),
            NORAD_CAT_ID = COALESCE({self.TABLE_NAME}.NORAD_CAT_ID, excluded.NORAD_CAT_ID),
            CLASSIFICATION = COALESCE({self.TABLE_NAME}.CLASSIFICATION, excluded.CLASSIFICATION),
            EPOCH = COALESCE({self.TABLE_NAME}.EPOCH, excluded.EPOCH),
            MEAN_MOTION_DOT = COALESCE({self.TABLE_NAME}.MEAN_MOTION_DOT, excluded.MEAN_MOTION_DOT),
            MEAN_MOTION_DDOT = COALESCE({self.TABLE_NAME}.MEAN_MOTION_DDOT, excluded.MEAN_MOTION_DDOT),
            B_STAR = COALESCE({self.TABLE_NAME}.B_STAR, excluded.B_STAR),
            ELEMENT_SET_NUM = COALESCE({self.TABLE_NAME}.ELEMENT_SET_NUM, excluded.ELEMENT_SET_NUM),
            INCLINATION = COALESCE({self.TABLE_NAME}.INCLINATION, excluded.INCLINATION),
            RA_OF_ASC_NODE = COALESCE({self.TABLE_NAME}.RA_OF_ASC_NODE, excluded.RA_OF_ASC_NODE),
            ECCENTRICITY = COALESCE({self.TABLE_NAME}.ECCENTRICITY, excluded.ECCENTRICITY),
            ARG_OF_PERIGEE = COALESCE({self.TABLE_NAME}.ARG_OF_PERIGEE, excluded.ARG_OF_PERIGEE),
            MEAN_ANOMALY = COALESCE({self.TABLE_NAME}.MEAN_ANOMALY, excluded.MEAN_ANOMALY),
            MEAN_MOTION = COALESCE({self.TABLE_NAME}.MEAN_MOTION, excluded.MEAN_MOTION),
            REV_AT_EPOCH = COALESCE({self.TABLE_NAME}.REV_AT_EPOCH, excluded.REV_AT_EPOCH),
            EPHEMERIS_TYPE = COALESCE({self.TABLE_NAME}.EPHEMERIS_TYPE, excluded.EPHEMERIS_TYPE),
            CENTER_NAME = COALESCE({self.TABLE_NAME}.CENTER_NAME, excluded.CENTER_NAME),
            TIME_SYSTEM = COALESCE({self.TABLE_NAME}.TIME_SYSTEM, excluded.TIME_SYSTEM),
            MEAN_ELEMENT_THEORY = COALESCE({self.TABLE_NAME}.MEAN_ELEMENT_THEORY, excluded.MEAN_ELEMENT_THEORY),
            SEMIMAJOR_AXIS = COALESCE({self.TABLE_NAME}.SEMIMAJOR_AXIS, excluded.SEMIMAJOR_AXIS),
            PERIOD = COALESCE({self.TABLE_NAME}.PERIOD, excluded.PERIOD),
            APOAPSIS = COALESCE({self.TABLE_NAME}.APOAPSIS, excluded.APOAPSIS),
            PERIAPSIS = COALESCE({self.TABLE_NAME}.PERIAPSIS, excluded.PERIAPSIS),
            OBJECT_TYPE = COALESCE({self.TABLE_NAME}.OBJECT_TYPE, excluded.OBJECT_TYPE),
            RCS_SIZE = COALESCE({self.TABLE_NAME}.RCS_SIZE, excluded.RCS_SIZE),
            COUNTRY_CODE = COALESCE({self.TABLE_NAME}.COUNTRY_CODE, excluded.COUNTRY_CODE),
            LAUNCH_DATE = COALESCE({self.TABLE_NAME}.LAUNCH_DATE, excluded.LAUNCH_DATE),
            SITE = COALESCE({self.TABLE_NAME}.SITE, excluded.SITE),
            DECAY_DATE = COALESCE({self.TABLE_NAME}.DECAY_DATE, excluded.DECAY_DATE),
            DEBUT = COALESCE({self.TABLE_NAME}.DEBUT, excluded.DEBUT),
            DRY_MASS = COALESCE({self.TABLE_NAME}.DRY_MASS, excluded.DRY_MASS),
            WET_MASS = COALESCE({self.TABLE_NAME}.WET_MASS, excluded.WET_MASS),
            SHAPE = COALESCE({self.TABLE_NAME}.SHAPE, excluded.SHAPE),
            WIDTH = COALESCE({self.TABLE_NAME}.WIDTH, excluded.WIDTH),
            HEIGHT = COALESCE({self.TABLE_NAME}.HEIGHT, excluded.HEIGHT),
            DEPTH = COALESCE({self.TABLE_NAME}.DEPTH, excluded.DEPTH),
            DIAMETER = COALESCE({self.TABLE_NAME}.DIAMETER, excluded.DIAMETER),
            SPAN = COALESCE({self.TABLE_NAME}.SPAN, excluded.SPAN),
            X_SECT_MAX = COALESCE({self.TABLE_NAME}.X_SECT_MAX, excluded.X_SECT_MAX),
            X_SECT_MIN = COALESCE({self.TABLE_NAME}.X_SECT_MIN, excluded.X_SECT_MIN),
            X_SECT_AVG = COALESCE({self.TABLE_NAME}.X_SECT_AVG, excluded.X_SECT_AVG),
            MISSION_DESC = COALESCE({self.TABLE_NAME}.MISSION_DESC, excluded.MISSION_DESC),
            SOURCES = {sources_query}
        """
        data_tuple = (
            usc_data.INTERNATIONAL_DESIGNATOR,
            usc_data.SATELLITE_NAME,
            usc_data.NORAD_CAT_ID,
            usc_data.CLASSIFICATION,
            usc_data.EPOCH,
            usc_data.MEAN_MOTION_DOT,
            usc_data.MEAN_MOTION_DDOT,
            usc_data.B_STAR,
            usc_data.ELEMENT_SET_NUM,
            usc_data.INCLINATION,
            usc_data.RA_OF_ASC_NODE,
            usc_data.ECCENTRICITY,
            usc_data.ARG_OF_PERIGEE,
            usc_data.MEAN_ANOMALY,
            usc_data.MEAN_MOTION,
            usc_data.REV_AT_EPOCH,
            usc_data.EPHEMERIS_TYPE,
            usc_data.CENTER_NAME,
            usc_data.TIME_SYSTEM,
            usc_data.MEAN_ELEMENT_THEORY,
            usc_data.SEMIMAJOR_AXIS,
            usc_data.PERIOD,
            usc_data.APOAPSIS,
            usc_data.PERIAPSIS,
            usc_data.OBJECT_TYPE,
            usc_data.RCS_SIZE,
            usc_data.COUNTRY_CODE,
            usc_data.LAUNCH_DATE,
            usc_data.SITE,
            usc_data.DECAY_DATE,
            usc_data.DEBUT,
            usc_data.DRY_MASS,
            usc_data.WET_MASS,
            usc_data.SHAPE,
            usc_data.WIDTH,
            usc_data.HEIGHT,
            usc_data.DEPTH,
            usc_data.DIAMETER,
            usc_data.SPAN,
            usc_data.X_SECT_MAX,
            usc_data.X_SECT_MIN,
            usc_data.X_SECT_AVG,
            usc_data.MISSION_DESC,
            json.dumps(usc_data.SOURCES),  # Serialize list to JSON string
        )
        try:
            self.cursor.execute(sql_query, data_tuple)
            # print(f"Successfully inserted USC: {usc_data.INTERNATIONAL_DESIGNATOR}")

        except sqlite3.IntegrityError as e:
            print(
                f"Error: Integrity constraint violated for {usc_data.INTERNATIONAL_DESIGNATOR}. It might already exist. Details: {e}"
            )

        except sqlite3.OperationalError as e:
            print(f"Error: Operational issue when adding USC - {e}")

        except Exception as e:
            print(f"An unexpected error occurred when adding USC: {e}")

    def bulkInsertUSC(self, usc_data_list: list[USC]):
        print("Inserting usc data")
        uscSet = set()
        for idx, usc in enumerate(usc_data_list):
            id = usc.INTERNATIONAL_DESIGNATOR
            if (idx % 1000) == 0:
                print(f"\tInserted {idx}/{len(usc_data_list)}")
            if id == "UNKNOWN" or id in uscSet:
                continue
            self.insertUSC(usc)
            uscSet.add(id)
        self.saveDB()  # Save inserts
        print("Finished bulk insert")

    def get_usc_by_id(self, international_designator: str):
        """Retrieves a single spacecraft's data by its international designator."""
        query = f"SELECT * FROM {self.TABLE_NAME} WHERE INTERNATIONAL_DESIGNATOR = ?"
        self.cursor.execute(query, (international_designator,))
        return self.cursor.fetchone()

    def saveDB(self):
        self.connection.commit()

    def closeConnection(self):
        self.connection.close()


def initialize_database():
    """Initialize all database tables defined by the models."""
    db.connect()
    db.create_tables([GP, SatcatDebut], safe=True)
    db.close()


def insert_gp_data(gp_data_list: List[GpData]) -> None:
    """
    Bulk-insert a list of GpData objects into the GP table.
    """
    bulk_insert_data(GP, gp_data_list)


def insert_satcat_debut_data(debut_data_list: List[SatcatDebutData]) -> None:
    """
    Bulk-insert a list of SatcatDebutData objects into the SATCAT_DEBUT table.
    """
    print(f"Starting insertion of {len(debut_data_list)} SatcatDebut records")

    # Count records before insertion
    count_before = SatcatDebut.select().count()
    print(f"Records in database before insertion: {count_before}")

    # Check a sample record for type issues
    if debut_data_list:
        sample = debut_data_list[0]
        print("Sample record types:")
        for key, value in sample.items():
            print(f"  {key}: {value} (type: {type(value).__name__})")

    # Convert string values to integers for specific fields
    print("Converting data types...")
    converted_data = []
    conversion_errors = 0

    for record in debut_data_list:
        try:
            # Create a new record with converted types
            new_record = record.copy()

            # Convert string fields that should be integers
            int_fields = [
                "NORAD_CAT_ID",
                "COMMENTCODE",
                "RCSVALUE",
                "FILE",
                "LAUNCH_YEAR",
                "LAUNCH_NUM",
                "OBJECT_NUMBER",
            ]

            for field in int_fields:
                if field in new_record and new_record[field] is not None:
                    try:
                        new_record[field] = int(new_record[field])
                    except (ValueError, TypeError):
                        print(
                            f"Warning: Could not convert {field} value '{new_record[field]}' to integer"
                        )
                        conversion_errors += 1

            # Convert float fields
            float_fields = ["PERIOD", "INCLINATION"]

            for field in float_fields:
                if field in new_record and new_record[field] is not None:
                    try:
                        new_record[field] = float(new_record[field])
                    except (ValueError, TypeError):
                        print(
                            f"Warning: Could not convert {field} value '{new_record[field]}' to float"
                        )
                        conversion_errors += 1

            converted_data.append(new_record)
        except Exception as e:
            print(f"Error converting record: {e}")
            conversion_errors += 1

    print(f"Data conversion completed with {conversion_errors} errors")
    print(f"Converted {len(converted_data)} records for insertion")

    # Try to insert with explicit unique field
    print("Starting bulk insert with replace action...")
    try:
        bulk_insert_data(SatcatDebut, converted_data, conflict_action="replace")
    except Exception as e:
        print(f"Error during bulk insert: {e}")
        import traceback

        traceback.print_exc()

    # Count records after insertion
    count_after = SatcatDebut.select().count()
    print(f"Records in database after insertion: {count_after}")
    print(f"Actually inserted: {count_after - count_before} new records")


def bulk_insert_data(
    model: Type[Model],
    data_list: List[Any],
    conflict_action: str = "ignore",
    batch_size: int = 100,
) -> None:
    """
    Generic bulk insert function for Peewee models with automatic field type detection.
    """
    if not data_list:
        return

    # Automatically detect field types
    date_fields = []
    datetime_fields = []
    integer_fields = []  # Add this for integer fields

    for field_name, field in model._meta.fields.items():
        if isinstance(field, DateField):
            date_fields.append(field_name)
        elif isinstance(field, DateTimeField):
            datetime_fields.append(field_name)
        elif isinstance(field, IntegerField):  # Check for IntegerField
            integer_fields.append(field_name)

    # Explicitly use FILE as the unique field for SatcatDebut model
    if model.__name__ == "SatcatDebut":
        unique_field = "FILE"
    else:
        unique_field = _get_unique_field(model)

    print(f"Using unique field: {unique_field}")
    print(f"Date fields: {date_fields}")
    print(f"Datetime fields: {datetime_fields}")
    print(f"Integer fields: {integer_fields}")

    rows = []
    skipped_count = 0

    for item in data_list:
        try:
            row = {}
            for field_name, value in item.items():
                if field_name in date_fields:
                    row[field_name] = _safe_iso_to_date(value)
                elif field_name in datetime_fields:
                    row[field_name] = _safe_iso_to_datetime(value)
                elif field_name in integer_fields and value is not None:
                    # Convert string to integer if possible
                    try:
                        row[field_name] = int(value)
                    except (ValueError, TypeError):
                        print(
                            f"Warning: Could not convert {field_name} value '{value}' to integer"
                        )
                        row[field_name] = value  # Keep as string if conversion fails
                else:
                    row[field_name] = value
            rows.append(row)
        except Exception as e:
            print(f"Error processing record: {e}")
            skipped_count += 1

    print(
        f"Prepared {len(rows)} rows for insertion, skipped {skipped_count} due to errors"
    )

    with model._meta.database.atomic():
        for i, batch in enumerate(chunked(rows, batch_size)):
            try:
                query = model.insert_many(batch)

                if unique_field:
                    if conflict_action == "replace":
                        query = query.on_conflict_replace()
                    else:
                        query = query.on_conflict_ignore()

                result = query.execute()
                print(f"Batch {i+1}: Inserted {len(batch)} records")
            except Exception as e:
                print(f"Error inserting batch {i+1}: {e}")
                # Try to insert records one by one to identify problematic ones
                for j, record in enumerate(batch):
                    try:
                        query = model.insert(**record)
                        if unique_field:
                            if conflict_action == "replace":
                                query = query.on_conflict_replace()
                            else:
                                query = query.on_conflict_ignore()
                        query.execute()
                    except Exception as e2:
                        print(f"Error inserting record {j} in batch {i+1}: {e2}")
                        print(f"Record data: {record}")


def insert_discos_data(discos_data_list: List[DiscosObject]) -> None:
    """
    Prepares and bulk-inserts a list of DiscosObject dictionaries into the
    DiscosObjectDB table.

    This function transforms the nested API response into a flat structure
    suitable for the Peewee model before calling the generic bulk inserter.
    """
    if not discos_data_list:
        print("No DISCOS data to insert.")
        return

    print(f"Preparing to insert {len(discos_data_list)} DISCOS object records.")

    # The API data is nested. We need to flatten it to match the model.
    # The model fields are derived from `item['attributes']`, plus the
    # top-level `id` and `relationships`.
    processed_data = []
    for item in discos_data_list:
        # Start with the attributes dictionary
        row_data = item.get("attributes", {})

        # Add the top-level fields
        row_data["id"] = item.get("id")
        row_data["relationships"] = item.get("relationships")

        # Ensure the primary key 'id' is present
        if not row_data["id"]:
            print(f"Skipping record due to missing 'id': {item}")
            continue

        processed_data.append(row_data)

    print(f"Processed {len(processed_data)} records for insertion.")

    # Use the generic bulk insert function.
    # 'replace' is a good strategy here, as it will update records if they
    # are fetched again with new information, using the 'id' primary key.
    bulk_insert_data(DiscosObjectDB, processed_data, conflict_action="replace")

    print("Finished inserting DISCOS data.")


# --------------------------------------------------------------------------- #
# Helper utilities
# --------------------------------------------------------------------------- #
from datetime import datetime, date
from typing import Union


def _get_unique_field(model: Type[Model]) -> Optional[str]:
    """
    Find the first unique field in a model for conflict resolution.

    Parameters
    ----------
    model : Type[Model]
        The Peewee model to inspect

    Returns
    -------
    Optional[str]
        Name of the first unique field found, or None if none exists
    """
    # Check for primary key
    pk = model._meta.primary_key
    if not isinstance(pk, CompositeKey) and pk is not None:
        return pk.name

    # Look for fields with unique=True
    for field in model._meta.fields.values():
        if field.unique:
            return field.name

    return None


def _safe_iso_to_datetime(value: Optional[str]) -> Optional[datetime]:
    """Convert ISO-8601 string to datetime; return None on failure."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _safe_iso_to_date(value: Optional[str]) -> Optional[date]:
    """Convert ISO-8601 string to date; return None on failure."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except (ValueError, TypeError):
        return None


def chunked(iterable, n):
    """Yield successive n-sized chunks from iterable."""
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]
