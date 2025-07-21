import json  # Import the json module
from spacetrack import SpaceTrackClient
from Spade.config import settings

with SpaceTrackClient(
    settings.SPACE_TRACKER_USERNAME, settings.SPACE_TRACKER_PASSWORD
) as st:
    print(f"Type of st.basicspacedata: {type(st.basicspacedata)}")

    print(f"Type of st.basicspacedata.gp: {type(st.basicspacedata.gp)}")

    try:
        # Request data with format="json". This means 'data' will be a JSON string.
        data_raw_json = st.basicspacedata.gp(format="json", limit=1)
        print("Successfully retrieved data!")

        # Check if the data is not empty before trying to parse
        if data_raw_json:
            # Parse the JSON string into a Python object (e.g., list of dicts)
            data_python_object = json.loads(data_raw_json)

            # Pretty print the Python object back to a JSON string
            print(json.dumps(data_python_object, indent=2))
        else:
            print("Received empty data.")

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        print(
            f"Raw response was: {data_raw_json}"
        )  # Print raw response if decoding fails
    except Exception as e:
        print(f"An error occurred during the call: {e}")
