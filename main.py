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
    print("Filename for downloaded file is: ", filename)

    listOfUSCs = spaceTrackXML(filename)

    print(len(listOfUSCs))

    print("Starting insert of USCS")
    t0 = time.time()
    for idx, usc in enumerate(listOfUSCs):
        if (idx % 100) == 0:
            print(f"\tInserted {idx}/{len(listOfUSCs)}")
        if usc.INTERNATIONAL_DESIGNATOR == "UNKNOWN":
            continue
        db.insertUSC(usc)
    db.saveDB()  # Save insertes
    t1 = time.time()
    print("Inserting finished, total time: ", t1 - t0)

    # Downloads full catlog from ESA
    # discosFile = save_discos_objects(settings)
    # if discosFile is None:
    #     return
    # print("DISCOS Data saved to: ", discosFile)

    # discosUSCS = parseDISCOSJSON(discosFile)
    # print("Number of satellites from discos: ", len(discosUSCS))


if __name__ == "__main__":
    main()
