from __future__ import annotations
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import GOOGLE_SHEETS_CREDENTIALS_FILE, GOOGLE_SHEET_NAME

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    "Italiano", "Deutsch", "Categoria", "Genere IT", "Genere DE",
    "Plurale IT", "Plurale DE", "Esempio IT", "Esempio DE", "Data",
]


def _get_sheet():
    creds = Credentials.from_service_account_file(
        GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    spreadsheet = gc.open(GOOGLE_SHEET_NAME)
    sheet = spreadsheet.sheet1

    # Ensure headers exist
    first_row = sheet.row_values(1)
    if not first_row:
        sheet.append_row(HEADERS)

    return sheet


def save_word(data: dict) -> bool:
    try:
        sheet = _get_sheet()
        row = [
            data.get("italiano", ""),
            data.get("deutsch", ""),
            data.get("categoria", ""),
            data.get("genere_it", ""),
            data.get("genere_de", ""),
            data.get("plurale_it", ""),
            data.get("plurale_de", ""),
            data.get("esempio_it", ""),
            data.get("esempio_de", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        print(f"Sheets error: {e}")
        return False


def get_all_words() -> list[dict]:
    try:
        sheet = _get_sheet()
        records = sheet.get_all_records()
        return records
    except Exception as e:
        print(f"Sheets read error: {e}")
        return []


def get_random_words(n: int = 5) -> list[dict]:
    import random
    words = get_all_words()
    if not words:
        return []
    return random.sample(words, min(n, len(words)))


def get_word_count() -> int:
    try:
        sheet = _get_sheet()
        return max(0, len(sheet.get_all_values()) - 1)  # minus header
    except Exception:
        return 0
