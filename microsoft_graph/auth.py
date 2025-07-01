# import os
# from dotenv import load_dotenv
# from azure.identity import ClientSecretCredential
# from msgraph.graph_service_client import GraphServiceClient # This is the correct, working import!

# # Load environment variables from .env file
# load_dotenv()

# class MicrosoftGraphAuth:
#     """
#     Handles authentication with Azure AD for Microsoft Graph API using Client Credentials Flow.
#     """
#     def __init__(self):
#         self.client_id = os.getenv("AZURE_CLIENT_ID")
#         self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
#         self.tenant_id = os.getenv("AZURE_TENANT_ID")
#         # For client credentials flow, the scope typically points to the resource itself
#         # ".default" scope indicates all permissions configured for the app registration.
#         self.scope = ["https://graph.microsoft.com/.default"]

#         if not all([self.client_id, self.client_secret, self.tenant_id]):
#             raise ValueError("AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID must be set in the .env file.")

#         # Type assertion to satisfy type checker (useful for IDEs, doesn't affect runtime)
#         assert self.client_id is not None
#         assert self.client_secret is not None
#         assert self.tenant_id is not None

#         self.credential = ClientSecretCredential(
#             tenant_id=self.tenant_id,
#             client_id=self.client_id,
#             client_secret=self.client_secret
#         )
#         self.graph_client = self._initialize_graph_client()

#     def _initialize_graph_client(self):
#         """
#         Initializes and returns a Microsoft GraphServiceClient.
#         This client automatically handles token acquisition and refresh using the provided credential.
#         """
#         # The GraphServiceClient constructor expects credentials and scopes.
#         client = GraphServiceClient(credentials=self.credential, scopes=self.scope)
#         return client

#     def get_graph_client(self):
#         """
#         Returns the initialized Microsoft GraphServiceClient.
#         """
#         return self.graph_client

#     def get_access_token(self):
#         """
#         Retrieves a raw access token. Useful for debugging or direct HTTP calls if needed.
#         """
#         # ClientSecretCredential.get_token expects a list of scopes
#         token_response = self.credential.get_token(*self.scope)
#         return token_response.token

# # Example Usage (for testing purposes, you can remove this later)
# if __name__ == "__main__":
#     try:
#         print("Attempting to initialize Microsoft Graph authentication...")
#         auth_handler = MicrosoftGraphAuth()
#         graph_client = auth_handler.get_graph_client()
#         access_token = auth_handler.get_access_token()

#         print("Microsoft Graph client initialized successfully!")
#         print(f"Access Token (first 20 chars): {access_token[:20]}...")
#         print("\nAuthentication setup complete. You can now use graph_client for Microsoft Graph API calls.")

#     except ValueError as e:
#         print(f"Configuration Error: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred during authentication: {e}")

























import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
import asyncio # Needed for running async test

# Load environment variables from .env file
load_dotenv()

class MicrosoftGraphAuth:
    """
    Handles authentication with Azure AD for Microsoft Graph API using Client Credentials Flow.
    It provides methods to retrieve access tokens and the base URL for direct Graph API calls.
    """
    def __init__(self):
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.scope = ["https://graph.microsoft.com/.default"] # Required scope for client credentials flow
        self.base_graph_url = "https://graph.microsoft.com/v1.0"

        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError("AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID must be set in the .env file.")

        assert self.client_id is not None
        assert self.client_secret is not None
        assert self.tenant_id is not None

        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )

    def get_access_token(self) -> str:
        """
        Retrieves an access token string from Azure AD.
        """
        try:
            token_object = self.credential.get_token(*self.scope)
            return token_object.token
        except Exception as e:
            # Capture the original exception type and message for better debugging
            raise Exception(f"Failed to get access token from Azure AD: {type(e).__name__} - {e}")

    def get_base_graph_url(self) -> str:
        """
        Returns the base URL for the Microsoft Graph API.
        """
        return self.base_graph_url

# Example Usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    async def run_auth_test():
        try:
            print("Attempting to initialize Microsoft Graph authentication handler...")
            auth_handler = MicrosoftGraphAuth()
            # This call MUST be awaited because get_access_token is a regular method.
            access_token = auth_handler.get_access_token() 
            base_url = auth_handler.get_base_graph_url()

            print("Microsoft Graph authentication handler initialized successfully!")
            print(f"Access Token (first 20 chars): {access_token[:20]}...")
            print(f"Base Graph URL: {base_url}")
            print("\nAuthentication setup complete. You can now use this token and URL for direct HTTP calls.")

        except ValueError as e:
            print(f"Configuration Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during authentication: {type(e).__name__} - {e}")
    
    asyncio.run(run_auth_test())