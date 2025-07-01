# import asyncio
# import httpx
# import os
# import json
# from datetime import datetime
# from typing import Optional, Union

# from microsoft_graph.auth import MicrosoftGraphAuth

# async def upload_file_to_onedrive(
#     auth_handler: MicrosoftGraphAuth,
#     user_id: str, # The user ID or userPrincipalName of the OneDrive owner
#     folder_path: str, # Path to the folder in OneDrive, e.g., "Documents/Reports" or "General"
#     file_name: str,   # Name of the file to upload, e.g., "my_document.txt"
#     file_content: Union[str, bytes] # Content of the file as string or bytes
# ) -> dict:
#     """
#     Uploads a file to a specified OneDrive folder via direct HTTP request.

#     Args:
#         auth_handler: An authenticated MicrosoftGraphAuth instance.
#         user_id: The user ID or userPrincipalName whose OneDrive the file will be uploaded to.
#         folder_path: The path to the target folder in OneDrive (e.g., "Documents", "MyFolder/Subfolder").
#                      Use "root" or "" for the top-level drive.
#         file_name: The name of the file, including extension (e.g., "report.docx").
#         file_content: The content of the file. Can be a string (for text files) or bytes.

#     Returns:
#         A dictionary indicating success/failure and file details.
#     """
#     try:
#         access_token = auth_handler.get_access_token()
#         base_url = auth_handler.get_base_graph_url()

#         # Construct the URL for uploading file content
#         # Drive root is /drives/{drive-id}/root:/{path}:/content
#         # Or simpler: /users/{user-id}/drive/root:/{path}/{filename}:/content
        
#         # URL-encode the file name and path segments
#         encoded_folder_path = httpx.URL(folder_path).path.lstrip('/')
#         encoded_file_name = httpx.URL(file_name).path

#         # Construct the upload URL
#         # For simplicity, using the default drive of the user.
#         # Ensure 'root' or a valid folder_path is provided.
#         if folder_path and folder_path.lower() != 'root' and folder_path != '':
#             upload_url = f"{base_url}/users/{user_id}/drive/root:/{encoded_folder_path}/{encoded_file_name}:/content"
#         else:
#             upload_url = f"{base_url}/users/{user_id}/drive/root/children/{encoded_file_name}/content"


#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "text/plain" if isinstance(file_content, str) else "application/octet-stream" # Adjust content type based on content
#         }

#         async with httpx.AsyncClient() as client:
#             response = await client.put( # PUT is used for uploading content directly
#                 upload_url,
#                 headers=headers,
#                 content=file_content.encode('utf-8') if isinstance(file_content, str) else file_content
#             )
#             response.raise_for_status()
        
#         file_data = response.json()
#         return {"status": "success", "message": f"File '{file_name}' uploaded to '{folder_path}' successfully.", "file_id": file_data.get("id"), "file_name": file_data.get("name")}
#     except httpx.HTTPStatusError as e:
#         return {"status": "error", "message": f"Failed to upload file '{file_name}': HTTP Error {e.response.status_code} - {e.response.text}"}
#     except Exception as e:
#         return {"status": "error", "message": f"An error occurred during file upload: {type(e).__name__} - {e}"}

# async def download_file_from_onedrive(
#     auth_handler: MicrosoftGraphAuth,
#     user_id: str, # The user ID or userPrincipalName of the OneDrive owner
#     file_id: Optional[str] = None, # File ID
#     file_path: Optional[str] = None # Path to the file, e.g., "Documents/report.txt"
# ) -> dict:
#     """
#     Downloads a file from OneDrive via direct HTTP request.
#     Requires either file_id or file_path.

#     Args:
#         auth_handler: An authenticated MicrosoftGraphAuth instance.
#         user_id: The user ID or userPrincipalName whose OneDrive the file is in.
#         file_id: The ID of the file to download.
#         file_path: The path to the file in OneDrive (e.g., "Documents/MyFile.txt").

