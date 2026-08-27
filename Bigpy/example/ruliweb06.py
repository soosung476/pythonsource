from bs4 import BeautifulSoup
import requests
from pathlib import Path
import unicodedata

import re

BASE_DIR = Path(__file__).resolve().parent
Py_Scrap = BASE_DIR.parent/"Py_Scrap"

url = "https://bbs.ruliweb.com/market/board/1020/read/106677"

with requests.Session() as s:
    post = s.get(url)
    soup = BeautifulSoup(post.text, 'html.parser')

    # print(soup.prettify)
    
    text_list = soup.select("article > div > p")
    for i in text_list:
        text = i.get_text(separator=' ', strip=True)
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        # 그냥 string 처리하면 너무 공백이 많음. 이걸 지우고 싶음.
        if text: 
            print(text)