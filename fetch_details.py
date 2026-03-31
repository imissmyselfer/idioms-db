import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re

def clean_text(text):
    if not text:
        return ""
    # 移除多餘的空白、換行與 </a> 標籤殘留
    text = re.sub(r'</a>', '', text)
    return text.strip()

def get_content_until_next_h4(h4_tag):
    content = []
    curr = h4_tag.next_sibling
    while curr and curr.name != 'h4':
        if hasattr(curr, 'get_text'):
            content.append(curr.get_text())
        else:
            content.append(str(curr))
        curr = curr.next_sibling
    
    # 合併後移除 HTML 標籤（如 <br>, <nbr> 等），但保留文字
    raw_html = "".join(content)
    clean = BeautifulSoup(raw_html, "html.parser").get_text()
    return clean_text(clean)

def fetch_idiom_details():
    conn = sqlite3.connect('idioms-db/idioms.db')
    cursor = conn.cursor()
    
    # 1. 建立詳細資訊表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS idiom_details (
            external_id TEXT PRIMARY KEY,
            name TEXT,
            bopomofo TEXT,
            pinyin TEXT,
            meaning TEXT,
            synonyms TEXT,
            antonyms TEXT,
            memo TEXT
        )
    ''')
    
    # 2. 找出標註為 '1' 的 100 個成語
    cursor.execute("SELECT external_id, name FROM idioms WHERE tag = '1'")
    target_idioms = cursor.fetchall()
    print(f"準備抓取 {len(target_idioms)} 個成語的詳細資料...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    count = 0
    for ext_id, name in target_idioms:
        url = f"https://dict.idioms.moe.edu.tw/bookView.jsp?ID={ext_id}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"無法抓取 {name} ({ext_id})")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'external_id': ext_id,
                'name': name,
                'bopomofo': "",
                'pinyin': "",
                'meaning': "",
                'synonyms': "",
                'antonyms': ""
            }
            
            # 根據 <h4> 標籤定位
            for h4 in soup.find_all('h4'):
                header_text = h4.get_text(strip=True)
                if "注" in header_text and "音" in header_text:
                    details['bopomofo'] = get_content_until_next_h4(h4)
                elif "漢語拼音" in header_text:
                    details['pinyin'] = get_content_until_next_h4(h4)
                elif "語義說明" in header_text:
                    details['meaning'] = get_content_until_next_h4(h4)
                elif "近義" in header_text:
                    details['synonyms'] = get_content_until_next_h4(h4)
                elif "反義" in header_text:
                    details['antonyms'] = get_content_until_next_h4(h4)
            
            # 寫入資料庫 (使用 COALESCE 保留已有的 memo)
            cursor.execute('''
                INSERT INTO idiom_details 
                (external_id, name, bopomofo, pinyin, meaning, synonyms, antonyms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(external_id) DO UPDATE SET
                    name=excluded.name,
                    bopomofo=excluded.bopomofo,
                    pinyin=excluded.pinyin,
                    meaning=excluded.meaning,
                    synonyms=excluded.synonyms,
                    antonyms=excluded.antonyms
            ''', (
                details['external_id'], details['name'], details['bopomofo'], 
                details['pinyin'], details['meaning'], details['synonyms'], details['antonyms']
            ))
            
            count += 1
            if count % 10 == 0:
                print(f"已完成 {count}/100...")
                conn.commit() # 定期儲存
            
            time.sleep(0.5) # 禮貌性延遲
            
        except Exception as e:
            print(f"處理 {name} 時出錯: {e}")
    
    conn.commit()
    conn.close()
    print(f"全部完成！共更新 {count} 筆詳細資料。")

if __name__ == "__main__":
    fetch_idiom_details()
