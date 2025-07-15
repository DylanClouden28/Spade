import argparse
import sys
from datetime import datetime

from drama import ares

# Assuming the USCDatabaseHelper is located in Spade/database/ as described.
from Spade.database import USCDatabaseHelper


import argparse
import sys
from datetime import datetime

from drama import ares

# Assuming the USCDatabaseHelper is located in Spade/database/ as described.
from Spade.database import USCDatabaseHelper


def run_ares_analysis(designator: str, risk_threshold: float):
    """
    Fetches satellite data, runs DRAMA ARES analysis, and prints the result.

    Args:
        designator (str): The international designator of the satellite.
        risk_threshold (float): The target collision probability level for the
                                maneuver criteria.
    """
    db_helper = USCDatabaseHelper()
    try:
        print(f"INFO: Querying database for satellite '{designator}'...")
        # Fetch the satellite data using the provided helper class
        # The result is a tuple of the database row.
        satellite_data = db_helper.get_usc_by_id(designator)

        if not satellite_data:
            print(
                f"ERROR: Satellite with ID '{designator}' not found in the database.",
                file=sys.stderr,
            )
            sys.exit(1)

        print("INFO: Satellite data found. Preparing ARES configuration.")

        # Map database columns to ARES parameters based on the table schema in
        # USCDatabaseHelper.
        # Key indices: inclination=9, ra_of_asc_node=10, eccentricity=11,
        # arg_of_perigee=12, semimajor_axis=20.
        ares_config = {
            "inclination": satellite_data[9],
            "rightAscensionOfTheAscendingNode": satellite_data[10],
            "eccentricity": satellite_data[11],
            "argumentOfPerigee": satellite_data[12],
            "semiMajorAxis": satellite_data[20],
        }

        # Validate that essential orbital parameters were found in the database
        for key, value in ares_config.items():
            if value is None:
                print(
                    f"ERROR: Record for '{designator}' is missing required orbital parameter '{key}'.",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Complete the configuration for a maneuver frequency estimation run
        ares_config.update(
            {
                "functionality": 4,  # 4 = Manoeuvre frequency estimation
                # --- THIS IS THE CORRECTED LINE ---
                # Set the date to match your installed ARES data files (e.g., cond_20161101_...).
                "analysisReferenceDate": datetime(2016, 11, 1),
                "targetCollisionProbabilityLevel": risk_threshold,
                # Provide sensible defaults for other required parameters
                "spacecraftMass": 1000,  # kg
                "spacecraftRadius": 2.0,  # m
            }
        )

        print(
            "INFO: Running DRAMA ARES analysis with reference date 2016-11-01. This may take a moment..."
        )
        results_data = ares.run(config=ares_config)

        # Process the results from the ARES run
        if results_data.get("errors"):
            print("ERROR: ARES run failed.", file=sys.stderr)
            for error in results_data["errors"]:
                print(f"  - Status: {error.get('status')}", file=sys.stderr)
                print(f"  - Log: {error.get('logfile')}", file=sys.stderr)
            sys.exit(1)

        if results_data.get("results"):
            # For functionality=4, the 'annual_collision_p' key holds the
            # estimated annual maneuver frequency.
            maneuver_frequency = results_data["results"][0].get("annual_collision_p")
            if maneuver_frequency is not None:
                print("\n--- ARES Analysis Complete ---")
                print(f"Maneuver Frequency (events/year): {maneuver_frequency}")
            else:
                print(
                    "ERROR: Analysis succeeded but could not find the maneuver frequency in the output.",
                    file=sys.stderr,
                )
                print(
                    f"Available result keys: {results_data['results'][0].keys()}",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            print("ERROR: ARES run completed but produced no results.", file=sys.stderr)
            sys.exit(1)

    finally:
        # Ensure the database connection is always closed
        db_helper.closeConnection()
        print("INFO: Database connection closed.")


def main():
    """
    Main function to parse command-line arguments and initiate the analysis.
    """
    parser = argparse.ArgumentParser(
        description="Calculate maneuver frequency for a satellite using DRAMA ARES and a USC database."
    )
    parser.add_argument(
        "international_designator",
        type=str,
        help="International designator of the satellite (e.g., '1998-067A').",
    )
    parser.add_argument(
        "risk_threshold",
        type=float,
        help="Target collision probability level to trigger a maneuver (e.g., 1e-4).",
    )
    args = parser.parse_args()

    run_ares_analysis(args.international_designator, args.risk_threshold)


if __name__ == "__main__":
    # This allows the script to be executed directly via the module flag.
    # Example: python3 -m Spade.drama_ares 1998-067A 1e-4
    main()
