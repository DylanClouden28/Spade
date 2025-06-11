from Spade.data_fetcher import fetch_full_catlog_ST
from Spade.importers import spaceTrackXML
from timeit import default_timer as timer
import os


def main():
    """
    This function just starts the program as a whole calling different sub modules.
    """

    filename = fetch_full_catlog_ST()
    if filename is None:
        return
    print("Filename for downloaded file is: ", filename)

    listOfUSCs = spaceTrackXML(filename)

    print(len(listOfUSCs))


if __name__ == "__main__":
    main()
