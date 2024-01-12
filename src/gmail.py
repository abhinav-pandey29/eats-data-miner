"""
Classes related to Gmail API
"""
import os

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
        self.credentials = self.run_auth_flow()
        self.client = build("gmail", "v1", credentials=self.credentials)

    def run_auth_flow(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(self.TOKEN_PATH, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.CREDENTIALS_PATH, self.SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        assert isinstance(creds, Credentials)
        self.credentials = creds

        return self.credentials

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
