import requests
from bs4 import BeautifulSoup

def list_all_links():
    url = "https://dict.idioms.moe.edu.tw/bookView.jsp?ID=-1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    count = 0
    for a in soup.find_all('a'):
        href = a.get('href', '')
        text = a.get_text(strip=True)
        print(f"Text: {text} | Href: {href}")
        count += 1
        if count > 100:
            break

if __name__ == "__main__":
    list_all_links()
