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
    python drive_upload_to_folder.py -h

Arguments:
    'drive_folder_id', type=str, help='The ID of the destination Drive folder'
    'local_folder_or_filename', type=str, help='The local file or folder to upload'
    '--create_folder', action='store_true', help='Create the remote Drive folder if it does not exist'
    '--overwrite', action='store_true', help='Overwrite existing files in the destination folder'

CLI example with the appropriate arguments to specify the remote folder ID, local folder/file path, and option to create remote folder.
    python drive_upload_to_folder.py your-remote-folder-id-here path-to-local-folder-or-file --create_folder

CLI example with the appropriate arguments to specify the remote folder ID, local folder/file path, and option to overwrite existing remote files.
    python drive_upload_to_folder.py your-remote-folder-id-here path-to-local-folder-or-file --overwrite

"""

# [START drive_upload_to_folder]
import argparse
import os
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth import get_credentials
from drive_create_folder import folder_exists, create_folder

def human_readable_size(size):
    """Convert file size to human-readable form (B, KB, MB, GB, TB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def file_exists(service, file_name, folder_id):
    """Check if a file with the given name exists in the specified folder."""
    query = f"'{folder_id}' in parents and name='{file_name}' and mimeType!='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = results.get('files', [])
    return files[0]['id'] if files else None

def upload_file(service, file_path, folder_id, overwrite=False):
    """Uploads a single file to the specified Google Drive folder."""
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    existing_file_id = file_exists(service, file_name, folder_id)
    
    start_time = time.time()
    
    if existing_file_id:
        if overwrite:
            try:
                # The update method is used without attempting to modify the parents field. Instead, it only updates the file content using media_body.
                media = MediaFileUpload(file_path, resumable=True)
                file = service.files().update(
                    fileId=existing_file_id,
                    media_body=media
                ).execute()
                elapsed_time = time.time() - start_time
                speed = file_size / elapsed_time
                print(f'File "{file_path}" overwritten with ID: "{file.get("id")}".')
                print(f'File size: {human_readable_size(file_size)}, Time taken: {elapsed_time:.2f} seconds, Speed: {human_readable_size(speed)}/s')
                return file.get("id")
            except HttpError as error:
                print(f"An error occurred: {error}")
                return None
        else:
            print(f'Error: A file named "{file_name}" already exists in the folder. Use --overwrite to overwrite it.')
            return None
    else:
        try:
            file_metadata = {"name": file_name, "parents": [folder_id]}
            media = MediaFileUpload(file_path, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            elapsed_time = time.time() - start_time
            speed = file_size / elapsed_time
            print(f'File "{file_path}" uploaded with ID: "{file.get("id")}".')
            print(f'File size: {human_readable_size(file_size)}, Time taken: {elapsed_time:.2f} seconds, Speed: {human_readable_size(speed)}/s')
            return file.get("id")
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

def create_drive_subfolder(service, parent_folder_id, subfolder_name):
    """Creates a subfolder inside the specified parent folder on Google Drive."""
    if folder_exists(service, subfolder_name, parent_folder_id):
        results = service.files().list(q=f"'{parent_folder_id}' in parents and name='{subfolder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false", spaces='drive', fields='files(id, name)').execute()
        return results.get('files', [])[0]['id']
    else:
        return create_folder(service, subfolder_name, parent_folder_id)

def upload_to_folder(service, local_path, parent_folder_id, overwrite):
    """Uploads a file or folder to the specified Google Drive folder."""
    folder_mapping = {local_path: parent_folder_id}
    
    for root, dirs, files in os.walk(local_path):
        current_folder_id = folder_mapping[root]
        
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            folder_id = create_drive_subfolder(service, current_folder_id, directory)
            folder_mapping[dir_path] = folder_id
        
        for file in files:
            file_path = os.path.join(root, file)
            upload_file(service, file_path, current_folder_id, overwrite)

def main():
    parser = argparse.ArgumentParser(description='Upload a file or folder to Google Drive.')
    parser.add_argument('drive_folder_id', type=str, help='The ID of the destination Drive folder')
    parser.add_argument('local_folder_or_filename', type=str, help='The local file or folder to upload')
    parser.add_argument('--create_folder', action='store_true', help='Create the remote Drive folder if it does not exist')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files in the destination folder')

    args = parser.parse_args()
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    try:
        folder_id = args.drive_folder_id

        if os.path.isdir(args.local_folder_or_filename):
            folder_name = os.path.basename(args.local_folder_or_filename)
            
            if args.create_folder:
                if folder_exists(service, folder_name, folder_id):
                    print(f'Error: A folder named "{folder_name}" already exists in the specified parent folder.')
                    return
                else:
                    folder_id = create_folder(service, folder_name, folder_id)
                    if folder_id is None:
                        return
            else:
                if not folder_exists(service, folder_name, folder_id):
                    print(f'Error: The folder "{folder_name}" does not exist and the create_folder option is not set.')
                    return

            upload_to_folder(service, args.local_folder_or_filename, folder_id, args.overwrite)
        
        elif os.path.isfile(args.local_folder_or_filename):
            upload_file(service, args.local_folder_or_filename, folder_id, args.overwrite)
        
        else:
            print(f'Error: "{args.local_folder_or_filename}" is neither a file nor a folder.')

    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
if __name__ == "__main__":
    main()
# [END drive_upload_to_folder]
