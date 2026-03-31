import requests
from bs4 import BeautifulSoup

def debug_structure():
    url = "https://dict.idioms.moe.edu.tw/bookView.jsp?ID=-1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Print some <a> tags and their surroundings
    count = 0
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if 'dictView.jsp?ID=' in href or 'detail.jsp?ID=' in href:
            print(f"Link: {a.get_text()} | Href: {href} | Parent: {a.parent.name}")
            count += 1
            if count > 20:
                break

    # Look for phonetic initial markers
    phonetic_initials = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄜㄞㄡㄢㄦㄧㄨㄩ"
    for tag in soup.find_all(['div', 'span', 'h1', 'h2', 'h3', 'h4', 'a']):
        text = tag.get_text(strip=True)
        if text in phonetic_initials and len(text) == 1:
            print(f"Found Initial: {text} | Tag: {tag.name} | ID: {tag.get('id')} | Class: {tag.get('class')}")

if __name__ == "__main__":
    debug_structure()
