"""
Classes related to Gmail API
"""

import os

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class Gmail:
    """
    Wrapper class for Gmail API functionality.
    Ensure you have the 'credentials.json' in the 'creds/' directory.
    Refer to the README.md for setup instructions.
    """

    CREDENTIALS_PATH = "creds/credentials.json"
    TOKEN_PATH = "creds/token.json"
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self):
        try:
            self.credentials = self.run_auth_flow()
        except RefreshError as e:
            print(f"Authentication failed: {e}")
            if os.path.exists(self.TOKEN_PATH):
                os.remove(self.TOKEN_PATH)
            self.credentials = self.run_auth_flow()

        self.client = build("gmail", "v1", credentials=self.credentials)

    def run_auth_flow(self):
        creds = None
        # Check if the token file exists
        if os.path.exists(self.TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(self.TOKEN_PATH, self.SCOPES)

        # If the credentials are not valid or do not exist, log in.
        # This includes checking if the credentials are expired or if there is no refresh token.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_PATH, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        assert isinstance(
            creds, Credentials
        ), "Problem with authentication credentials."
        return creds

    def search(self, query: str):
        results = []
        while True:
            if len(results) == 0:
                req = self.client.users().messages().list(userId="me", q=query)
                resp = req.execute()
            else:
                req = self.client.users().messages().list_next(req, resp)
                resp = req.execute()

            print(
                f'Messages: {len(resp["messages"])}, '
                f'nextPageToken: {resp.get("nextPageToken")}, '
                f'resultSizeEstimate: {resp["resultSizeEstimate"]}'
            )

            results.extend(resp["messages"])

            if "nextPageToken" not in resp:
                break

        return results

    def get_message_by_id(self, id: str, msg_format: str = "raw"):
        return (
            self.client.users()
            .messages()
            .get(userId="me", id=id, format=msg_format)
            .execute()
        )
