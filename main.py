from Spade.data_fetcher import fetch_full_catlog_ST
from Spade.importers import spaceTrackXML
from timeit import default_timer as timer
import os
from Spade.config import settings


def main():
    """
    This function just starts the program as a whole calling different sub modules.
    """
    if not settings:
        print("Could not start due to missing config")

    filename = fetch_full_catlog_ST(settings)
    if filename is None:
        return
    print("Filename for downloaded file is: ", filename)

    listOfUSCs = spaceTrackXML(filename)

    print(len(listOfUSCs))


if __name__ == "__main__":
    main()
