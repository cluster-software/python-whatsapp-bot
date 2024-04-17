import time
import logging
import requests
from dotenv import load_dotenv
import os

load_dotenv()
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")


def get_hubspot_owner_data():
    url = "https://api.hubapi.com/crm/v3/owners"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        owners = response.json()
        onwer_list = [
            {
                "name": owner.get("firstName") + " " + owner.get("lastName"),
                "email": owner.get("email"),
                "owner_id": owner.get("id"),
                "user_id": owner.get("userId"),
                "created_at": owner.get("createdAt"),
                "updated_at": owner.get("updatedAt"),
                "team": owner.get("team"),
            }
            for owner in owners.get("results", [])
            if owner.get("email")
            == "luis@hello-cluster.com"  # to avoid returning enrique's account too
        ]
        return onwer_list[0]
    else:
        raise Exception(f"Error retrieving owners: {response.content}")


def create_hubspot_contact(phone_number=None, first_name=None, last_name=None):
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "properties": {
            "phone": phone_number,
            "firstname": first_name,
            "lastname": last_name,
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        logging.info(response.json())
        return response.json()
    else:
        raise Exception(f"Error creating contact: {response.content}")


def create_hubspot_note_on_contact(contact_id, note):
    url = "https://api.hubapi.com/crm/v3/objects/notes"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }
    owner_data = get_hubspot_owner_data()
    data = {
        "properties": {
            "hs_timestamp": int(time.time() * 1000),
            "hs_note_body": note,
            "hubspot_owner_id": owner_data["owner_id"],
        },
        "associations": [  # https://developers.hubspot.com/docs/api/crm/associations
            {
                "to": {"id": contact_id},
                "types": [
                    {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}
                ],
            }
        ],
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Error creating contact: {response.content}")


# print(get_hubspot_owners())