#     Returns:
#         A dictionary indicating success/failure and the file content (as bytes).
#     """
#     try:
#         if not file_id and not file_path:
#             return {"status": "error", "message": "Either file_id or file_path must be provided for download."}

#         access_token = auth_handler.get_access_token()
#         base_url = auth_handler.get_base_graph_url()

#         # Construct the URL for downloading file content
#         if file_id:
#             download_url = f"{base_url}/users/{user_id}/drive/items/{file_id}/content"
#         elif file_path:
#             encoded_file_path = httpx.URL(file_path).path.lstrip('/')
#             download_url = f"{base_url}/users/{user_id}/drive/root:/{encoded_file_path}:/content"
#         else:
#             return {"status": "error", "message": "Invalid file identifier for download."}
        
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Accept": "application/octet-stream" # Request binary stream
#         }

#         async with httpx.AsyncClient() as client:
#             response = await client.get(
#                 download_url,
#                 headers=headers
#             )
#             response.raise_for_status()
        
#         return {"status": "success", "message": f"File downloaded successfully.", "file_content": response.content}
#     except httpx.HTTPStatusError as e:
#         return {"status": "error", "message": f"Failed to download file: HTTP Error {e.response.status_code} - {e.response.text}"}
#     except Exception as e:
#         return {"status": "error", "message": f"An error occurred during file download: {type(e).__name__} - {e}"}

# async def list_files_in_folder(
#     auth_handler: MicrosoftGraphAuth,
#     user_id: str, # The user ID or userPrincipalName of the OneDrive owner
#     folder_path: str = "root" # Path to the folder in OneDrive, e.g., "Documents/Reports" or "root"
# ) -> Union[list[dict], dict]:
#     """
#     Lists files and folders in a specified OneDrive folder via direct HTTP request.

#     Args:
#         auth_handler: An authenticated MicrosoftGraphAuth instance.
#         user_id: The user ID or userPrincipalName whose OneDrive to list from.
#         folder_path: The path to the folder in OneDrive. Use "root" for the top-level drive.

#     Returns:
#         A list of dictionaries, each representing a file or folder.
#     """
#     try:
#         access_token = auth_handler.get_access_token()
#         base_url = auth_handler.get_base_graph_url()

#         # Construct the URL for listing children of a folder
#         if folder_path and folder_path.lower() != 'root' and folder_path != '':
#             list_url = f"{base_url}/users/{user_id}/drive/root:/{httpx.URL(folder_path).path.lstrip('/')}:/children"
#         else:
#             list_url = f"{base_url}/users/{user_id}/drive/root/children"
        
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Accept": "application/json"
#         }

#         async with httpx.AsyncClient() as client:
#             response = await client.get(
#                 list_url,
#                 headers=headers
#             )
#             response.raise_for_status()
        
#         response_data = response.json()
        
#         files_and_folders = []
#         if response_data and response_data.get('value'):
#             for item in response_data['value']:
#                 files_and_folders.append({
#                     "id": item.get("id"),
#                     "name": item.get("name"),
#                     "type": "folder" if "folder" in item else "file",
#                     "size": item.get("size"),
#                     "last_modified_date_time": item.get("lastModifiedDateTime")
#                 })
#         return files_and_folders
#     except httpx.HTTPStatusError as e:
#         return {"status": "error", "message": f"Failed to list files in '{folder_path}': HTTP Error {e.response.status_code} - {e.response.text}"}
#     except Exception as e:
#         return {"status": "error", "message": f"An error occurred during file listing: {type(e).__name__} - {e}"}

# async def delete_file_from_onedrive(
#     auth_handler: MicrosoftGraphAuth,
#     user_id: str, # The user ID or userPrincipalName of the OneDrive owner
#     file_id: Optional[str] = None, # File ID
#     file_path: Optional[str] = None # Path to the file, e.g., "Documents/report.txt"
# ) -> dict:
#     """
#     Deletes a file from OneDrive via direct HTTP request.
#     Requires either file_id or file_path.

