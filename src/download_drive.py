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
    python download_drive.py -h

Arguments:
    'folder_or_file_id', help='ID of the Google Drive folder or file to download or process.'
    '--local_folder_path', help='Local path where the files will be saved.'
    '--recursive', help='Recursively download files from subfolders.'
    '--overwrite', help='Overwrite existing files.'
    '--return_object', help='Return file content as objects instead of downloading.'
    '--mime_types', help='List of MIME types to filter files.'
    '--file_extensions', help='List of file extensions to filter files.'

CLI example with the appropriate arguments to specify the folder or File ID, local path, and options for recursion and overwriting files.
    python download_drive.py your-folder-or-file-id-here --local_folder_path path-to-local-folder --recursive --overwrite

CLI example if you don't want recursion or overwriting, you can omit those flags:
    python download_drive.py your-folder-or-file-id-here --local_folder_path path-to-save-files

CLI example to run the script recursively and return file objects without downloading them:
    python download_drive.py your-folder-or-file-id-here --recursive --return_object

CLI example to return file objects, with MIME type and file extension filtering:
    python drive_download.py our-folder-or-file-id-here --return_object --mime_types application/pdf --file_extensions .txt

Details of the Returned Objects:
    Each dictionary in the list includes:

    file_id: The ID of the file.
    file_name: The name of the file.
    mime_type: The MIME type of the file.
    content: The BytesIO object containing the file content.

Example:
    Assume there are three files in the folder, and the return_object parameter is set. The script will return a list like this:

    [
        {
            'file_id': '1A2B3C4D',
            'file_name': 'file1.pdf',
            'mime_type': 'application/pdf',
            'extension': .pdf
            'content': <BytesIO object at 0x7fabc1234560>
        },
        {
            'file_id': '2B3C4D5E',
            'file_name': 'file2.docx',
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'extension': .docx
            'content': <BytesIO object at 0x7fabc1234560>
        },
        {
            'file_id': '3C4D5E6F',
            'file_name': 'file3.xlsx',
            'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'extension': .xlsx
            'content': <BytesIO object at 0x7fabc1234560>
        }
    ]

