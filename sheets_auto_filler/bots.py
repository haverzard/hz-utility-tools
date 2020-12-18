from __future__ import print_function
import pickle
import os.path
import extractor
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "**REDACTED**"
RANGE_NAME = "!A5:L305"

CREDS = ["creds.pickle", "credentials.json"]


def main():
    creds = None

    # Check for creds
    if os.path.exists(CREDS[0]):
        with open(CREDS[0], "rb") as token:
            creds = pickle.load(token)

    # Request new creds if not found or not valid
    if not creds or not creds.valid:
        # Refresh creds if creds is not valid
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS[1], SCOPES)
            creds = flow.run_local_server(port=5000)

        # Save new creds
        with open(CREDS[0], "wb") as token:
            pickle.dump(creds, token)

    # Build sheets app
    service = build("sheets", "v4", credentials=creds)

    for x in ["CP", "CTF", "Datavidia", "Arkalogica", "Arkav Game Jam"]:
        # Extract your data
        data = extractor.extract_data(x)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .update(
                spreadsheetId=SPREADSHEET_ID,
                range=x+RANGE_NAME,
                valueInputOption="USER_ENTERED",
                body={"majorDimension": "ROWS", "values": data},
            )
            .execute()
        )
        del result


if __name__ == "__main__":
    main()