#     Args:
#         auth_handler: An authenticated MicrosoftGraphAuth instance.
#         user_id: The user ID or userPrincipalName whose OneDrive the file is in.
#         file_id: The ID of the file to delete.
#         file_path: The path to the file in OneDrive (e.g., "Documents/MyFile.txt").

#     Returns:
#         A dictionary indicating success/failure.
#     """
#     try:
#         if not file_id and not file_path:
#             return {"status": "error", "message": "Either file_id or file_path must be provided for deletion."}

#         access_token = auth_handler.get_access_token()
#         base_url = auth_handler.get_base_graph_url()

#         # Construct the URL for deleting a file
#         if file_id:
#             delete_url = f"{base_url}/users/{user_id}/drive/items/{file_id}"
#         elif file_path:
#             encoded_file_path = httpx.URL(file_path).path.lstrip('/')
#             delete_url = f"{base_url}/users/{user_id}/drive/root:/{encoded_file_path}"
#         else:
#             return {"status": "error", "message": "Invalid file identifier for deletion."}
        
#         headers = {
#             "Authorization": f"Bearer {access_token}"
#         }

#         async with httpx.AsyncClient() as client:
#             response = await client.delete( # Use DELETE method
#                 delete_url,
#                 headers=headers
#             )
#             response.raise_for_status() # 204 No Content for successful delete is a success

#         return {"status": "success", "message": f"File deleted successfully."}
#     except httpx.HTTPStatusError as e:
#         return {"status": "error", "message": f"Failed to delete file: HTTP Error {e.response.status_code} - {e.response.text}"}
#     except Exception as e:
#         return {"status": "error", "message": f"An error occurred during file deletion: {type(e).__name__} - {e}"}

# # Example Usage (for testing purposes)
# async def main():
#     auth_handler = MicrosoftGraphAuth()
    
#     # IMPORTANT: Replace with the actual email address/UPN of the OneDrive owner
#     # For application permissions, this user must exist and the app must have Files.ReadWrite.All permission.
#     onedrive_owner_id = "ginura.b@intellistrata.com.au" 
#     test_folder_path = "AI_Agent_Test_Files" # A new folder for testing
#     test_file_name = "test_document.txt"
#     test_file_content = "This is a test file created by the Microsoft 365 Intelligent Agent.\n" + \
#                         f"Current time: {datetime.now().isoformat()}."

#     print(f"\n--- Testing OneDrive Operations for {onedrive_owner_id} ---")

#     # --- Test 1: Upload a file ---
#     print(f"\nAttempting to upload file '{test_file_name}' to '{test_folder_path}'...")
#     upload_result = await upload_file_to_onedrive(
#         auth_handler,
#         onedrive_owner_id,
#         test_folder_path,
#         test_file_name,
#         test_file_content
#     )
#     print(f"Upload file result: {upload_result}")
    
#     uploaded_file_id = upload_result.get("file_id")
#     uploaded_file_name = upload_result.get("file_name")

#     # --- Test 2: List files in the test folder ---
#     if upload_result.get("status") == "success":
#         print(f"\nAttempting to list files in '{test_folder_path}'...")
#         list_result = await list_files_in_folder(auth_handler, onedrive_owner_id, test_folder_path)
#         if isinstance(list_result, dict) and list_result.get("status") == "error":
#             print(f"Error listing files: {list_result['message']}")
#         else:
#             print(f"Found {len(list_result)} items in '{test_folder_path}':")
#             for item in list_result:
#                 print(f"  - Name: {item['name']}, Type: {item['type']}, ID: {item['id']}")
#                 if item['name'] == test_file_name and item['type'] == 'file':
#                     uploaded_file_id = item['id'] # Confirm ID if found via list
#     else:
#         print("\nSkipping list and download tests as upload failed.")

