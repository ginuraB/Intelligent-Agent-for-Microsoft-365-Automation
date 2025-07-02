ONEDRIVE_FILE_TOOLS = [
    {
        "type": "function",
        "name": "upload_file_to_onedrive", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "upload_file_to_onedrive",
            "description": "Uploads a file with specified content to a designated folder in a user's OneDrive. If the folder does not exist, it will be created.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The User Principal Name (UPN) of the OneDrive owner (e.g., 'ai_agent_dev2@intellistrata.com.au')."
                    },
                    "folder_path": {
                        "type": "string",
                        "description": "The path to the target folder in OneDrive (e.g., 'Documents', 'Reports/Q3'). Use 'root' or an empty string for the top-level drive."
                    },
                    "file_name": {
                        "type": "string",
                        "description": "The name of the file to upload, including its extension (e.g., 'meeting_notes.txt', 'image.jpg')."
                    },
                    "file_content": {
                        "type": "string",
                        "description": "The content of the file to be uploaded. For text files, provide the text. For binary files, indicate that binary content is needed (the agent will handle encoding)."
                    }
                },
                "required": ["user_id", "folder_path", "file_name", "file_content"]
            }
        }
    },
    {
        "type": "function",
        "name": "list_files_in_folder", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "list_files_in_folder",
            "description": "Lists files and subfolders within a specified folder in a user's OneDrive. Returns summary details like name, type (file/folder), and ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The User Principal Name (UPN) of the OneDrive owner (e.g., 'ai_agent_dev2@intellistrata.com.au')."
                    },
                    "folder_path": {
                        "type": "string",
                        "description": "The path to the folder in OneDrive to list contents from (e.g., 'Documents', 'Shared Files/Project X'). Use 'root' for the top-level drive. Defaults to 'root'."
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "name": "download_file_from_onedrive", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "download_file_from_onedrive",
            "description": "Downloads the content of a specific file from a user's OneDrive. The file can be identified by its ID or its full path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The User Principal Name (UPN) of the OneDrive owner (e.g., 'ai_agent_dev2@intellistrata.com.au')."
                    },
                    "file_id": {
                        "type": "string",
                        "description": "The unique ID of the file to download. Provide this if available."
                    },
                    "file_path": {
                        "type": "string",
                        "description": "The full path to the file in OneDrive (e.g., 'Documents/report.pdf'). Use this if file_id is not available."
                    }
                },
                "required": ["user_id"]
                # Note: Either file_id or file_path will be required by the Python function's internal logic.
                # The model will infer this from the descriptions and examples.
            }
        }
    },
    {
        "type": "function",
        "name": "delete_file_from_onedrive", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "delete_file_from_onedrive",
            "description": "Deletes a specific file or folder from a user's OneDrive. The item can be identified by its ID or its full path. This action is permanent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The User Principal Name (UPN) of the OneDrive owner (e.g., 'ai_agent_dev2@intellistrata.com.au')."
                    },
                    "file_id": {
                        "type": "string",
                        "description": "The unique ID of the file or folder to delete. Provide this if available."
                    },
                    "file_path": {
                        "type": "string",
                        "description": "The full path to the file or folder in OneDrive (e.g., 'Documents/old_report.txt', 'Archive/OldFolder'). Use this if file_id is not available."
                    }
                },
                "required": ["user_id"]
                # Note: Either file_id or file_path will be required by the Python function's internal logic.
            }
        }
    }
]