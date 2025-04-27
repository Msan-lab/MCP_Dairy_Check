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
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build('sheets', 'v4', credentials=creds)

    spreadsheet_id = sheet_id
    requests = [
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "MCP Indexed Count Over Time",
                        "basicChart": {
                            "chartType": "LINE",
                            "legendPosition": "BOTTOM_LEGEND",
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Datetime"},
                                {"position": "LEFT_AXIS", "title": "Indexed Count"}
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": 0,
                                                    "startRowIndex": 1,
                                                    "startColumnIndex": 0,
                                                    "endColumnIndex": 1
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": 0,
                                                    "startRowIndex": 1,
                                                    "startColumnIndex": 1,
                                                    "endColumnIndex": 2
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS"
                                }
                            ],
                            "headerCount": 0
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": 0,
                                "rowIndex": 0,
                                "columnIndex": 3
                            },
                            "offsetXPixels": 0,
                            "offsetYPixels": 0,
                            "widthPixels": 600,
                            "heightPixels": 400
                        }
                    }
                }
            }
        }
    ]

    body = {'requests': requests}

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

def main():
    service_account_info = json.loads(os.environ['GCP_SERVICE_ACCOUNT_KEY'])
    sheet_id = os.environ['SHEET_ID']

    count = get_indexed_count()
    if count is not None:
        now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
        print(f"✅ {now} のIndexed数：{count}個 を記録します")
        append_to_sheet(service_account_info, sheet_id, now, count)

        # ここでグラフ作成を呼び出す！
        create_line_chart(service_account_info, sheet_id)
    else:
        print("⚠️ Indexed数を取得できませんでした。")

if __name__ == "__main__":
    main()