"""

# [START drive_download]
import io
import os
import time
import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google_auth import get_credentials

def disk_space():
    st = os.statvfs('/')
    block_size = st.f_frsize
    total_blocks = st.f_blocks
    free_blocks = st.f_bavail

    total_gb = total_blocks * block_size / (1024 ** 3)
    free_gb = free_blocks * block_size / (1024 ** 3)

    return {"total": total_gb, "free": free_gb}

def get_file_extension(file_name):
    return os.path.splitext(file_name)[1]

def should_process_file(mime_type, file_extension, file_path, mime_types, file_extensions, return_object, overwrite):
    if mime_types and mime_type not in mime_types:
        return False
    if file_extensions and file_extension not in file_extensions:
        return False
    if not return_object and not overwrite and file_path and os.path.exists(file_path):
        print(f'Skipping {file_path}, file already exists.')
        return False
    return True

def human_readable_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def download_file(service, file_id, file_name, mime_type, file_extension, folder_path=None, return_object=False):
    try:
        if folder_path is not None:
            file_path = os.path.join(folder_path, file_name)
        else:
            file_path = None

        export_mime_types = {
            'application/vnd.google-apps.document': 'application/pdf',
            'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }

        if mime_type in export_mime_types:
            request = service.files().export_media(fileId=file_id, mimeType=export_mime_types[mime_type])
            file_name += file_extension
        else:
            request = service.files().get_media(fileId=file_id, supportsAllDrives=True)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        start_time = time.time()
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f'Download {int(status.progress() * 100)}% of {file_name}.')

        elapsed_time = time.time() - start_time
        file_size = fh.tell()
        speed = file_size / elapsed_time
        print(f'Download completed. File size: {human_readable_size(file_size)}, Time taken: {elapsed_time:.2f} seconds, Speed: {human_readable_size(speed)}/s.')

        fh.seek(0)

        if return_object:
            return {
                'file_id': file_id,
                'file_name': file_name,
                'mime_type': mime_type,
                'file_extension': file_extension,
                'content': fh
            }

        if folder_path is not None:
            with open(file_path, 'wb') as f:
                f.write(fh.read())

    except HttpError as error:
        print(f"An error occurred: {error}")

def download_files_in_folder(service, folder_id, folder_path=None, recursive=False, overwrite=False, return_object=False, mime_types=None, file_extensions=None):
    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name, mimeType, size)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        items = results.get('files', [])

        if not items:
            print('No files found in the folder.')
            return []

        file_objects = []

        if not return_object and folder_path is not None:
            os.makedirs(folder_path, exist_ok=True)

        for item in items:
            file_id = item['id']
            file_name = item['name']
            mime_type = item['mimeType']
            file_extension = get_file_extension(file_name)

            if mime_type == 'application/vnd.google-apps.folder':
                if recursive:
                    print(f'Found subfolder: {file_name}')
                    subfolder_path = os.path.join(folder_path, file_name) if folder_path else None
                    file_objects.extend(download_files_in_folder(service, file_id, subfolder_path, recursive, overwrite, return_object, mime_types, file_extensions))
            else:
                file_path = os.path.join(folder_path, file_name) if folder_path else None
                if not should_process_file(mime_type, file_extension, file_path, mime_types, file_extensions, return_object, overwrite):
                    continue
                
                print(f'Downloading {file_name}...')
                file_object = download_file(service, file_id, file_name, mime_type, file_extension, folder_path, return_object)
                if return_object and file_object:
                    file_objects.append(file_object)

        return file_objects

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def process_drive_item(service, item_id, local_folder_path=None, recursive=False, overwrite=False, return_object=False, mime_types=None, file_extensions=None):
    try:
        item = service.files().get(fileId=item_id, fields='id, name, mimeType, size', supportsAllDrives=True).execute()
        mime_type = item['mimeType']
        item_name = item['name']
        file_extension = get_file_extension(item_name)

        if mime_type == 'application/vnd.google-apps.folder':
            print(f'Processing folder: {item_name}')
            return download_files_in_folder(service, item_id, local_folder_path, recursive, overwrite, return_object, mime_types, file_extensions)
        else:
            print(f'Processing file: {item_name}')
            file_path = os.path.join(local_folder_path, item_name) if local_folder_path else None
            file_objects = []
            if not should_process_file(mime_type, file_extension, file_path, mime_types, file_extensions, return_object, overwrite):
                return []
            
            file_object = download_file(service, item_id, item_name, mime_type, file_extension, local_folder_path, return_object)
            if return_object and file_object:
                file_objects.append(file_object)
            return file_objects

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def fetch_files_in_folder(service, folder_id, recursive, current_path=''):
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, mimeType, size)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    items = results.get('files', [])
    for item in items:
        item_path = os.path.join(current_path, item['name'])
        if item['mimeType'] == 'application/vnd.google-apps.folder' and recursive:
            yield from fetch_files_in_folder(service, item['id'], recursive, item_path)
        else:
            yield {
                'id': item['id'],
                'name': item['name'],
                'mimeType': item['mimeType'],
                'size': item.get('size', 0),
                'path': item_path
            }

def calculate_total_download_size(service, folder_or_file_id, local_folder_path, recursive, overwrite, mime_types, file_extensions):
    remote_files = list(fetch_files_in_folder(service, folder_or_file_id, recursive))
    local_files = {}

    for root, _, files in os.walk(local_folder_path):
        for name in files:
            local_file_path = os.path.join(root, name)
            relative_path = os.path.relpath(local_file_path, local_folder_path)
            local_files[relative_path] = os.path.getsize(local_file_path)

    total_size = 0
    for remote_file in remote_files:
        remote_file_path = remote_file['path']
        remote_file_size = int(remote_file['size'])
        if remote_file_path in local_files:
            if not overwrite:
                continue
        total_size += remote_file_size

    return total_size

def check_disk_space(service, folder_or_file_id, local_folder_path, recursive, mime_types, file_extensions, overwrite):
    if not local_folder_path:
        return True

    total_size = calculate_total_download_size(service, folder_or_file_id, local_folder_path, recursive, overwrite, mime_types, file_extensions)

    disk_info = disk_space()
    print("Total disk space:", disk_info["total"], "GB")
    print("Free disk space:", disk_info["free"], "GB")
    print("Total download size:", human_readable_size(total_size))

    if total_size / (1024 ** 3) > disk_info["free"]:
        return False

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download or process files from Google Drive.')
    parser.add_argument('folder_or_file_id', help='ID of the Google Drive folder or file to download or process.')
    parser.add_argument('--local_folder_path', help='Local path where the files will be saved.')
    parser.add_argument('--recursive', action='store_true', help='Recursively download files from subfolders.')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files.')
    parser.add_argument('--return_object', action='store_true', help='Return file content as objects.')
    parser.add_argument('--mime_types', nargs='*', help='List of MIME types to filter files.')
    parser.add_argument('--file_extensions', nargs='*', help='List of file extensions to filter files.')

    args = parser.parse_args()

    if not args.return_object and not args.local_folder_path:
        parser.error('The --local_folder_path parameter is required when --return_object is not set.')

    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    if not check_disk_space(service, args.folder_or_file_id, args.local_folder_path, args.recursive, args.mime_types, args.file_extensions, args.overwrite):
        print("Error: Not enough free disk space to download the files.")
        exit(1)

    file_objects = process_drive_item(service, args.folder_or_file_id, args.local_folder_path, args.recursive, args.overwrite, args.return_object, args.mime_types, args.file_extensions)

    if args.return_object:
        for obj in file_objects:
            print(f"Processed file: {obj['file_name']}, MIME Type: {obj['mime_type']}, File Extension: {obj['file_extension']}")
# [END drive_download]
