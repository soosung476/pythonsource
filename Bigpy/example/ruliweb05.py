from bs4 import BeautifulSoup
import requests
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
Py_Scrap = BASE_DIR.parent/"Py_Scrap"

url = "https://bbs.ruliweb.com/market/board/1020/read/37546"


with requests.Session() as s:
    post_one = s.get(url)
    post_one.raise_for_status
    print(post_one)
    

    soup = BeautifulSoup(post_one.text, 'html.parser')
    # print(soup.prettify)
    article = soup.select("article>div>p")
    for text in article:
        if text.string is not None and text.img == None :
            print(text.string)