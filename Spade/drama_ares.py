import argparse
import sqlite3
import os
from datetime import datetime
from math import pi, sqrt
from typing import Optional
from Spade.database import USCDatabaseHelper, USC

try:
    from drama import ares
except ImportError:
    print(
        "Error: The 'drama' library is not installed. "
        "Please install it to run this script."
    )
    print("See installation instructions for the DRAMA software suite.")
    exit(1)


def calculate_maneuver_frequency(
    international_designator: str,
    accepted_risk: float,
    project: Optional[str] = None,
    db_path: str = "database/usc.db",
):
    """
    Calculates the collision avoidance maneuver frequency for a given spacecraft
    and an accepted risk level using the DRAMA ARES tool.

    This function fetches spacecraft data, prepares a DRAMA ARES configuration,
    runs the analysis, and prints the resulting expected number of maneuvers
    per year.

    Args:
        international_designator: The international designator of the spacecraft.
        accepted_risk: The project-specific accepted risk level (target
                       collision probability).
        project: Optional path to a DRAMA project to use as a baseline.
        db_path: Path to the USC SQLite database file.
    """
    print(
        "--- Starting Maneuver Frequency Calculation for"
        f" {international_designator} ---"
    )
    db_helper = USCDatabaseHelper(db_name=db_path)

    # 1. Fetch spacecraft data from the database
    print(f"Querying database for spacecraft data...")
    sc_data = db_helper.get_usc_by_id(international_designator)

    if not sc_data:
        print(
            "Error: Spacecraft with ID"
            f" '{international_designator}' not found in the database."
        )
        db_helper.closeConnection()
        return

    print("Spacecraft data found.")

    # 2. Get the base configuration from ARES
    config = ares.get_basic_config(project=project)

    # 3. Update config with spacecraft data and user inputs
    print("Preparing ARES configuration...")
    # --- Orbital Parameters ---
    required_params = [
        "SEMIMAJOR_AXIS",
        "ECCENTRICITY",
        "INCLINATION",
        "RA_OF_ASC_NODE",
        "ARG_OF_PERIGEE",
    ]
    for param in required_params:
        if sc_data[param] is None:
            print(f"Error: Missing required orbital parameter '{param}' in database.")
            db_helper.closeConnection()
            return

    config["semiMajorAxis"] = sc_data["SEMIMAJOR_AXIS"]
    config["eccentricity"] = sc_data["ECCENTRICITY"]
    config["inclination"] = sc_data["INCLINATION"]
    config["rightAscensionOfTheAscendingNode"] = sc_data["RA_OF_ASC_NODE"]
    config["argumentOfPerigee"] = sc_data["ARG_OF_PERIGEE"]
    config["analysisReferenceDate"] = datetime.now()

    # --- Physical Characteristics (with defaults) ---
    mass = sc_data["WET_MASS"] or sc_data["DRY_MASS"] or 1000.0  # Default: 1000 kg
    config["spacecraftMass"] = mass

    # Estimate radius: Use diameter if available, otherwise estimate from dimensions
    if sc_data["DIAMETER"] is not None:
        radius = sc_data["DIAMETER"] / 2
    elif all(sc_data[k] is not None for k in ["WIDTH", "HEIGHT", "DEPTH"]):
        w, h, d = sc_data["WIDTH"], sc_data["HEIGHT"], sc_data["DEPTH"]
        surface_area = 2 * (w * h + w * d + h * d)
        radius = sqrt(surface_area / (4 * pi))
    else:
        radius = 1.0  # Default: 1.0 meter
    config["spacecraftRadius"] = radius

    # --- Analysis Parameters ---
    # Set the criteria to use the target collision probability.
    config["avoidanceManoeuvreCriteria"] = 1
    config["targetCollisionProbabilityLevel"] = accepted_risk

    # 4. Run the ARES analysis
    print("Running ARES analysis... (This may take a moment)")
    results_data = ares.run(config=config)
    db_helper.closeConnection()

    # 5. Process and display the results
    print("--- Analysis Complete ---")
    if results_data["errors"]:
        print("Error(s) occurred during the ARES run:")
        for error in results_data["errors"]:
            print(f"  - Status: {error.get('status')}")
            print(f"  - Output: {error.get('output')}")
        return

    if results_data["results"]:
        final_result = results_data["results"][0]
        # The 'annual_collision_p' represents the rate of events exceeding the
        # risk threshold, which is the expected maneuver frequency.
        maneuver_freq = final_result["annual_collision_p"]
        print(f"Spacecraft: {international_designator} ({sc_data['SATELLITE_NAME']})")
        print(f"Accepted Risk (Target Pc): {accepted_risk:.2e}")
        print(
            "\n>>> Estimated Avoidance Maneuver Frequency: "
            f"{maneuver_freq:.4f} maneuvers/year <<<"
        )
    else:
        print("ARES run completed, but no results were returned.")


