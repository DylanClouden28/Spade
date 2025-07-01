from Spade.data_fetcher import (
    fetch_full_catlog_ST,
    save_discos_objects,
    fetch_full_debut,
)
from Spade.importers import parseDISCOSJSON, spaceTrackXML, spaceTrackXML_DEBUT
from timeit import default_timer as timer
import os
from Spade.config import settings
from Spade.database import USCDatabaseHelper
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


def fetchSpaceCatlog(db: USCDatabaseHelper):
    # Downloads fill catlog from Space Track
    filename = fetch_full_catlog_ST(settings)
    if filename is None:
        return
    print("Space Track Data saved to: ", filename)

    spaceTrackUSCs = spaceTrackXML(filename)

    print(f"Number of satellites from spaceTrack: ", len(spaceTrackUSCs))
    db.bulkInsertUSC(spaceTrackUSCs)


def fetchSpaceDebut(db: USCDatabaseHelper):
    # Downloads fill catlog from Space Track
    filename = fetch_full_debut(settings)
    if filename is None:
        return
    print("Space Track Data saved to: ", filename)

    spaceTrackUSCs = spaceTrackXML_DEBUT(filename)

    print(f"Number of satellites from spaceTrack: ", len(spaceTrackUSCs))
    db.bulkInsertUSC(spaceTrackUSCs)


def fetchDiscosData(db: USCDatabaseHelper):
    # Downloads full catlog from ESA
    discosFile = save_discos_objects(settings)
    if discosFile is None:
        return
    print("DISCOS Data saved to: ", discosFile)

    discosUSCS = parseDISCOSJSON(discosFile)
    print("Number of satellites from discos: ", len(discosUSCS))
    db.bulkInsertUSC(discosUSCS)


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

    if args.Refetch:
        # Downloads full catlog from Space Track
        # Then updates database
        fetchSpaceCatlog(
            db
        )  # This gets general data about all currently tracked objects
        fetchSpaceDebut(db)  # This gets the data on when objects were first catloged

        # Downloads full catlog from ESA
        # Then updates database
        fetchDiscosData(db)

    if args.Count:
        countDataBase(db)  # Outputs basic stats on current satellite data

    if args.Graph:
        generateGraph(db, args)


if __name__ == "__main__":
    main()
