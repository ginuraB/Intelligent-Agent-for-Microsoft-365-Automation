import asyncio
import json
import os
from openai import OpenAI
from typing import Optional, List, Dict, Any
from datetime import datetime

from openai.types.chat import (
    ChatCompletionMessageToolCall,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
)

# Microsoft Graph auth and tool functions
from microsoft_graph.auth import MicrosoftGraphAuth
from microsoft_graph.outlook_email import send_outlook_email, list_outlook_emails, get_outlook_email_content
from microsoft_graph.outlook_calendar import create_calendar_event, update_calendar_event, delete_calendar_event
from microsoft_graph.onedrive_files import upload_file_to_onedrive, list_files_in_folder, download_file_from_onedrive, delete_file_from_onedrive

# Tool definitions
from tools.outlook_tools import OUTLOOK_EMAIL_TOOLS
from tools.calendar_tools import CALENDAR_TOOLS
from tools.onedrive_tools import ONEDRIVE_FILE_TOOLS


class AgentCore:
    def __init__(self, supervisor_email: str):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.auth_handler = MicrosoftGraphAuth()
        self.supervisor_email = supervisor_email

        # Combine tools
        self.all_tools = OUTLOOK_EMAIL_TOOLS + CALENDAR_TOOLS + ONEDRIVE_FILE_TOOLS

        self.tool_functions = {
            "send_outlook_email": send_outlook_email,
            "list_outlook_emails": list_outlook_emails,
            "get_outlook_email_content": get_outlook_email_content,
            "create_calendar_event": create_calendar_event,
            "update_calendar_event": update_calendar_event,
            "delete_calendar_event": delete_calendar_event,
            "upload_file_to_onedrive": upload_file_to_onedrive,
            "list_files_in_folder": list_files_in_folder,
            "download_file_from_onedrive": download_file_from_onedrive,
            "delete_file_from_onedrive": delete_file_from_onedrive,
        }

        self.system_instructions = (
            "You are an intelligent Microsoft 365 agent designed to help users manage their email, calendar, and OneDrive files. "
            "You have access to specific tools to perform these actions. "
            "Always prioritize using the available tools to fulfill user requests related to these domains. "
            "If a request is outside your capabilities (e.g., requires access to systems not covered by your tools, or is a highly complex multi-step process that you cannot break down), "
            f"or if a tool call fails repeatedly, you must escalate the request to the supervisor by stating 'This task requires supervisor attention.' "
            "When performing file operations, assume the user's OneDrive is the target unless specified otherwise. "
            "For email and calendar operations, assume the user's mailbox/calendar is 'ai_agent_dev2@intellistrata.com.au' unless another specific user ID is provided by the user. "
            "When creating or updating calendar events, always ask for specific date and time details if not provided, and clarify the timezone. "
            "When a tool produces results (e.g., a list of emails), summarize them concisely and offer further assistance based on the results. "
            "Be polite, helpful, and clear in your responses. "
            "When sending emails, ask for confirmation before sending the final email content if it's a critical action. "
            "After performing an action, confirm success or report any failures clearly."
        )

        # Typed history of messages
        self.messages_history: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(role="system", content=self.system_instructions)
        ]

    async def _dispatch_tool_call(self, tool_call: ChatCompletionMessageToolCall) -> Dict[str, Any]:
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments

        if tool_name not in self.tool_functions:
            return {"error": f"Tool '{tool_name}' not found or implemented."}

        try:
            parsed_args = json.loads(tool_args)
            func = self.tool_functions[tool_name]
            result = await func(auth_handler=self.auth_handler, **parsed_args)
            return result
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON arguments for '{tool_name}': {tool_args}"}
        except Exception as e:
            return {"error": f"Error executing tool '{tool_name}': {type(e).__name__} - {e}"}

    async def process_message(self, user_message: str) -> Dict[str, Any]:
        self.messages_history.append(ChatCompletionUserMessageParam(role="user", content=user_message))

        try:
            chat_completion_response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages_history,
                tools=self.all_tools,
                tool_choice="auto",
            )

            response_message = chat_completion_response.choices[0].message

            # Append assistant message with either content or tool calls
            self.messages_history.append(ChatCompletionAssistantMessageParam(
                role="assistant",
                content=response_message.content,
                tool_calls=response_message.tool_calls
            ))

            # Handle tool calls if present
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    print(f"\nCalling tool: {tool_call.function.name} with args: {tool_call.function.arguments}")
                    tool_result = await self._dispatch_tool_call(tool_call)
                    print(f"Tool result: {tool_result}")

                    self.messages_history.append(ChatCompletionToolMessageParam(
                        role="tool",
                        tool_call_id=tool_call.id,
                        content=json.dumps(tool_result)
                    ))

                # Second call with tool responses
                second_response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=self.messages_history,
                    tools=self.all_tools,
                    tool_choice="auto"
                )

                final_message = second_response.choices[0].message
                final_text = final_message.content or ""

                self.messages_history.append(ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=final_text
                ))

                return {"text_output": final_text}

            elif response_message.content:
                return {"text_output": response_message.content}
            else:
                return {"text_output": "I couldn't process that request fully. Could you please rephrase?"}

        except Exception as e:
            print(f"[Error in process_message] {type(e).__name__}: {e}")
            return {"text_output": "An internal error occurred. Please try again later or contact support."}


# Testing script (optional)
async def main():
    supervisor_email = os.getenv("SUPERVISOR_EMAIL", "default_supervisor@example.com")
    agent = AgentCore(supervisor_email)

    print("Agent ready. Type 'exit' to quit.")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break

        response = await agent.process_message(user_input)
        print(f"Agent: {response['text_output']}")

        if "supervisor attention" in response['text_output'].lower():
            print(f"(Automatic escalation to {agent.supervisor_email})")


if __name__ == "__main__":
    asyncio.run(main())
