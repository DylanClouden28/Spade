from Spade.spacetrack import SpaceTrackClient
from Spade.config import Settings


def main():
    """
    Example usage of the SpaceTrackClient to fetch and count active satellites.
    """
    print("Initializing settings and client...")
    try:
        settings = Settings()
    except Exception as e:
        print(
            "Could not initialize settings. "
            f"Make sure your .env file is set up. Error: {e}"
        )
        return

    print("Attempting to connect to Space-Track.org...")
    try:
        with SpaceTrackClient(settings) as client:
            print("Successfully connected. Fetching active satellite data...")

            active_satellites = client.gp(
                orderby="NORAD_CAT_ID",
            )

            if active_satellites:
                print("Successfully fetched data.")
                print(
                    "Total number of active satellites found: "
                    f"{len(active_satellites)}"
                )
            else:
                print("Failed to fetch satellite data.")

    except ConnectionError as e:
        print(f"Connection failed: {e}")
    except RuntimeError as e:
        print(f"Runtime error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
