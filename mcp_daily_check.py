# -*- coding: utf-8 -*-

import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

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

def main():
    # GitHub Secrets から読み込み
    service_account_info = json.loads(os.environ['GCP_SERVICE_ACCOUNT_KEY'])
    sheet_id = os.environ['SHEET_ID']  # 別途登録する
    
    count = get_indexed_count()
    if count is not None:
        now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
        print(f" {now} のIndexed数：{count}個 を記録します")
        append_to_sheet(service_account_info, sheet_id, now, count)
    else:
        print("Indexed数を取得できませんでした。")

if __name__ == "__main__":
    main()
