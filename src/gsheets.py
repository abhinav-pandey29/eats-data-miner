"""
Classes related to Google Sheets
"""
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheets:
    """
    Wrapper class for Google Sheets functionality.
    Ensure you have the 'sheets_serviceaccount.json' in the 'creds/' directory.
    Refer to the README.md for setup instructions.
    """

    SERVICEACCOUNT_PATH = "creds/sheets_serviceaccount.json"
    SCOPES = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self) -> None:
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.SERVICEACCOUNT_PATH, self.SCOPES
        )
        self.client = gspread.authorize(self.credentials)

    def get_sheet(self, name: str) -> gspread.spreadsheet.Spreadsheet:
        sheet = self.client.open(name)
        return sheet

    def write_df_to_sheet(
        self,
        df: pd.DataFrame,
        sheet_name: str,
        worksheet_title: str,
        worksheet_index: int = 0,
    ) -> None:
        sheet = self.client.open(sheet_name)
        assert isinstance(sheet, gspread.spreadsheet.Spreadsheet)
        try:
            worksheet = sheet.get_worksheet(index=worksheet_index)
            worksheet.update_title(worksheet_title)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.add_worksheet(
                sheet_name,
                title=worksheet_title,
                rows=df.shape[0],
                cols=df.shape[1],
                index=worksheet_index,
            )
        assert isinstance(worksheet, gspread.worksheet.Worksheet)
        worksheet.clear()
        worksheet.update(
            values=[df.columns.values.tolist()] + df.values.tolist(),
            range_name="A1",
        )

    def add_worksheet(
        self, sheet_name: str, title: str, rows: int, cols: int, index: int
    ) -> gspread.worksheet.Worksheet:
        sheet = self.client.open(sheet_name)
        assert isinstance(sheet, gspread.spreadsheet.Spreadsheet)
        worksheet = sheet.add_worksheet(title=title, rows=rows, cols=cols, index=index)
        assert isinstance(worksheet, gspread.worksheet.Worksheet)
        return worksheet
