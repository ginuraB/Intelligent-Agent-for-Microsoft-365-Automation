OUTLOOK_EMAIL_TOOLS = [
    {
        "type": "function",
        "name": "send_outlook_email", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "send_outlook_email",
            "description": "Sends an email to a specified recipient with a given subject and body content. Requires the email address of the sender's mailbox (userPrincipalName) for application permissions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient_email": {
                        "type": "string",
                        "description": "The email address of the primary recipient."
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject line of the email."
                    },
                    "body_content": {
                        "type": "string",
                        "description": "The main content of the email body (plain text or HTML)."
                    }
                },
                "required": ["recipient_email", "subject", "body_content"]
            }
        }
    },
    {
        "type": "function",
        "name": "list_outlook_emails", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "list_outlook_emails",
            "description": "Lists emails from a specified Outlook mailbox folder (e.g., 'Inbox', 'JunkEmail', 'JunkEmail', 'SentItems', 'Drafts'). Can filter by unread status or importance. Returns a list of email summaries (id, subject, from, read status, importance).",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The User Principal Name (UPN) or Object ID of the mailbox owner (e.g., 'ai_agent_dev2@intellistrata.com.au')."
                    },
                    "folder_name": {
                        "type": "string",
                        "description": "The name of the mailbox folder to list emails from (e.g., 'Inbox', 'JunkEmail', 'SentItems'). Defaults to 'Inbox'."
                    },
                    "filter_unread": {
                        "type": "boolean",
                        "description": "Set to true to only retrieve unread emails. Defaults to false."
                    },
                    "filter_importance": {
                        "type": "string",
                        "enum": ["high", "normal", "low"],
                        "description": "Filter emails by importance level ('high', 'normal', 'low'). Defaults to no importance filter."
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "name": "get_outlook_email_content", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "get_outlook_email_content",
            "description": "Retrieves the full body content and details of a specific email using its unique ID from a user's mailbox. Useful after listing emails.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The User Principal Name (UPN) or Object ID of the mailbox owner (e.g., 'ai_agent_dev2@intellistrata.com.au')."
                    },
                    "email_id": {
                        "type": "string",
                        "description": "The unique ID of the email to retrieve its content."
                    }
                },
                "required": ["user_id", "email_id"]
            }
        }
    }
]