#     # --- Test 3: Download the uploaded file (if uploaded successfully) ---
#     if uploaded_file_id:
#         print(f"\nAttempting to download file '{uploaded_file_name}' (ID: {uploaded_file_id})...")
#         download_result = await download_file_from_onedrive(
#             auth_handler,
#             onedrive_owner_id,
#             file_id=uploaded_file_id # Use ID for download
#         )
#         print(f"Download file result: {download_result['status']}")
#         if download_result.get("status") == "success":
#             downloaded_content = download_result.get("file_content", b"").decode('utf-8')
#             print(f"  Downloaded content snippet: {downloaded_content[:150]}...")
#             if test_file_content == downloaded_content:
#                 print("  Content matches original!")
#             else:
#                 print("  Content MISMATCH!")
#     else:
#         print("\nSkipping download test as no file ID available.")

#     # --- Test 4: Delete the uploaded file (if uploaded successfully) ---
#     if uploaded_file_id:
#         print(f"\nAttempting to delete file '{uploaded_file_name}' (ID: {uploaded_file_id})...")
#         delete_result = await delete_file_from_onedrive(auth_handler, onedrive_owner_id, file_id=uploaded_file_id)
#         print(f"Delete file result: {delete_result}")
#     else:
#         print("\nSkipping delete test as no file ID available.")

#     # --- Optional: Try to clean up the test folder if empty ---
#     print(f"\nAttempting to delete test folder '{test_folder_path}' if empty...")
#     try:
#         # Get folder ID by path first
#         base_list_url = f"{auth_handler.get_base_graph_url()}/users/{onedrive_owner_id}/drive/root/children"
#         headers = {"Authorization": f"Bearer {auth_handler.get_access_token()}", "Accept": "application/json"}
#         async with httpx.AsyncClient() as client:
#             list_response = await client.get(base_list_url, headers=headers, params={"$filter": f"name eq '{test_folder_path}' and folder ne null"})
#             list_response.raise_for_status()
#             folders = list_response.json().get('value', [])
#             if folders and folders[0].get('id'):
#                 folder_to_delete_id = folders[0]['id']
#                 # Check if folder is empty before attempting deletion
#                 folder_contents = await list_files_in_folder(auth_handler, onedrive_owner_id, test_folder_path)
#                 if isinstance(folder_contents, list) and not folder_contents: # Only delete if it's an empty list
#                     cleanup_delete_result = await delete_file_from_onedrive(auth_handler, onedrive_owner_id, file_id=folder_to_delete_id)
#                     print(f"Cleanup delete folder result: {cleanup_delete_result}")
#                 else:
#                     print(f"Folder '{test_folder_path}' is not empty, skipping folder deletion.")
#             else:
#                 print(f"Folder '{test_folder_path}' not found, no folder to delete.")
#     except Exception as e:
#         print(f"Error during folder cleanup: {type(e).__name__} - {e}")


# if __name__ == "__main__":
#     asyncio.run(main())




















import asyncio
import httpx
import os
import json
from datetime import datetime
from typing import Optional, Union
from urllib.parse import quote_plus # Import for proper URL encoding of path segments

from microsoft_graph.auth import MicrosoftGraphAuth

