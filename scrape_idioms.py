import requests
from bs4 import BeautifulSoup
import sqlite3
import re

def scrape_idioms():
    url = "https://dict.idioms.moe.edu.tw/bookView.jsp?ID=-1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    conn = sqlite3.connect('idioms-db/idioms.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS idioms')
    cursor.execute('''
        CREATE TABLE idioms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phonetic_initial TEXT NOT NULL,
            external_id TEXT NOT NULL,
            is_main_entry BOOLEAN
        )
    ''')
    
    phonetic_initials = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄜㄞㄡㄢㄦㄧㄨㄩ"
    current_initial = ""
    idioms_found = 0
    
    # We iterate through the whole page.
    # When we see a <legend id="phㄅ">, we update current_initial.
    # When we see an <a href="/bookView.jsp?ID=...">, we add the idiom if it's positive ID.
    
    # To be safe, we'll iterate through all tags in order.
    for tag in soup.find_all(True):
        text = tag.get_text(strip=True)
        
        # Check for section header
        if tag.name == 'legend' and text in phonetic_initials and len(text) == 1:
            current_initial = text
            # print(f"Entering section: {current_initial}")
            continue
            
        # Check for idiom link
        if tag.name == 'a' and current_initial:
            href = tag.get('href', '')
            if '/bookView.jsp?ID=' in href:
                match = re.search(r'ID=(\d+)', href)
                if match:
                    external_id = match.group(1)
                    if int(external_id) > 0:
                        idiom_name = text
                        # Skip if it's a navigational link like "上一頁"
                        if not idiom_name or len(idiom_name) > 30:
                            continue
                        if "上一頁" in idiom_name or "下一頁" in idiom_name:
                            continue
                            
                        is_main = "主" in idiom_name
                        clean_name = idiom_name.replace("主", "")
                        
                        cursor.execute('''
                            INSERT INTO idioms (name, phonetic_initial, external_id, is_main_entry)
                            VALUES (?, ?, ?, ?)
                        ''', (clean_name, current_initial, external_id, is_main))
                        idioms_found += 1
    
    conn.commit()
    conn.close()
    print(f"Finished. Total idioms found: {idioms_found}")

if __name__ == "__main__":
    scrape_idioms()