def _setup_test_database(db_path):
    """Helper function to create and populate the database with a test entry."""
    print(f"Setting up test database at: {db_path}")
    # This will initialize the table if it doesn't exist
    db_helper = USCDatabaseHelper(db_name=db_path)
    conn = db_helper.connection
    cur = db_helper.cursor

    # Data for the International Space Station (ISS)
    mock_data = {
        "INTERNATIONAL_DESIGNATOR": "1998-067A",
        "SATELLITE_NAME": "ISS",
        "NORAD_CAT_ID": "25544",
        "CLASSIFICATION": "U",
        "EPOCH": "2024-01-01T00:00:00",
        "MEAN_MOTION_DOT": 0.0,
        "MEAN_MOTION_DDOT": 0.0,
        "B_STAR": 0.0001,
        "ELEMENT_SET_NUM": 999,
        "INCLINATION": 51.6,
        "RA_OF_ASC_NODE": 120.0,
        "ECCENTRICITY": 0.001,
        "ARG_OF_PERIGEE": 45.0,
        "MEAN_ANOMALY": 315.0,
        "MEAN_MOTION": 15.49,
        "REV_AT_EPOCH": 12345,
        "EPHEMERIS_TYPE": 0,
        "CENTER_NAME": "JSC",
        "TIME_SYSTEM": "UTC",
        "MEAN_ELEMENT_THEORY": "SGP4",
        "SEMIMAJOR_AXIS": 6778.0,
        "PERIOD": 92.6,
        "APOAPSIS": 420.0,
        "PERIAPSIS": 410.0,
        "OBJECT_TYPE": "PAYLOAD",
        "RCS_SIZE": "LARGE",
        "COUNTRY_CODE": "US",
        "LAUNCH_DATE": "1998-11-20",
        "SITE": "KSC",
        "DECAY_DATE": None,
        "DEBUT": "1998-11-20T00:00:00",
        "DRY_MASS": 100000.0,
        "WET_MASS": 450000.0,
        "SHAPE": "COMPLEX",
        "WIDTH": 73.0,
        "HEIGHT": 27.0,
        "DEPTH": 109.0,
        "DIAMETER": None,
        "SPAN": 109.0,
        "X_SECT_MAX": 2997.0,
        "X_SECT_MIN": 2500.0,
        "X_SECT_AVG": 2750.0,
        "MISSION_DESC": "International Space Station",
        "SOURCES": '["space-track.org"]',
    }

    columns = ", ".join(mock_data.keys())
    placeholders = ", ".join(["?"] * len(mock_data))
    sql = (
        f"INSERT OR REPLACE INTO {db_helper.TABLE_NAME} ({columns}) VALUES"
        f" ({placeholders})"
    )
    cur.execute(sql, tuple(mock_data.values()))
    conn.commit()
    db_helper.closeConnection()
    print("Mock data for '1998-067A' (ISS) inserted.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Calculate collision avoidance maneuver frequency for a spacecraft "
            "using DRAMA ARES."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "satellite_id",
        nargs="?",
        default=None,
        type=str,
        help="International Designator of the satellite (e.g., '1998-067A').",
    )
    parser.add_argument(
        "risk_level",
        nargs="?",
        default=None,
        type=float,
        help="Project-specific accepted risk level (e.g., 1e-4).",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Optional path to a DRAMA project to use as a baseline.",
    )
    parser.add_argument(
        "--db_path",
        type=str,
        default="database/usc.db",
        help="Path to the USC SQLite database file (default: database/usc.db).",
    )
    parser.add_argument(
        "--setup_db",
        action="store_true",
        help=(
            "A flag to set up and populate the database with a test entry (ISS).\n"
            "If this flag is used, no calculation will be performed."
        ),
    )

    args = parser.parse_args()

    if args.setup_db:
        _setup_test_database(args.db_path)
        print("\nDatabase setup complete. You can now run the calculation.")
        print(
            "Example: python maneuver_calculator.py 1998-067A 0.0001 "
            f"--db_path {args.db_path}\n"
        )
    elif args.satellite_id and args.risk_level:
        calculate_maneuver_frequency(
            international_designator=args.satellite_id,
            accepted_risk=args.risk_level,
            project=args.project,
            db_path=args.db_path,
        )
    else:
        parser.print_help()
        print(
            "\nError: Please provide satellite_id and risk_level, or use the"
            " --setup_db flag."
        )