async def upload_file_to_onedrive(
    auth_handler: MicrosoftGraphAuth,
    user_id: str, # The user ID or userPrincipalName of the OneDrive owner
    folder_path: str, # Path to the folder in OneDrive, e.g., "Documents/Reports" or "General"
    file_name: str,   # Name of the file to upload, e.g., "my_document.txt"
    file_content: Union[str, bytes] # Content of the file as string or bytes
) -> dict:
    """
    Uploads a file to a specified OneDrive folder via direct HTTP request.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance.
        user_id: The user ID or userPrincipalName whose OneDrive the file will be uploaded to.
        folder_path: The path to the target folder in OneDrive (e.g., "Documents", "MyFolder/Subfolder").
                     Use "root" or "" for the top-level drive.
        file_name: The name of the file, including extension (e.g., "report.docx").
        file_content: The content of the file. Can be a string (for text files) or bytes.

    Returns:
        A dictionary indicating success/failure and file details.
    """
    try:
        access_token = auth_handler.get_access_token()
        base_url = auth_handler.get_base_graph_url()

        encoded_file_name = quote_plus(file_name) # Encode filename

        if folder_path and folder_path.lower() != 'root' and folder_path != '':
            encoded_folder_path_segments = '/'.join(quote_plus(s) for s in folder_path.split('/') if s)
            upload_url = f"{base_url}/users/{user_id}/drive/root:/{encoded_folder_path_segments}/{encoded_file_name}:/content"
        else:
            upload_url = f"{base_url}/users/{user_id}/drive/root/children/{encoded_file_name}/content"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "text/plain" if isinstance(file_content, str) else "application/octet-stream"
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(
                upload_url,
                headers=headers,
                content=file_content.encode('utf-8') if isinstance(file_content, str) else file_content
            )
            response.raise_for_status()
        
        file_data = response.json()
        return {"status": "success", "message": f"File '{file_name}' uploaded to '{folder_path}' successfully.", "file_id": file_data.get("id"), "file_name": file_data.get("name")}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to upload file '{file_name}': HTTP Error {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during file upload: {type(e).__name__} - {e}"}

async def download_file_from_onedrive(
    auth_handler: MicrosoftGraphAuth,
    user_id: str, # The user ID or userPrincipalName of the OneDrive owner
    file_id: Optional[str] = None, # File ID
    file_path: Optional[str] = None # Path to the file, e.g., "Documents/report.txt"
) -> dict:
    """
    Downloads a file from OneDrive via direct HTTP request.
    Requires either file_id or file_path.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance.
        user_id: The user ID or userPrincipalName whose OneDrive the file is in.
        file_id: The ID of the file to download.
        file_path: The path to the file in OneDrive (e.g., "Documents/MyFile.txt").

    Returns:
        A dictionary indicating success/failure and the file content (as bytes).
    """
    try:
        if not file_id and not file_path:
            return {"status": "error", "message": "Either file_id or file_path must be provided for download."}

        access_token = auth_handler.get_access_token()
        base_url = auth_handler.get_base_graph_url()

        if file_id:
            download_url = f"{base_url}/users/{user_id}/drive/items/{file_id}/content"
        elif file_path:
            encoded_file_path_segments = '/'.join(quote_plus(s) for s in file_path.split('/') if s)
            download_url = f"{base_url}/users/{user_id}/drive/root:/{encoded_file_path_segments}:/content"
        else:
            return {"status": "error", "message": "Invalid file identifier for download."}
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/octet-stream"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                download_url,
                headers=headers
            )
            response.raise_for_status()
        
        return {"status": "success", "message": f"File downloaded successfully.", "file_content": response.content}
    except httpx.HTTPStatusError as e:
        # Provide more specific HTTP error details for debugging download failures
        return {"status": "error", "message": f"Failed to download file: HTTP Error {e.response.status_code} - {e.response.text} URL: {e.request.url}"}
    except Exception as e:
        # Provide more specific generic error details for debugging download failures
        return {"status": "error", "message": f"An unexpected error occurred during file download: {type(e).__name__} - {e}"}

