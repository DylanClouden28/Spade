import argparse
import math
import os

os.environ["MASTER_HOME"] = "/home/dylan/MASTER-8.0.5"
from pathlib import Path
import sys
from datetime import datetime

from drama import ares


import argparse
import sys
from datetime import datetime

from drama import ares

from Spade.database.database import get_sat_by_designator


def effective_radius_from_area_m2(area_m2: float) -> float:
    # ARES expects spacecraftRadius in meters (circular-equivalent area)
    # r_eff = sqrt(A / pi)
    return math.sqrt(area_m2 / math.pi)


def build_ares_config_from_satellite(
    satellite_data: dict,
    analysis_date: datetime = datetime(2024, 8, 1),  # matches cond_202408
    horizon_days: float = 5.0,  # predictionToEventTime (0 < days <= 7)
    use_pc_policy: bool = True,
    pc_threshold: float = 1e-4,  # targetCollisionProbabilityLevel
    miss_distance_km: float | None = None,  # if miss-distance policy
    sc_cov_km: tuple[float, float, float] = (1.0, 0.2, 0.2),  # AT, CT, R (km)
    catalog_scale: float = 1.3,  # globalUncertaintyScalingFactor
) -> dict:
    # Orbit (km, deg)
    cfg = {
        "semiMajorAxis": float(satellite_data["SEMIMAJOR_AXIS"]),
        "eccentricity": float(satellite_data["ECCENTRICITY"]),
        "inclination": float(satellite_data["INCLINATION"]),
        "rightAscensionOfTheAscendingNode": float(satellite_data["RA_OF_ASC_NODE"]),
        "argumentOfPerigee": float(satellite_data["ARG_OF_PERICENTER"]),
    }
    # Spacecraft props
    mass = float(satellite_data.get("mass", 260.0))  # kg
    xsect_avg = satellite_data.get("xSectAvg")
    if xsect_avg and xsect_avg > 0:
        r_eff_m = effective_radius_from_area_m2(float(xsect_avg))
    else:
        r_eff_m = 2.1  # conservative fallback for Starlink-like geometry

    # Core ARES settings
    cfg.update(
        {
            "functionality": 4,  # manoeuvre frequency estimation
            "analysisReferenceDate": analysis_date,
            "spacecraftMass": mass,
            "spacecraftRadius": float(r_eff_m),
            "predictionToEventTime": float(horizon_days),
            "collisionProbabilityAlgorithm": 1,  # recommended
        }
    )

    # Avoidance policy
    if use_pc_policy:
        cfg["avoidanceManoeuvreCriteria"] = 1
        cfg["targetCollisionProbabilityLevel"] = float(pc_threshold)
    else:
        cfg["avoidanceManoeuvreCriteria"] = 0
        cfg["allowedMinimumMissDistance"] = float(
            miss_distance_km if miss_distance_km is not None else 0.5
        )

    # Uncertainties
    at_km, ct_km, r_km = sc_cov_km
    cfg.update(
        {
            "spacecraftUncertaintyType": 1,
            "spacecraftAlongTrackUncertainty": float(at_km),
            "spacecraftCrossTrackUncertainty": float(ct_km),
            "spacecraftRadialUncertainty": float(r_km),
            "catalogUncertaintyType": 1,
            "globalUncertaintyScalingFactor": float(catalog_scale),
        }
    )

    # Optional metadata
    norad = str(satellite_data.get("NORAD_CAT_ID", ""))[-6:]
    # runid = (norad or satellite_data.get("OBJECT_ID", "RUN"))[:6]
    cfg.update(
        {
            # "runid": runid,
            "comment1": satellite_data.get("OBJECT_NAME", "unknown"),
            "comment2": satellite_data.get("OBJECT_ID", ""),
        }
    )

    return cfg


def run_ares_analysis(designator: str):
    """
    Fetches satellite data, runs DRAMA ARES analysis, and prints the result.
    """
    try:
        print(f"INFO: Querying database for satellite '{designator}'...")
        satellite_data = get_sat_by_designator(designator)

        if not satellite_data:
            print(
                f"ERROR: Satellite with ID '{designator}' not found in the "
                "database.",
                file=sys.stderr,
            )
            sys.exit(1)

        print("INFO: Satellite data found. Preparing ARES configuration.")
        # print(f"Satellite data: {satellite_data}")

        # Basic required fields present?
        required = [
            "INCLINATION",
            "RA_OF_ASC_NODE",
            "ECCENTRICITY",
            "ARG_OF_PERICENTER",
            "SEMIMAJOR_AXIS",
        ]
        for key in required:
            if satellite_data.get(key) is None:
                print(
                    f"ERROR: Record for '{designator}' is missing required "
                    f"orbital parameter '{key}'.",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Build enriched config (keeps same overall behavior, more realistic)
        ares_config = build_ares_config_from_satellite(
            satellite_data,
            analysis_date=datetime(2024, 8, 1),
            horizon_days=5.0,
            use_pc_policy=True,
            pc_threshold=1e-4,
            sc_cov_km=(1.0, 0.2, 0.2),
            catalog_scale=1.3,
        )

        results_data = ares.run(config=ares_config, project=None)

        if results_data.get("errors"):
            print("ERROR: ARES run failed.", file=sys.stderr)
            for error in results_data["errors"]:
                print(f"  - Status: {error.get('status')}", file=sys.stderr)
                print(f"  - Log: {error.get('logfile')}", file=sys.stderr)
            sys.exit(1)

        if results_data.get("results"):
            # functionality=4 exposes manoeuvre rate in 'annual_collision_p'
            maneuver_frequency = results_data["results"][0].get("annual_collision_p")
            if maneuver_frequency is not None:
                print("\n--- ARES Analysis Complete ---")
                print(f"Maneuver Frequency (events/year): {maneuver_frequency}")
            else:
                print(
                    "ERROR: Analysis succeeded but could not find the "
                    "maneuver frequency in the output.",
                    file=sys.stderr,
                )
                print(
                    f"Available result keys: " f"{results_data['results'][0].keys()}",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            print(
                "ERROR: ARES run completed but produced no results.",
                file=sys.stderr,
            )
            sys.exit(1)
    finally:
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

    args = parser.parse_args()

    run_ares_analysis(args.international_designator)


if __name__ == "__main__":
    # This allows the script to be executed directly via the module flag.
    # Example: python3 -m Spade.drama_ares 1998-067A 1e-4
    main()
