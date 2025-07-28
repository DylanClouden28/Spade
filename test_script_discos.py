import json
import os
import requests
from Spade.config import settings


API_URL = settings.DISCOS_BASE_URL + "/api/objects"


OUTPUT_FILENAME = "discos_response_test_data.json"

API_TOKEN = settings.DISCOS_TOKEN


def fetch_and_save_data():

    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    params = {"include": "destinationOrbits", "page[size]": 10}

    print(f"Requesting data from {API_URL}...")
    print(f"Parameters: {params}")

    try:

        response = requests.get(API_URL, headers=headers, params=params)

        response.raise_for_status()

        data = response.json()
        print("Successfully received data from the API.")

        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:

            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Response successfully saved to '{OUTPUT_FILENAME}'")

    except requests.exceptions.HTTPError as http_err:

        print(f"HTTP error occurred: {http_err}")
        print(f"Status Code: {response.status_code}")

        try:
            print(f"API Response: {response.json()}")
        except json.JSONDecodeError:
            print(f"API Response (raw): {response.text}")
    except requests.exceptions.RequestException as err:

        print(f"An error occurred during the request: {err}")
    except Exception as err:

        print(f"An unexpected error occurred: {err}")


if __name__ == "__main__":
    fetch_and_save_data()
