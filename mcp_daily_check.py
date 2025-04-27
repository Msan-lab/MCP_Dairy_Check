# -*- coding: utf-8 -*-

import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

from googleapiclient.discovery import build
from google.oauth2 import service_account

def get_indexed_count():
    url = "https://mcp.so/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    indexed_section = soup.find(lambda tag: tag.name in ["div", "span"] and "Indexed" in tag.text)

    if indexed_section:
        text = indexed_section.get_text()
        numbers = ''.join(filter(str.isdigit, text))
        return int(numbers) if numbers else None
    else:
        return None

def append_to_sheet(service_account_info, sheet_id, datetime_str, count):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(sheet_id)
    worksheet = sh.sheet1
    worksheet.append_row([datetime_str, count])

def create_line_chart(service_account_info, sheet_id):
    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https
