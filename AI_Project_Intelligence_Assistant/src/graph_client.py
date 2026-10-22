
import os

import msal
import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def get_access_token():
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        raise ValueError(
            "Check TENANT_ID, CLIENT_ID, and CLIENT_SECRET in .env"
        )

    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
    )

    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in result:
        raise RuntimeError(
            f"Authentication failed: {result.get('error')} - "
            f"{result.get('error_description', 'No details')}"
        )

    return result["access_token"]


def list_onedrive_files():
    user_email = os.getenv("ONEDRIVE_USER_EMAIL")

    if not user_email:
        raise ValueError(
            "Add ONEDRIVE_USER_EMAIL to your .env file."
        )

    token = get_access_token()

    url = (
        f"{GRAPH_BASE_URL}/users/"
        f"{user_email}/drive/root/children"
    )

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()

    return response.json().get("value", [])


def list_folder_items(folder_id):
    user_email = os.getenv("ONEDRIVE_USER_EMAIL")

    if not user_email:
        raise ValueError("Add ONEDRIVE_USER_EMAIL to your .env file.")

    token = get_access_token()

    url = (
        f"{GRAPH_BASE_URL}/users/"
        f"{user_email}/drive/items/{folder_id}/children"
    )

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()

    return response.json().get("value", [])


def download_file_content(file_id):
    user_email = os.getenv("ONEDRIVE_USER_EMAIL")

    if not user_email:
        raise ValueError("Add ONEDRIVE_USER_EMAIL to your .env file.")

    token = get_access_token()

    url = (
        f"{GRAPH_BASE_URL}/users/"
        f"{user_email}/drive/items/{file_id}/content"
    )

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    response.raise_for_status()

    return response.content



if __name__ == "__main__":
    try:
        files = list_onedrive_files()

        print(f"\nFound {len(files)} items in OneDrive root:\n")

        for item in files:
            item_type = "Folder" if "folder" in item else "File"

            print(f"Name: {item.get('name', 'Unknown')}")
            print(f"Type: {item_type}")
            print(f"ID: {item.get('id', 'N/A')}")
            print(f"Modified: {item.get('lastModifiedDateTime', 'N/A')}")
            print("-" * 40)

    except requests.HTTPError as error:
        print(f"Microsoft Graph request failed: {error}")
        if error.response is not None:
            print(f"Response details: {error.response.text[:1000]}")
    except (ValueError, RuntimeError) as error:
        print(error)
