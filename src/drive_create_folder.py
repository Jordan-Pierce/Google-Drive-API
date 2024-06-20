"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Writen and Mods by: Kirk L. Yedinak and ChatGPT4

Start here:
    https://developers.google.com/drive/api/quickstart/python

Requirements:
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Script Help
    python drive_create_folder.py -h

Arguments:
    'folder_name', help='The name of the folder to create'
    'starting_folder_id', type=str, help='The ID of the parent folder where the new folder will be created'

CLI example with the appropriate arguments to specify the folder or File ID, local path, and options for recursion and overwriting files.
    python drive_create_folder.py "My New Folder" "parent_folder_id"

Special Note:  To create a folder in Google Drive you must use the "https://www.googleapis.com/auth/drive" SCOPE.  This grants full access to create and delete from drive.
"""

# [START drive_create_folder]
import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth import get_credentials

def folder_exists(service, folder_name, starting_folder_id):
    """Check if a folder with the given name exists in the specified parent folder.
    Args:
        service: The Google Drive API service instance.
        folder_name (str): The name of the folder to check for.
        starting_folder_id (str): The ID of the parent folder where to check for the folder.
    Returns:
        bool: True if the folder exists, False otherwise.
    """
    query = f"'{starting_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    return len(results.get('files', [])) > 0

def create_folder(service, folder_name, starting_folder_id):
    """Create a folder inside a specified parent folder and prints the folder ID.
    Args:
        folder_name (str): The name of the folder to create.
        starting_folder_id (str): The ID of the parent folder where the new folder will be created.
    Returns:
        str: Folder ID
    """
    try:   
        # Check if folder already exists
        if folder_exists(service, folder_name, starting_folder_id):
            print(f'Error: A folder named "{folder_name}" already exists in the specified parent folder.')
            return None

        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [starting_folder_id]
        }

        file = service.files().create(body=file_metadata, fields="id").execute()
        print(f'Folder ID: "{file.get("id")}".')
        return file.get("id")

    except HttpError as error:
        print(f"An error occurred: {error}")
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a folder in Google Drive.')
    parser.add_argument('folder_name', type=str, help='The name of the folder to create')
    parser.add_argument('starting_folder_id', type=str, help='The ID of the parent folder where the new folder will be created')
    
    args = parser.parse_args()
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)
    create_folder(service, args.folder_name, args.starting_folder_id)
# [END drive_create_folder]
