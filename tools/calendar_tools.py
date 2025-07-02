import datetime

CALENDAR_TOOLS = [
    {
        "type": "function",
        "name": "create_calendar_event", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "create_calendar_event",
            "description": "Creates a new event in an Outlook calendar for a specified user. Requires start and end times, subject, and optional attendees and body content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The User Principal Name (UPN) or Object ID of the calendar owner (e.g., 'ai_agent_dev2@intellistrata.com.au')."
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject or title of the calendar event."
                    },
                    "start_time_str": {
                        "type": "string",
                        "description": "The start date and time of the event in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SS'). For example, '2025-07-25T09:00:00'."
                    },
                    "end_time_str": {
                        "type": "string",
                        "description": "The end date and time of the event in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SS'). For example, '2025-07-25T10:00:00'."
                    },
                    "timezone_str": {
                        "type": "string",
                        "description": "The IANA timezone ID for the start and end times, e.g., 'UTC', 'America/New_York', 'Asia/Colombo'. Defaults to 'UTC'."
                    },
                    "attendees_emails": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An optional list of email addresses of attendees to invite to the event."
                    },
                    "body_content": {
                        "type": "string",
                        "description": "Optional body content for the event (e.g., meeting agenda, notes)."
                    }
                },
                "required": ["user_id", "subject", "start_time_str", "end_time_str"]
            }
        }
    },
    {
        "type": "function",
        "name": "update_calendar_event", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "update_calendar_event",
            "description": "Updates an existing calendar event identified by its ID for a specified user. Provide the event ID and a dictionary of fields to update.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The User Principal Name (UPN) or Object ID of the calendar owner (e.g., 'ai_agent_dev2@intellistrata.com.au')."
                    },
                    "event_id": {
                        "type": "string",
                        "description": "The unique ID of the calendar event to be updated. This ID is typically obtained from a 'create' or 'list' operation."
                    },
                    "updates": {
                        "type": "object",
                        "description": "A JSON object containing the fields to update. For example, {'subject': 'New Subject', 'body': {'contentType': 'Text', 'content': 'Updated agenda.'}}.",
                        "example": {"subject": "Revised Meeting"}
                    }
                },
                "required": ["user_id", "event_id", "updates"]
            }
        }
    },
    {
        "type": "function",
        "name": "delete_calendar_event", # <-- ADDED THIS TOP-LEVEL NAME FIELD
        "function": {
            "name": "delete_calendar_event",
            "description": "Deletes a calendar event identified by its ID for a specified user. This action is permanent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The User Principal Name (UPN) or Object ID of the calendar owner (e.g., 'ai_agent_dev2@intellistrata.com.au')."
                    },
                    "event_id": {
                        "type": "string",
                        "description": "The unique ID of the calendar event to be deleted."
                    }
                },
                "required": ["user_id", "event_id"]
            }
        }
    }
]