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
    initialize_database,
    insert_discos_data,
    insert_gp_data,
    USCDatabaseHelper,
    insert_satcat_debut_data,
)
from Spade.discos import DiscosClient

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
        print("Successfully connected. Fetching active satellite data...")

        active_satellites = client.gp(
            orderby="NORAD_CAT_ID",
        )

        if active_satellites:
            print("Successfully fetched data.")
            print(
                "Total number of active satellites found: " f"{len(active_satellites)}"
            )
        else:
            print("Failed to fetch satellite data.")
            return
        insert_gp_data(active_satellites)


def fetchSpaceDebut():
    with SpaceTrackClient(settings) as client:
        print("Successfully connected. Fetching active satellite data...")

        active_satellites = client.satcat_debut(
            orderby="NORAD_CAT_ID",
        )

        if active_satellites:
            print("Successfully fetched data.")
            print(
                "Total number of active satellites found: " f"{len(active_satellites)}"
            )
        else:
            print("Failed to fetch satellite data.")
            return
        insert_satcat_debut_data(active_satellites)


def fetchDiscosData(db: USCDatabaseHelper):
    with DiscosClient(settings=settings) as discos_client:
        all_objects = discos_client.get_all_objects(page_size=50, only_active=False)
        if all_objects:
            print("Successfully fetched data.")
            print("Total number of active satellites found: " f"{len(all_objects)}")
        else:
            print("Failed to fetch satellite data.")
            return
        insert_discos_data(all_objects)


def countDataBase(db: USCDatabaseHelper):
    result = db.cursor.execute(
        f"""
        SELECT COUNT(DRY_MASS)
        FROM USC;
        """
    )
    print("Number of satellites with mass data: ", result.fetchone()[0])

    result = db.cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM USC
        WHERE EPOCH IS NOT NULL
        """
    )
    print("Number of satellites that are currently tracked: ", result.fetchone()[0])

    result = db.cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM USC;
        """
    )
    print("Total number of satellites in table: ", result.fetchone()[0])


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
        fetchSpaceDebut()  # This gets the data on when objects were first catloged

        # Downloads full catlog from ESA
        # Then updates database
        # fetchDiscosData(db)

    if args.Count:
        countDataBase(db)  # Outputs basic stats on current satellite data

    if args.Graph:
        generateGraph(db, args)


if __name__ == "__main__":
    main()