async def list_files_in_folder(
    auth_handler: MicrosoftGraphAuth,
    user_id: str, # The user ID or userPrincipalName of the OneDrive owner
    folder_path: str = "root" # Path to the folder in OneDrive, e.g., "Documents/Reports" or "root"
) -> Union[list[dict], dict]:
    """
    Lists files and folders in a specified OneDrive folder via direct HTTP request.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance.
        user_id: The user ID or userPrincipalName whose OneDrive to list from.
        folder_path: The path to the folder in OneDrive. Use "root" for the top-level drive.

    Returns:
        A list of dictionaries, each representing a file or folder.
    """
    try:
        access_token = auth_handler.get_access_token()
        base_url = auth_handler.get_base_graph_url()

        if folder_path and folder_path.lower() != 'root' and folder_path != '':
            encoded_path_segments = '/'.join(quote_plus(s) for s in folder_path.split('/') if s)
            list_url = f"{base_url}/users/{user_id}/drive/root:/{encoded_path_segments}:/children"
        else:
            list_url = f"{base_url}/users/{user_id}/drive/root/children"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                list_url,
                headers=headers
            )
            response.raise_for_status()
        
        response_data = response.json()
        
        files_and_folders = []
        if response_data and response_data.get('value'):
            for item in response_data['value']:
                files_and_folders.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": "folder" if "folder" in item else "file",
                    "size": item.get("size"),
                    "last_modified_date_time": item.get("lastModifiedDateTime")
                })
        return files_and_folders
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to list files in '{folder_path}': HTTP Error {e.response.status_code} - {e.response.text} URL: {e.request.url}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during file listing: {type(e).__name__} - {e}"}

