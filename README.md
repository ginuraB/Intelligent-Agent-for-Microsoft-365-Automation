# 🚀 Intelligent Agent for Microsoft 365 Automation

## Project Description

This project aims to develop an intelligent agent designed to automate and streamline various tasks within the Microsoft 365 ecosystem. Leveraging the latest OpenAI Responses API for advanced natural language understanding and tool-calling capabilities, this agent will seamlessly integrate with Microsoft Outlook, Calendar, and OneDrive via the Microsoft Graph API.

The primary objective is to enhance productivity by enabling the agent to:
* [cite_start]**Email Management:** Read, filter (unread, important, junk/spam), and send emails. 
* [cite_start]**Calendar Management:** Create, update, and delete calendar events. 
* [cite_start]**File Management:** Read and write files locally or via cloud storage (OneDrive MS). 

[cite_start]The agent will be capable of responding intelligently based on its knowledge base and if the mail seems to be beyond the agent’s scope then it should reach out to the supervisor.  [cite_start]This project is built exclusively using Microsoft technologies for integration and management. 

## Team Members

* [cite_start]Ginura Binath Pasanjith 
* [cite_start]Sameera Athukorala 
* [cite_start]M.A. Mohamed Asaf 

## Technologies Used

* [cite_start]**Core AI:** OpenAI Responses API (for natural language processing, decision making, and tool orchestration) 
* [cite_start]**Microsoft 365 Integration:** Microsoft Graph API (for interacting with Outlook, Calendar, and OneDrive) 
* **Programming Language:** Python
* **Authentication:** Azure Active Directory (OAuth 2.0 Client Credentials Flow)

## Getting Started

[cite_start]Follow these structured steps to ensure a smooth and successful project execution: 

### Prerequisites

* Python 3.9+ (Python 3.11 recommended)
* `pip` package manager
* Access to an Azure subscription with permissions to register applications and grant API permissions.
* An OpenAI API key with access to the Responses API.
* Necessary administrative consent for Azure AD application permissions.

### Setup and Configuration

1.  **Set up Azure AD Application:**
    * Register a new application in your Azure Active Directory.
    * Configure API permissions for Microsoft Graph (Application permissions):
        * `Mail.ReadWrite`
        * `Calendars.ReadWrite`
        * `Files.ReadWrite.All`
    * Grant admin consent for these permissions.
    * Create a new client secret for the application.
    * Note down your **Application (Client) ID**, **Client Secret Value**, and **Tenant ID**.

2.  **Configure Environment Variables:**
    Create a `.env` file in the root of the project (this file should NOT be committed to Git). See `.env.example` for format.

3.  **Install Dependencies:**
    ```bash
    # Create and activate virtual environment (highly recommended)
    python -m venv venv
    .\venv\Scripts\activate  # On Windows, use `venv\Scripts\activate` or `source venv/bin/activate` for Git Bash

    # Install dependencies
    pip install -r requirements.txt
    ```

## Folder Structure (Corrected and Final)

Intelligent-Agent-for-Microsoft-365-Automation/
├── .env.example              # Example for environment variables (DO NOT COMMIT .env)
├── .gitignore                # Specifies intentionally untracked files to ignore
├── README.md                 # Project overview and setup instructions
├── requirements.txt          # Python dependencies
├── main.py                   # Main entry point for the agent application
├── agent/                    # Contains core agent logic
│   ├── init.py
│   ├── core.py               # Handles OpenAI API calls, response parsing, and tool execution
│   └── conversation.py       # Manages conversation state and context
├── microsoft_graph/          # Contains functions for interacting with Microsoft Graph API
│   ├── init.py
│   ├── auth.py               # Handles Azure AD authentication and token management
│   ├── outlook_email.py      # Functions for Outlook email operations (read, send, filter)
│   ├── outlook_calendar.py   # Functions for Outlook calendar operations (create, update, delete)
│   └── onedrive_files.py     # Functions for OneDrive file operations (read, write)
├── tools/                    # Definitions of custom tools for OpenAI
│   ├── init.py
│   ├── outlook_tools.py      # OpenAI tool definitions for email operations
│   ├── calendar_tools.py     # OpenAI tool definitions for calendar operations
│   └── onedrive_tools.py     # OpenAI tool definitions for OneDrive operations
├── utils/                    # Utility functions (e.g., logging, error handling)
│   ├── init.py
│   └── logger.py
└── tests/                    # Unit and integration tests
├── test_auth.py
├── test_email.py
└── ...


## How to Run

(Instructions will be added here once the basic structure is implemented in Phase 1)

## Contributing

We welcome contributions! Please adhere to the project's coding standards and submit pull requests for review.

## License

[See LICENSE](#license) (Link will point to the LICENSE file once created)