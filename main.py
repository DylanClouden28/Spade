from Spade.data_fetcher import (
    fetch_full_catlog_ST,
    save_discos_objects,
    fetch_full_debut,
)
from Spade.importers import parseDISCOSJSON, spaceTrackXML, spaceTrackXML_DEBUT
from timeit import default_timer as timer
import os
from Spade.config import settings
import time
import argparse
from argparse import Namespace
import sys
from Spade.graphs import (
    generateSatellitesOvertime,
    generateScatterPlots,
    generateScatterAVG,
    generateScatterGrid,
    generateAltInc,
    generateDensityBins,
)
from Spade.graph3d import generate3dgraphsOrbits
import Spade.graphs_withoutstarlink as gws
from Spade.spacetrack import SpaceTrackClient
from Spade.database.database import (
    combine_data,
    initialize_database,
    insert_discos_data,
    insert_gp_data,
    USCDatabaseHelper,
    insert_satcat_debut_data,
    main_combiner,
)
from Spade.discos import DiscosClient
from Spade.database.models import GP, SatcatDebut, DiscosObjectDB
import json
import pprint

from Spade.drama_ares import run_ares_analysis

# Initialize parser
msg = "Adding description"
parser = argparse.ArgumentParser(description=msg)

parser.add_argument(
    "-r", "--Refetch", help="Refetchs data for database", action="store_true"
)

parser.add_argument(
    "-c",
    "--Count",
    help="General Counts of satellites in database",
    action="store_true",
)

parser.add_argument(
    "-g",
    "--Graph",
    help="Creates graph of choice",
    choices=[
        "SatsOvertime",
        "scatterPlot",
        "scatterPlotAVG",
        "scatterPlotGrid",
        "scatterAltInc",
        "scatterDensityBins",
        "3dorbits",
        "2dplots_nostarlink",
    ],
)


def fetchSpaceCatlog():
    with SpaceTrackClient(settings) as client:
        print("Successfully connected to space track. Fetching catlog data...")

        active_satellites = client.gp(
            orderby="NORAD_CAT_ID",
        )

        if active_satellites:
            print("Successfully fetched data.")
            print(
                "\tTotal number of active satellites found: "
                f"{len(active_satellites)}"
            )
        else:
            print("Failed to fetch satellite data.")
            return
        insert_gp_data(active_satellites)


def fetchSpaceDebut():
    with SpaceTrackClient(settings) as client:
        print("Successfully connected to space track. Fetching debut data...")

        active_satellites = client.satcat_debut(
            orderby="NORAD_CAT_ID",
        )

        if active_satellites:
            print("Successfully fetched data.")
            print(
                "\tTotal number of active satellites found: "
                f"{len(active_satellites)}"
            )
        else:
            print("Failed to fetch satellite data.")
            return
        insert_satcat_debut_data(active_satellites)


def fetchDiscosData():
    with DiscosClient(settings=settings) as discos_client:
        print("Successfully connected to discos. Fetching satellite data...")
        all_objects = discos_client.get_all_objects(page_size=50, only_active=False)
        if all_objects:
            print("Successfully fetched data.")
            print("\tTotal number of active satellites found: " f"{len(all_objects)}")
        else:
            print("Failed to fetch satellite data.")
            return
        insert_discos_data(all_objects)


def countDataBase(db: USCDatabaseHelper):
    combined_satellites = combine_data([GP, SatcatDebut, DiscosObjectDB], main_combiner)
    print(
        "Total number of satellites in the database after being combined:",
        len(combined_satellites),
    )


def startAresAnalysis(designator: str, risk_threshold: float):
    """
    Starts the ARES analysis for a given satellite designator.

    Args:
        designator (str): The international designator of the satellite.
        risk_threshold (float): The target collision probability level for the
                                maneuver criteria.
    """
    run_ares_analysis(designator, risk_threshold)


def generateGraph(db: USCDatabaseHelper, args: Namespace):
    match args.Graph:
        case "SatsOvertime":
            generateSatellitesOvertime(db)
        case "scatterPlot":
            generateScatterPlots(db)
        case "scatterPlotAVG":
            generateScatterAVG(db)
        case "scatterPlotGrid":
            generateScatterGrid(db)
        case "scatterAltInc":
            generateAltInc(db)
        case "scatterDensityBins":
            generateDensityBins(db)
        case "3dorbits":
            generate3dgraphsOrbits(db)
        case "2dplots_nostarlink":
            gws.generateDensityBins(db)
            gws.generateAltInc(db)
            gws.generateSatellitesOvertime(db)
            gws.generateScatterAVG(db)
            gws.generateScatterGrid(db)
            gws.generateScatterPlots(db)


class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def main():
    """
    This function just starts the program as a whole calling different sub modules.
    """
    if not settings:
        print("Could not start due to missing config")

    if len(sys.argv) < 2:
        print(
            color.BOLD + "Please provide an argument to run the program\n" + color.END
        )
        parser.print_help()
        return

    args = parser.parse_args()

    db = USCDatabaseHelper()
    db.initializeTable()

    initialize_database()

    if args.Refetch:
        # Downloads full catlog from Space Track
        # Then updates database
        fetchSpaceCatlog()  # This gets general data about all currently tracked objects
        print("\n")
        fetchSpaceDebut()  # This gets the data on when objects were first catloged
        print("\n")
        # Downloads full catlog from ESA
        # Then updates database
        fetchDiscosData()

    if args.Count:
        countDataBase(db)  # Outputs basic stats on current satellite data

    if args.Graph:
        generateGraph(db, args)


if __name__ == "__main__":
    main()
