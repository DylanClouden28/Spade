from Spade.spacetrack import SpaceTrackClient
from Spade.config import Settings
from Spade.discos import DiscosClient
from Spade.config import settings


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


def test_discos_client():

    try:
        with DiscosClient(settings=settings) as discos_client:
            #             print("\n--- Fetching a single page of objects ---")
            #             first_page = discos_client.get_objects_page(
            #                 page_number=1, page_size=5, filter_str="active=true"
            #             )
            #             if first_page and first_page["data"]:
            #                 print(
            #                     f"Successfully fetched {len(first_page['data'])} objects on page 1."
            #                 )
            #                 # print(json.dumps(first_page['data'][0], indent=2)) # Uncomment to see an object
            # #
            print("\n--- Fetching ALL active objects (will be cached) ---")
            # Using a smaller page size for demonstration to show pagination
            all_active_objects = discos_client.get_all_objects(
                page_size=50, only_active=False
            )
            if all_active_objects:
                print(
                    f"\nSuccessfully fetched a total of {len(all_active_objects)} active objects."
                )

    except RuntimeError as e:
        print(f"An error occurred: {e}")
    except ConnectionError as e:
        print(f"A connection error occurred: {e}")


if __name__ == "__main__":
    # main()
    test_discos_client()
