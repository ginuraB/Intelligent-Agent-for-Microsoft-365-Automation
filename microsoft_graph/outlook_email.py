import asyncio
import httpx
import json # To manually serialize JSON bodies
from typing import Optional, Union

from microsoft_graph.auth import MicrosoftGraphAuth # Import the auth handler

# We are no longer using msgraph-sdk's GraphServiceClient or any msgraph.generated.models.*
# All Graph API calls are made directly using httpx.

async def send_outlook_email(
    auth_handler: MicrosoftGraphAuth, # Pass the auth_handler directly
    recipient_email: str,
    subject: str,
    body_content: str
) -> dict:
    """
    Sends an email using the Microsoft Graph API via direct HTTP request with httpx.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance to get the token and base URL.
        recipient_email: The email address of the recipient.
        subject: The subject of the email.
        body_content: The content of the email body (plain text or HTML).

    Returns:
        A dictionary indicating success or failure.
    """
    try:
        # Get access token and base URL from the auth_handler (NO AWAIT HERE, as get_access_token is now SYNC)
        access_token = auth_handler.get_access_token()
        base_url = auth_handler.get_base_graph_url()

        message_payload = {
            "subject": subject,
            "body": {
                "contentType": "Text", # Or 'Html'
                "content": body_content
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient_email
                    }
                }
            ]
        }
        
        request_body = {
            "message": message_payload,
            "saveToSentItems": True
        }

        sender_mailbox_id = "ai_agent_dev2@intellistrata.com.au"
        send_mail_url = f"{base_url}/users/{sender_mailbox_id}/sendMail"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                send_mail_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=request_body
            )
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        return {"status": "success", "message": f"Email sent to {recipient_email} from {sender_mailbox_id} with subject '{subject}'."}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to send email: HTTP Error {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send email: {type(e).__name__} - {e}"}


async def list_outlook_emails(
    auth_handler: MicrosoftGraphAuth, # Pass the auth_handler directly
    user_id: str, # The user ID or userPrincipalName of the mailbox
    folder_name: str = "Inbox",
    filter_unread: bool = False,
    filter_importance: Optional[str] = None # e.g., 'high', 'normal', 'low'
) -> Union[list[dict], dict]:
    """
    Lists emails from a specified Outlook folder with optional filters, using direct HTTP request with httpx.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance to get the token and base URL.
        user_id: The user ID or userPrincipalName of the mailbox to read from.
        folder_name: The name of the mailbox folder (e.g., "Inbox", "JunkEmail", "SentItems").
        filter_unread: If True, only retrieve unread emails.
        filter_importance: Filter by importance ('high', 'normal', 'low').

    Returns:
        A list of dictionaries, each representing an email.
    """
    try:
        # Get access token and base URL from the auth_handler (NO AWAIT HERE)
        access_token = auth_handler.get_access_token()
        base_url = auth_handler.get_base_graph_url()

        odata_filter_parts = []
        if filter_unread:
            odata_filter_parts.append("isRead eq false")
        if filter_importance:
            odata_filter_parts.append(f"importance eq '{filter_importance.lower()}'")
        
        filter_string = " and ".join(odata_filter_parts) if odata_filter_parts else None
        
        select_fields_str = "id,subject,from,receivedDateTime,isRead,importance,hasAttachments,bodyPreview"

        request_url = f"{base_url}/users/{user_id}/mailFolders/{folder_name}/messages"
        
        query_params_list = []
        query_params_list.append(f"$select={select_fields_str}")
        query_params_list.append(f"$top=10") # Limit results for efficiency

        if filter_string:
            query_params_list.append(f"$filter={filter_string}")
        
        full_request_url = f"{request_url}?{'&'.join(query_params_list)}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                full_request_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
        
        response_data = response.json()
        
        emails = []
        if response_data and response_data.get('value'):
            for message in response_data['value']:
                emails.append({
                    "id": message.get("id"),
                    "subject": message.get("subject"),
                    "from": message.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                    "received_date_time": message.get("receivedDateTime"),
                    "is_read": message.get("isRead"),
                    "importance": message.get("importance"),
                    "has_attachments": message.get("hasAttachments"),
                    "body_preview": message.get("bodyPreview", "")
                })
        return emails
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to list emails from {folder_name}: HTTP Error {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during email listing: {type(e).__name__} - {e}"}


async def get_outlook_email_content(
    auth_handler: MicrosoftGraphAuth, # Pass the auth_handler directly
    user_id: str,
    email_id: str
) -> dict:
    """
    Retrieves the full content of a specific email by its ID using direct HTTP request with httpx.

    Args:
        auth_handler: An authenticated MicrosoftGraphAuth instance to get the token.
        user_id: The user ID or userPrincipalName of the mailbox.
        email_id: The ID of the email to retrieve.

    Returns:
        A dictionary containing the email details and body content.
    """
    try:
        # Get access token and base URL from the auth_handler (NO AWAIT HERE)
        access_token = auth_handler.get_access_token()
        base_url = auth_handler.get_base_graph_url()

        select_fields_str = "id,subject,from,receivedDateTime,isRead,importance,body,hasAttachments"
        
        request_url = f"{base_url}/users/{user_id}/messages/{email_id}?$select={select_fields_str}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                request_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
        
        email_message = response.json()

        if email_message:
            return {
                "id": email_message.get("id"),
                "subject": email_message.get("subject"),
                "from": email_message.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                "received_date_time": email_message.get("receivedDateTime"),
                "is_read": email_message.get("isRead"),
                "importance": email_message.get("importance"),
                "has_attachments": email_message.get("hasAttachments"),
                "body_content_type": email_message.get("body", {}).get("contentType"),
                "body": email_message.get("body", {}).get("content", "")
            }
        return {"status": "error", "message": f"Email with ID {email_id} not found."}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"Failed to get email content for {email_id}: HTTP Error {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred during email content retrieval: {type(e).__name__} - {e}"}

# Example Usage (for testing purposes outside the main agent loop)
async def main():
    try:
        auth_handler = MicrosoftGraphAuth()
        
        agent_mailbox_id = "ai_agent_dev2@intellistrata.com.au" 

        print(f"\n--- Listing unread emails for {agent_mailbox_id} (using filters) ---")
        unread_emails = await list_outlook_emails(auth_handler, agent_mailbox_id, filter_unread=True)
        if isinstance(unread_emails, dict) and unread_emails.get("status") == "error":
            print(f"Error listing unread emails: {unread_emails['message']}")
        else:
            print(f"Found {len(unread_emails)} unread emails.")
            for i, email in enumerate(unread_emails[:3]):
                print(f"  {i+1}. Subject: {email['subject']}, From: {email['from']}, Read: {email['is_read']}")
                if i == 0 and email.get('id'):
                    print(f"    - Getting content for email ID: {email['id']}")
                    content = await get_outlook_email_content(auth_handler, agent_mailbox_id, email['id'])
                    if isinstance(content, dict) and content.get("status") == "error":
                         print(f"      Error getting email content: {content['message']}")
                    else:
                        print(f"      Content snippet: {content['body'][:150]}...")
        
        print(f"\n--- Listing important emails for {agent_mailbox_id} ---")
        important_emails = await list_outlook_emails(auth_handler, agent_mailbox_id, filter_importance='high')
        if isinstance(important_emails, dict) and important_emails.get("status") == "error":
            print(f"Error listing important emails: {important_emails['message']}")
        else:
            print(f"Found {len(important_emails)} important emails.")
            for i, email in enumerate(important_emails[:3]):
                print(f"  {i+1}. Subject: {email['subject']}, From: {email['from']}, Importance: {email['importance']}")


        print(f"\n--- Listing emails from Junk Email folder for {agent_mailbox_id} ---")
        junk_emails = await list_outlook_emails(auth_handler, agent_mailbox_id, folder_name="JunkEmail")
        if isinstance(junk_emails, dict) and junk_emails.get("status") == "error":
            print(f"Error listing junk emails: {junk_emails['message']}")
        else:
            print(f"Found {len(junk_emails)} junk emails.")
            for i, email in enumerate(junk_emails[:3]):
                print(f"  {i+1}. Subject: {email['subject']}, From: {email['from']}")

        # Test Sending an Email - now with httpx
        print(f"\n--- Attempting to send a test email from {agent_mailbox_id} (using httpx direct) ---")
        test_recipient = "ai_agent_dev2@intellistrata.com.au"
        test_subject = "Test Email from Intelligent Agent (HTTPX Direct)"
        test_body = "This is a test email sent by the Microsoft 365 Intelligent Agent. This uses direct HTTPX calls for robustness."
        
        send_result = await send_outlook_email(auth_handler, test_recipient, test_subject, test_body)
        print(f"Send email result: {send_result}")

    except Exception as e:
        print(f"An error occurred in main test: {e}")

if __name__ == "__main__":
    asyncio.run(main())