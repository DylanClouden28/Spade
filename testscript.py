import requests
from dotenv import load_dotenv
import os

load_dotenv()

URL = "https://discosweb.esoc.esa.int"
token = os.environ.get("DISCOS_TOKEN")

response = requests.get(
    f"{URL}/api/objects",
    headers={
        "Authorization": f"Bearer {token}",
        "DiscosWeb-Api-Version": "2",
    },
    params={"page[size]": 3, "page[number]": 1},
)

doc = response.json()
if response.ok:
    print(doc["data"])
else:
    print(doc["errors"])
