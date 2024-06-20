# Google Drive V3 Python Scripts

Complete the steps described in the [Drive V3 Python Quickstart](
https://developers.google.com/drive/v3/web/quickstart/python), and in
about five minutes you'll have a simple Python command-line application that
makes requests to the Drive V3 API.

## Prerequisites
- Python
- Create a project
- Activate the Drive API in the Google API Console ([the detail page](https://developers.google.com/workspace/guides/create-project))
- Create a OAuth client ID credential and download the json file to your root directory ([the detail page](https://developers.google.com/workspace/guides/create-credentials))
- Rename the file credentials.json

## Install

```shell
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```


# google_auth.py Features and Functions

The `google_auth.py` module provides a streamlined method for obtaining Google API credentials. This is particularly useful for applications that need to interact with Google services, such as Google Drive. Below are the key features and functions of this module.

## Features

1. **Credential Management**: Handles the storage and retrieval of user credentials.
2. **OAuth 2.0 Authorization**: Implements OAuth 2.0 authorization flow to obtain access tokens.
3. **Automatic Token Refresh**: Automatically refreshes the access token if it has expired.
4. **Local Server for Authorization**: Runs a local server to facilitate the OAuth 2.0 authorization process.

## Functions

### `get_credentials()`

This is the primary function provided by the `google_auth.py` module. It is used to obtain Google API credentials. Below is a detailed explanation of its functionality:

1. **Check for Existing Credentials**:
   - The function first checks if a `token.json` file exists. This file stores the user's credentials.
   - If the file exists, it loads the credentials from it.

2. **Validate Credentials**:
   - It verifies if the loaded credentials are valid.
   - If the credentials are expired but have a refresh token, it refreshes the credentials.

3. **Initiate OAuth Flow**:
   - If no valid credentials are found, it initiates the OAuth 2.0 flow using the `InstalledAppFlow` class.
   - It prompts the user to authorize the application via a local server.

4. **Save Credentials**:
   - After obtaining valid credentials, it saves them to the `token.json` file for future use.

### Usage

To use the `get_credentials` function in your application, follow these steps:

1. Import the function:
   ```python
   from google_auth import get_credentials
2. Obtain the credentials
   ```python
   credentials = get_credentials()
3. Use the credentials in your Google API calls:
   ```python
    # Example: Using the credentials to access Google Drive API
    from googleapiclient.discovery import build

    service = build('drive', 'v3', credentials=credentials)
    results = service.files().list().execute()
    items = results.get('files', [])

    for item in items:
        print(u'{0} ({1})'.format(item['name'], item['id']))


# Google Drive Download Script (`download_drive.py`)

The `download_drive.py` script provides functionality to download files and folders from Google Drive, with several features for managing downloads, including filtering by MIME type and file extension, handling subfolders, and checking disk space before downloading. Below is an overview of the key functions and features of the script.

## Functions

### `disk_space()`
- **Description**: Retrieves the total and free disk space on the system.
- **Returns**: A dictionary with total and free disk space in gigabytes.

### `get_file_extension(file_name)`
- **Description**: Extracts the file extension from a given file name.
- **Arguments**: `file_name` (str) - The name of the file.
- **Returns**: The file extension (str).

### `should_process_file(mime_type, file_extension, file_path, mime_types, file_extensions, return_object, overwrite)`
- **Description**: Determines if a file should be processed based on its MIME type, extension, existence, and other criteria.
- **Arguments**:
  - `mime_type` (str)
  - `file_extension` (str)
  - `file_path` (str)
  - `mime_types` (list)
  - `file_extensions` (list)
  - `return_object` (bool)
  - `overwrite` (bool)
- **Returns**: `True` if the file should be processed, otherwise `False`.

### `human_readable_size(size)`
- **Description**: Converts a file size into a human-readable string.
- **Arguments**: `size` (int) - The size in bytes.
- **Returns**: Human-readable file size (str).

### `download_file(service, file_id, file_name, mime_type, file_extension, folder_path=None, return_object=False)`
- **Description**: Downloads a single file from Google Drive.
- **Arguments**:
  - `service` - Google Drive service instance.
  - `file_id` (str)
  - `file_name` (str)
  - `mime_type` (str)
  - `file_extension` (str)
  - `folder_path` (str, optional)
  - `return_object` (bool, optional)
- **Returns**: A dictionary with file details if `return_object` is `True`, otherwise `None`.

### `download_files_in_folder(service, folder_id, folder_path=None, recursive=False, overwrite=False, return_object=False, mime_types=None, file_extensions=None)`
- **Description**: Downloads files from a Google Drive folder, optionally handling subfolders recursively.
- **Arguments**:
  - `service` - Google Drive service instance.
  - `folder_id` (str)
  - `folder_path` (str, optional)
  - `recursive` (bool, optional)
  - `overwrite` (bool, optional)
  - `return_object` (bool, optional)
  - `mime_types` (list, optional)
  - `file_extensions` (list, optional)
- **Returns**: A list of file objects if `return_object` is `True`, otherwise `None`.

### `process_drive_item(service, item_id, local_folder_path=None, recursive=False, overwrite=False, return_object=False, mime_types=None, file_extensions=None)`
- **Description**: Processes a Google Drive item (file or folder).
- **Arguments**:
  - `service` - Google Drive service instance.
  - `item_id` (str)
  - `local_folder_path` (str, optional)
  - `recursive` (bool, optional)
  - `overwrite` (bool, optional)
  - `return_object` (bool, optional)
  - `mime_types` (list, optional)
  - `file_extensions` (list, optional)
- **Returns**: A list of file objects if `return_object` is `True`, otherwise `None`.

### `fetch_files_in_folder(service, folder_id, recursive, current_path='')`
- **Description**: Generator function to fetch files in a Google Drive folder.
- **Arguments**:
  - `service` - Google Drive service instance.
  - `folder_id` (str)
  - `recursive` (bool)
  - `current_path` (str, optional)
- **Yields**: A dictionary with file details.

### `calculate_total_download_size(service, folder_or_file_id, local_folder_path, recursive, overwrite, mime_types, file_extensions)`
- **Description**: Calculates the total size of files to be downloaded.
- **Arguments**:
  - `service` - Google Drive service instance.
  - `folder_or_file_id` (str)
  - `local_folder_path` (str)
  - `recursive` (bool)
  - `overwrite` (bool)
  - `mime_types` (list, optional)
  - `file_extensions` (list, optional)
- **Returns**: Total size of files in bytes.

### `check_disk_space(service, folder_or_file_id, local_folder_path, recursive, mime_types, file_extensions, overwrite)`
- **Description**: Checks if there is enough disk space to download the files.
- **Arguments**:
  - `service` - Google Drive service instance.
  - `folder_or_file_id` (str)
  - `local_folder_path` (str)
  - `recursive` (bool)
  - `mime_types` (list, optional)
  - `file_extensions` (list, optional)
  - `overwrite` (bool)
- **Returns**: `True` if there is enough disk space, otherwise `False`.

Details of the Returned Objects:
    Each dictionary in the list includes:

    file_id: The ID of the file.
    file_name: The name of the file.
    mime_type: The MIME type of the file.
    extension: The file extension
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

## Script Execution

The script can be executed with the following command-line arguments:

- `folder_or_file_id` (str): ID of the Google Drive folder or file to download or process.
- `--local_folder_path` (str): Local path where the files will be saved.
- `--recursive`: Recursively download files from subfolders.
- `--overwrite`: Overwrite existing files.
- `--return_object`: Return file content as objects.
- `--mime_types` (list): List of MIME types to filter files.
- `--file_extensions` (list): List of file extensions to filter files.

### Usage

To use the `download_drive.py` module in your application, follow these steps:

1. Ensure `google_auth.py` is available and properly configured.
2. Import the required functions:
   ```python
   from google_auth import get_credentials
   from googleapiclient.discovery import build
   from download_drive import process_drive_item
3. Obtain credentials and create a Google Drive API service instance:
   ```python
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)
4. Process a Google Drive item:
   ```python
   folder_or_file_id = 'your_folder_or_file_id_here'
   file_objects = process_drive_item(service, folder_or_file_id, local_folder_path='path/to/save', recursive=True, overwrite=False, return_object=False, mime_types=['application/pdf'], file_extensions=['.pdf'])

### Command Line Usage
1. The download_drive.py module can also be used from the command line. Here is an example of how to use it:
    ```python
    python download_drive.py your_folder_or_file_id --local_folder_path path/to/save --recursive --overwrite --mime_types application/pdf --file_extensions .pdf

### Example

1. Here is an example script to download all PDF files from a specific Google Drive folder:
    ```python
    from google_auth import get_credentials
    from googleapiclient.discovery import build
    from download_drive import process_drive_item

    def main():
        folder_id = 'your_google_drive_folder_id'
        local_path = 'your_local_directory'

        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)

        process_drive_item(service, folder_id, local_path, recursive=True, overwrite=True, mime_types=['application/pdf'])

    if __name__ == '__main__':
        main()


# drive_create_folder.py Features and Functions

The `drive_create_folder.py` module provides functionalities to create folders in Google Drive. It includes functions to check for the existence of a folder within a specified parent folder and to create a new folder if it doesn't already exist.

## Features

1. **Folder Existence Check**: Checks if a folder with a given name already exists within a specified parent folder.
2. **Folder Creation**: Creates a new folder in a specified parent folder if it does not already exist.
3. **Google Drive API Integration**: Utilizes the Google Drive API for all operations.
4. **Error Handling**: Includes error handling for API requests.

## Functions

### `folder_exists(service, folder_name, starting_folder_id)`

Checks if a folder with the given name exists in the specified parent folder.

- **Arguments**:
  - `service`: The Google Drive API service instance.
  - `folder_name` (str): The name of the folder to check for.
  - `starting_folder_id` (str): The ID of the parent folder where to check for the folder.
- **Returns**:
  - `bool`: True if the folder exists, False otherwise.

### `create_folder(service, folder_name, starting_folder_id)`

Creates a folder inside a specified parent folder and prints the folder ID.

- **Arguments**:
  - `service`: The Google Drive API service instance.
  - `folder_name` (str): The name of the folder to create.
  - `starting_folder_id` (str): The ID of the parent folder where the new folder will be created.
- **Returns**:
  - `str`: Folder ID if the folder is created successfully, None otherwise.

### Command Line Usage
1. The drive_create_folder.py module can also be used from the command line. Here is an example of how to use it:
    ```python
    python drive_create_folder.py "New Folder" "your_parent_folder_id"

### Usage

To use the `drive_create_folder.py` module in your application, follow these steps:

1. Ensure `google_auth.py` is available and properly configured.
2. Import the required functions:
   ```python
   from google_auth import get_credentials
   from googleapiclient.discovery import build
   from drive_create_folder import create_folder
3. Obtain credentials and create a Google Drive API service instance:
   ```python
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)
4. Create a folder:
   ```python
    folder_name = 'New Folder'
    starting_folder_id = 'your_parent_folder_id'
    folder_id = create_folder(service, folder_name, starting_folder_id)
    if folder_id:
        print(f'Folder created with ID: {folder_id}')

### Example
1. Here is an example script to create a folder in a specified parent folder in Google Drive:
   ```python
    from google_auth import get_credentials
    from googleapiclient.discovery import build
    from drive_create_folder import create_folder

    def main():
        folder_name = 'New Folder'
        starting_folder_id = 'your_parent_folder_id'

        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)

        folder_id = create_folder(service, folder_name, starting_folder_id)
        if folder_id:
            print(f'Folder created with ID: {folder_id}')

    if __name__ == '__main__':
        main()

# drive_upload_to_folder.py Features and Functions

The `drive_upload_to_folder.py` module provides functionalities to upload files and folders to Google Drive. It includes functions to check if a file or folder already exists, upload files with the option to overwrite existing ones, and create subfolders within a specified parent folder.

## Features

1. **File Existence Check**: Checks if a file with a given name already exists in a specified folder.
2. **File Upload**: Uploads a file to a specified Google Drive folder, with an option to overwrite existing files.
3. **Folder Creation**: Creates a subfolder within a specified parent folder on Google Drive.
4. **Folder Upload**: Recursively uploads a folder and its contents to Google Drive.
5. **Google Drive API Integration**: Utilizes the Google Drive API for all operations.
6. **Command Line Interface**: Includes a command line interface for ease of use.

## Functions

### `file_exists(service, file_name, folder_id)`

Checks if a file with the given name exists in the specified folder.

- **Arguments**:
  - `service`: The Google Drive API service instance.
  - `file_name` (str): The name of the file to check for.
  - `folder_id` (str): The ID of the folder where to check for the file.
- **Returns**:
  - `str`: File ID if the file exists, None otherwise.

### `upload_file(service, file_path, folder_id, overwrite=False)`

Uploads a single file to the specified Google Drive folder.

- **Arguments**:
  - `service`: The Google Drive API service instance.
  - `file_path` (str): The local path of the file to upload.
  - `folder_id` (str): The ID of the destination folder on Google Drive.
  - `overwrite` (bool): Whether to overwrite an existing file with the same name.
- **Returns**:
  - `str`: File ID if the file is uploaded successfully, None otherwise.

### `create_drive_subfolder(service, parent_folder_id, subfolder_name)`

Creates a subfolder inside the specified parent folder on Google Drive.

- **Arguments**:
  - `service`: The Google Drive API service instance.
  - `parent_folder_id` (str): The ID of the parent folder where the subfolder will be created.
  - `subfolder_name` (str): The name of the subfolder to create.
- **Returns**:
  - `str`: Subfolder ID if the subfolder is created successfully, None otherwise.

### `upload_to_folder(service, local_path, parent_folder_id, overwrite)`

Uploads a file or folder to the specified Google Drive folder.

- **Arguments**:
  - `service`: The Google Drive API service instance.
  - `local_path` (str): The local path of the file or folder to upload.
  - `parent_folder_id` (str): The ID of the destination folder on Google Drive.
  - `overwrite` (bool): Whether to overwrite existing files in the destination folder.

### Command Line Usage
1. The drive_upload_to_folder.py module can also be used from the command line. Here is an example of how to use it:
    ```python
    python drive_upload_to_folder.py "your_drive_folder_id" "path/to/your/file_or_folder" --overwrite --create_folder

### Usage

To use the `drive_upload_to_folder.py` module in your application, follow these steps:

1. Ensure `google_auth.py` and `drive_create_folder.py` are available and properly configured.
2. Import the required functions:
   ```python
   from google_auth import get_credentials
   from googleapiclient.discovery import build
   from drive_upload_to_folder import upload_file, upload_to_folder
3. Obtain credentials and create a Google Drive API service instance:
   ```python
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)
4. Upload a file:
   ```python
    file_path = 'path/to/your/file.txt'
    folder_id = 'your_drive_folder_id'
    upload_file(service, file_path, folder_id, overwrite=True)
5. Upload a folder:
   ```python
    local_folder_path = 'path/to/your/folder'
    upload_to_folder(service, local_folder_path, folder_id, overwrite=True)

## Example
1. Here is an example script to upload a file or folder to a specified Google Drive folder:
   ```python
    from google_auth import get_credentials
    from googleapiclient.discovery import build
    from drive_upload_to_folder import upload_file, upload_to_folder

    def main():
        file_or_folder_path = 'path/to/your/file_or_folder'
        folder_id = 'your_drive_folder_id'
        overwrite = True  # Set to False if you do not want to overwrite existing files

        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)

        if os.path.isdir(file_or_folder_path):
            upload_to_folder(service, file_or_folder_path, folder_id, overwrite)
        elif os.path.isfile(file_or_folder_path):
            upload_file(service, file_or_folder_path, folder_id, overwrite)
        else:
            print(f'Error: "{file_or_folder_path}" is neither a file nor a folder.')

    if __name__ == '__main__':
        main()
