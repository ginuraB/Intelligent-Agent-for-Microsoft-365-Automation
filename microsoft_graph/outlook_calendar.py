import asyncio
import httpx
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from microsoft_graph.auth import MicrosoftGraphAuth

async def create_calendar_event(
    auth_handler: MicrosoftGraphAuth,
    user_id: str, # The user ID or userPrincipalName of the calendar owner
    subject: str,
    start_time_str: str, # e.g., "2025-07-25T09:00:00" (ISO 8601 format)
    end_time_str: str,   # e.g., "2025-07-25T10:00:00"
    timezone_str: str = "UTC", # e.g., "America/New_York", "UTC", "Asia/Colombo"
    attendees_emails: Optional[list[str]] = None,
    body_content: Optional[str] = None
) -> dict:
    """
    Creates a new calendar event in Outlook Calendar via direct HTTP request.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance.
        user_id: The user ID or userPrincipalName whose calendar the event will be created in.
        subject: The subject/title of the event.
        start_time_str: The start date and time of the event in ISO 8601 format (e.g., "YYYY-MM-DDTHH:MM:SS").
        end_time_str: The end date and time of the event in ISO 8601 format.
        timezone_str: The timezone for the start and end times.
        attendees_emails: Optional list of email addresses for attendees.
        body_content: Optional content for the event body.

    Returns:
        A dictionary indicating success/failure and event details.
    """
    try:
        access_token = auth_handler.get_access_token() # get_access_token is sync, but called from async context
        base_url = auth_handler.get_base_graph_url()

        event_body = {
            "subject": subject,
            "start": {
                "dateTime": start_time_str,
                "timeZone": timezone_str
            },
            "end": {
                "dateTime": end_time_str,
                "timeZone": timezone_str
            },
            "isOnlineMeeting": False # Set to True for Teams meeting etc.
        }

        if body_content:
            event_body["body"] = {"contentType": "Text", "content": body_content}

        if attendees_emails:
            attendees = []
            for email in attendees_emails:
                attendees.append({
                    "emailAddress": {"address": email},
                    "type": "required" # Or 'optional'
                })
            event_body["attendees"] = attendees

        create_event_url = f"{base_url}/users/{user_id}/calendar/events"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                create_event_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=event_body
            )
            response.raise_for_status()
        
        event_data = response.json()
        return {"status": "success", "message": "Calendar event created successfully.", "event_id": event_data.get("id"), "event_subject": event_data.get("subject")}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to create event: HTTP Error {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during event creation: {type(e).__name__} - {e}"}

async def update_calendar_event(
    auth_handler: MicrosoftGraphAuth,
    user_id: str,
    event_id: str,
    updates: dict
) -> dict:
    """
    Updates an existing calendar event via direct HTTP request.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance.
        user_id: The user ID or userPrincipalName whose calendar the event belongs to.
        event_id: The ID of the event to update.
        updates: A dictionary of fields to update (e.g., {"subject": "New Subject", "start": {"dateTime": "...", "timeZone": "..."}}).

    Returns:
        A dictionary indicating success/failure.
    """
    try:
        access_token = auth_handler.get_access_token()
        base_url = auth_handler.get_base_graph_url()

        update_event_url = f"{base_url}/users/{user_id}/calendar/events/{event_id}"

        async with httpx.AsyncClient() as client:
            response = await client.patch( # Use PATCH for partial updates
                update_event_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=updates
            )
            response.raise_for_status()
        
        return {"status": "success", "message": f"Calendar event {event_id} updated successfully."}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to update event {event_id}: HTTP Error {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during event update: {type(e).__name__} - {e}"}

async def delete_calendar_event(
    auth_handler: MicrosoftGraphAuth,
    user_id: str,
    event_id: str
) -> dict:
    """
    Deletes a calendar event via direct HTTP request.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance.
        user_id: The user ID or userPrincipalName whose calendar the event belongs to.
        event_id: The ID of the event to delete.

    Returns:
        A dictionary indicating success/failure.
    """
    try:
        access_token = auth_handler.get_access_token()
        base_url = auth_handler.get_base_graph_url()

        delete_event_url = f"{base_url}/users/{user_id}/calendar/events/{event_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete( # Use DELETE method
                delete_event_url,
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )
            response.raise_for_status() # 204 No Content for successful delete is a success

        return {"status": "success", "message": f"Calendar event {event_id} deleted successfully."}
    except httpx.HTTPStatusError as e:
        # 404 Not Found is common if event already deleted or ID is wrong
        return {"status": "error", "message": f"Failed to delete event {event_id}: HTTP Error {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during event deletion: {type(e).__name__} - {e}"}

# Example Usage (for testing purposes)
async def main():
    auth_handler = MicrosoftGraphAuth()
    
    # IMPORTANT: Replace with the actual email address/UPN of the calendar owner
    # For application permissions, this user must exist and the app must have Calendars.ReadWrite permission.
    calendar_owner_id = "ai_agent_dev2@intellistrata.com.au" 

    print(f"\n--- Testing Calendar Operations for {calendar_owner_id} ---")

    # --- Test 1: Create an event ---
    print("\nAttempting to create a new calendar event...")
    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(hours=1)).isoformat(timespec='seconds').replace('+00:00', 'Z')
    end_time = (now + timedelta(hours=2)).isoformat(timespec='seconds').replace('+00:00', 'Z')
    
    create_result = await create_calendar_event(
        auth_handler,
        calendar_owner_id,
        "Team Sync Meeting (AI Agent)",
        start_time,
        end_time,
        "UTC",
        ["ai_agent_dev2@intellistrata.com.au"] # Invite self for testing
    )
    print(f"Create event result: {create_result}")
    
    new_event_id = create_result.get("event_id")

    # --- Test 2: Update the event (if created successfully) ---
    if new_event_id:
        print(f"\nAttempting to update event {new_event_id}...")
        updated_subject = "Updated: Team Sync Meeting (AI Agent)"
        update_result = await update_calendar_event(
            auth_handler,
            calendar_owner_id,
            new_event_id,
            {"subject": updated_subject, "body": {"contentType": "Text", "content": "Updated body content."}}
        )
        print(f"Update event result: {update_result}")

        # --- Test 3: Delete the event (if updated successfully) ---
        if update_result.get("status") == "success":
            print(f"\nAttempting to delete event {new_event_id}...")
            delete_result = await delete_calendar_event(auth_handler, calendar_owner_id, new_event_id)
            print(f"Delete event result: {delete_result}")
        else:
            print(f"Skipping delete as update failed for event {new_event_id}.")
            # Still try to delete if create was successful but update failed, for cleanup
            print(f"\nAttempting to delete event {new_event_id} for cleanup...")
            delete_result = await delete_calendar_event(auth_handler, calendar_owner_id, new_event_id)
            print(f"Cleanup delete result: {delete_result}")
    else:
        print("\nSkipping update and delete tests as event creation failed.")

if __name__ == "__main__":
    asyncio.run(main())