import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re

def clean_text(text):
    if not text:
        return ""
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
    
    raw_html = "".join(content)
    clean = BeautifulSoup(raw_html, "html.parser").get_text()
    return clean_text(clean)

def fetch_idiom_details():
    conn = sqlite3.connect('idioms-db/idioms.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT external_id, name FROM idioms WHERE tag = '1'")
    target_idioms = cursor.fetchall()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    count = 0
    for ext_id, name in target_idioms:
        url = f"https://dict.idioms.moe.edu.tw/bookView.jsp?ID={ext_id}"
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 找到網頁主名稱
            main_title = ""
            title_tag = soup.find(['h1', 'h2', 'h3'])
            if title_tag:
                main_title = clean_text(title_tag.get_text())
            
            details = {'bopomofo': "", 'pinyin': "", 'meaning': "", 'synonyms': "", 'antonyms': ""}
            
            # 如果是主條目，直接抓取頁面最上方的注音
            is_primary = (name == main_title) or (name + "主" == main_title) or (main_title.startswith(name))
            
            if is_primary:
                for h4 in soup.find_all('h4'):
                    header_text = h4.get_text(strip=True)
                    if "注" in header_text and "音" in header_text and not details['bopomofo']:
                        details['bopomofo'] = get_content_until_next_h4(h4)
                    elif "漢語拼音" in header_text and not details['pinyin']:
                        details['pinyin'] = get_content_until_next_h4(h4)
            else:
                # 如果是變體，尋找精確匹配的 <li>
                found_variant = False
                for li in soup.find_all('li'):
                    # 變體名稱通常在 <li> 的開頭，可能包含 * 號
                    li_full_text = li.get_text(strip=True)
                    # 移除開頭的星號或空白
                    li_name = re.sub(r'^\*\s*', '', li_full_text)
                    
                    # 檢查 <li> 內容是否以成語名稱開頭，且後面緊跟著「注音」
                    if li_name.startswith(name):
                        variant_h4s = li.find_all('h4')
                        for vh4 in variant_h4s:
                            v_header = vh4.get_text(strip=True)
                            if "注" in v_header and "音" in v_header:
                                details['bopomofo'] = get_content_until_next_h4(vh4)
                                found_variant = True
                            elif "漢語拼音" in v_header:
                                details['pinyin'] = get_content_until_next_h4(vh4)
                        if found_variant: break
                
                # 若沒找到變體專屬注音，回歸主條目
                if not details['bopomofo']:
                    for h4 in soup.find_all('h4'):
                        header_text = h4.get_text(strip=True)
                        if "注" in header_text and "音" in header_text and not details['bopomofo']:
                            details['bopomofo'] = get_content_until_next_h4(h4)
                        elif "漢語拼音" in header_text and not details['pinyin']:
                            details['pinyin'] = get_content_until_next_h4(h4)

            # 抓取釋義、近反義 (這些通常是通用的)
            for h4 in soup.find_all('h4'):
                header_text = h4.get_text(strip=True)
                if ("釋義" in header_text or "語義說明" in header_text) and not details['meaning']:
                    details['meaning'] = get_content_until_next_h4(h4)
                elif "近義" in header_text and not details['synonyms']:
                    details['synonyms'] = get_content_until_next_h4(h4)
                elif "反義" in header_text and not details['antonyms']:
                    details['antonyms'] = get_content_until_next_h4(h4)

            cursor.execute('''
                INSERT INTO idiom_details 
                (external_id, name, bopomofo, pinyin, meaning, synonyms, antonyms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(external_id) DO UPDATE SET
                    bopomofo=excluded.bopomofo,
                    pinyin=excluded.pinyin,
                    meaning=excluded.meaning,
                    synonyms=excluded.synonyms,
                    antonyms=excluded.antonyms
            ''', (ext_id, name, details['bopomofo'], details['pinyin'], details['meaning'], details['synonyms'], details['antonyms']))
            
            count += 1
            if count % 10 == 0:
                print(f"已處理 {count}/100...")
                conn.commit()
            time.sleep(0.5)
            
        except Exception as e:
            print(f"處理 {name} 出錯: {e}")
            
    conn.commit()
    conn.close()
    print("全部修正完成。")

if __name__ == "__main__":
    fetch_idiom_details()
