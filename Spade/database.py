import json
import sqlite3
import os

from Spade.models import USC


class USCDatabaseHelper:

    def __init__(self, db_name="database/database.db") -> None:
        self.TABLE_NAME = "USC"
        self.DB_NAME = db_name
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, db_name)
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

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
        print(f"Table `{self.TABLE_NAME}` initialized succesfully.")

    def insertUSC(self, usc_data: USC):
        sql_query = f"""
        INSERT INTO {self.TABLE_NAME} (
            INTERNATIONAL_DESIGNATOR, SATELLITE_NAME, NORAD_CAT_ID, CLASSIFICATION,
            EPOCH, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, B_STAR, ELEMENT_SET_NUM,
            INCLINATION, RA_OF_ASC_NODE, ECCENTRICITY, ARG_OF_PERIGEE,
            MEAN_ANOMALY, MEAN_MOTION, REV_AT_EPOCH, EPHEMERIS_TYPE,
            CENTER_NAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, SEMIMAJOR_AXIS,
            PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE,
            LAUNCH_DATE, SITE, DECAY_DATE, DRY_MASS, WET_MASS, SHAPE, WIDTH,
            HEIGHT, DEPTH, DIAMETER, SPAN, X_SECT_MAX, X_SECT_MIN, X_SECT_AVG,
            MISSION_DESC, SOURCES
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?
        )
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

    def saveDB(self):
        self.connection.commit()

    def closeConnection(self):
        self.connection.close()
