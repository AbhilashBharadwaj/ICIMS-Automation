import gspread
from google.oauth2.service_account import Credentials


class GoogleAuthenticationUtil:

    def __init__(self, json_file_path):
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = Credentials.from_service_account_file(
            json_file_path, scopes=self.scopes)
        self.client = gspread.authorize(self.creds)

    def open_worksheet(self, sheet_url, worksheet_name):
        try:
            spreadsheet = self.client.open_by_url(sheet_url)
            worksheet = spreadsheet.worksheet(worksheet_name)
            return spreadsheet, worksheet
        except Exception as e:
            print(f"Error opening worksheet: {e}")
            return None
