from Spade.data_fetcher import fetch_full_catlog_ST, save_discos_objects
from Spade.importers import parseDISCOSJSON, spaceTrackXML
from timeit import default_timer as timer
import os
from Spade.config import settings
from Spade.database import USCDatabaseHelper
import time


def main():
    """
    This function just starts the program as a whole calling different sub modules.
    """
    if not settings:
        print("Could not start due to missing config")

    db = USCDatabaseHelper()
    db.initializeTable()

    # Downloads fill catlog from Space Track
    filename = fetch_full_catlog_ST(settings)
    if filename is None:
        return
    print("Space Track Data saved to: ", filename)

    spaceTrackUSCs = spaceTrackXML(filename)

    print(f"Number of satellites from spaceTrack: ", len(spaceTrackUSCs))
    db.bulkInsertUSC(spaceTrackUSCs)

    # Downloads full catlog from ESA
    discosFile = save_discos_objects(settings)
    if discosFile is None:
        return
    print("DISCOS Data saved to: ", discosFile)

    discosUSCS = parseDISCOSJSON(discosFile)
    print("Number of satellites from discos: ", len(discosUSCS))
    db.bulkInsertUSC(discosUSCS)

    result = db.cursor.execute(
        f"""
        SELECT COUNT(DRY_MASS)
        FROM USC;
        """
    )
    print("Number of satellites with mass data: ", result.fetchone())


if __name__ == "__main__":
    main()
