import requests
from bs4 import BeautifulSoup

def debug_initials():
    url = "https://dict.idioms.moe.edu.tw/bookView.jsp?ID=-1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    phonetic_initials = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄜㄞㄡㄢㄦㄧㄨㄩ"
    
    # Let's find all tags that contain a phonetic initial and print their attributes
    for tag in soup.find_all(True): # True means all tags
        text = tag.get_text(strip=True)
        if text in phonetic_initials and len(text) == 1:
            print(f"Tag: {tag.name} | Text: {text} | Attrs: {tag.attrs}")

if __name__ == "__main__":
    debug_initials()