async def delete_file_from_onedrive(
    auth_handler: MicrosoftGraphAuth,
    user_id: str, # The user ID or userPrincipalName of the OneDrive owner
    file_id: Optional[str] = None, # File ID
    file_path: Optional[str] = None # Path to the file, e.g., "Documents/report.txt"
) -> dict:
    """
    Deletes a file from OneDrive via direct HTTP request.
    Requires either file_id or file_path.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance.
        user_id: The user ID or userPrincipalName whose OneDrive the file is in.
        file_id: The ID of the file to delete.
        file_path: The path to the file in OneDrive (e.g., "Documents/MyFile.txt").

    Returns:
        A dictionary indicating success/failure.
    """
    try:
        if not file_id and not file_path:
            return {"status": "error", "message": "Either file_id or file_path must be provided for deletion."}

        access_token = auth_handler.get_access_token()
        base_url = auth_handler.get_base_graph_url()

        if file_id:
            delete_url = f"{base_url}/users/{user_id}/drive/items/{file_id}"
        elif file_path:
            encoded_file_path_segments = '/'.join(quote_plus(s) for s in file_path.split('/') if s)
            delete_url = f"{base_url}/users/{user_id}/drive/root:/{encoded_file_path_segments}"
        else:
            return {"status": "error", "message": "Invalid file identifier for deletion."}
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.delete( # Use DELETE method
                delete_url,
                headers=headers
            )
            response.raise_for_status() # 204 No Content for successful delete is a success

        return {"status": "success", "message": f"File deleted successfully."}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to delete file: HTTP Error {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during file deletion: {type(e).__name__} - {e}"}

# Example Usage (for testing purposes)
async def main():
    auth_handler = MicrosoftGraphAuth()
    
    # IMPORTANT: Replace with the actual email address/UPN of the OneDrive owner
    # For application permissions, this user must exist and the app must have Files.ReadWrite.All permission.
    onedrive_owner_id = "ginura.b@intellistrata.com.au" 
    test_folder_path = "AI_Agent_Test_Files" # A new folder for testing
    test_file_name = "test_document.txt"
    test_file_content = "This is a test file created by the Microsoft 365 Intelligent Agent.\n" + \
                        f"Current time: {datetime.now().isoformat()}."

    print(f"\n--- Testing OneDrive Operations for {onedrive_owner_id} ---")

    # --- Test 1: Upload a file ---
    print(f"\nAttempting to upload file '{test_file_name}' to '{test_folder_path}'...")
    upload_result = await upload_file_to_onedrive(
        auth_handler,
        onedrive_owner_id,
        test_folder_path,
        test_file_name,
        test_file_content
    )
    print(f"Upload file result: {upload_result}")
    
    uploaded_file_id = upload_result.get("file_id")
    uploaded_file_name = upload_result.get("file_name")

    # Give OneDrive a moment to process the upload/folder creation before listing
    await asyncio.sleep(2) 

    # --- Test 2: List files in the test folder ---
    if upload_result.get("status") == "success":
        print(f"\nAttempting to list files in '{test_folder_path}'...")
        list_result = await list_files_in_folder(auth_handler, onedrive_owner_id, test_folder_path)
        if isinstance(list_result, dict) and list_result.get("status") == "error":
            print(f"Error listing files: {list_result['message']}")
        else:
            print(f"Found {len(list_result)} items in '{test_folder_path}':")
            for item in list_result:
                print(f"  - Name: {item['name']}, Type: {item['type']}, ID: {item['id']}")
                if item['name'] == test_file_name and item['type'] == 'file':
                    uploaded_file_id = item['id'] # Confirm ID if found via list
    else:
        print("\nSkipping list and download tests as upload failed.")

    # --- Test 3: Download the uploaded file (if uploaded successfully) ---
    if uploaded_file_id:
        print(f"\nAttempting to download file '{uploaded_file_name}' (ID: {uploaded_file_id})...")
        download_result = await download_file_from_onedrive(
            auth_handler,
            onedrive_owner_id,
            file_id=uploaded_file_id # Use ID for download
        )
        print(f"Download file result: {download_result['status']}")
        if download_result.get("status") == "success":
            downloaded_content = download_result.get("file_content", b"").decode('utf-8')
            print(f"  Downloaded content snippet: {downloaded_content[:150]}...")
            if test_file_content == downloaded_content:
                print("  Content matches original!")
            else:
                print("  Content MISMATCH!")
    else:
        print("\nSkipping download test as no file ID available.")

    # --- Test 4: Delete the uploaded file (if uploaded successfully) ---
    if uploaded_file_id:
        print(f"\nAttempting to delete file '{uploaded_file_name}' (ID: {uploaded_file_id})...")
        delete_result = await delete_file_from_onedrive(auth_handler, onedrive_owner_id, file_id=uploaded_file_id)
        print(f"Delete file result: {delete_result}")
    else:
        print("\nSkipping delete test as no file ID available.")

    # --- Optional: Try to clean up the test folder if empty ---
    print(f"\nAttempting to delete test folder '{test_folder_path}' if empty...")
    try:
        # Get folder ID by path first (list children of root and filter by name)
        base_list_url = f"{auth_handler.get_base_graph_url()}/users/{onedrive_owner_id}/drive/root/children"
        headers = {"Authorization": f"Bearer {auth_handler.get_access_token()}", "Accept": "application/json"}
        async with httpx.AsyncClient() as client:
            # Use params for cleaner query string construction
            list_response = await client.get(base_list_url, headers=headers, params={"$filter": f"name eq '{test_folder_path}' and folder ne null"})
            list_response.raise_for_status()
            folders = list_response.json().get('value', [])
            if folders and folders[0].get('id'):
                folder_to_delete_id = folders[0]['id']
                # Check if folder is empty before attempting deletion
                # Re-fetch contents of this specific folder for emptiness check
                current_folder_contents = await list_files_in_folder(auth_handler, onedrive_owner_id, test_folder_path)
                if isinstance(current_folder_contents, list) and not current_folder_contents: # Only delete if it's an empty list
                    cleanup_delete_result = await delete_file_from_onedrive(auth_handler, onedrive_owner_id, file_id=folder_to_delete_id)
                    print(f"Cleanup delete folder result: {cleanup_delete_result}")
                else:
                    print(f"Folder '{test_folder_path}' is not empty, skipping folder deletion.")
            else:
                print(f"Folder '{test_folder_path}' not found, no folder to delete.")
    except Exception as e:
        print(f"Error during folder cleanup: {type(e).__name__} - {e}")


if __name__ == "__main__":
    asyncio.run(main())