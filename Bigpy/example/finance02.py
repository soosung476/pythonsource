from bs4 import BeautifulSoup
import urllib.request as req
import sys
import io
import json
from fake_useragent import UserAgent
import requests


ua = UserAgent()
headers={
    "User-Agent": ua.random, # 가짜 브라우저, 
    "referer" : 'http://finance.daum.net/'
}

url = "http://finance.daum.net/api/search/ranks?limit=10"

# res = req.urlopen(req.Request(url, headers=headers)).read().decode('utf-8')
res = requests.get(url,headers=headers)
res.encoding= 'utf-8'
print(res)

# rank_json = json.loads(res)["data"]
rank_json = res.json()['data']
print(rank_json)

for elm in rank_json:
    i = 0
    print(f"순위: {elm['rank']}, 금액: {elm['tradePrice']}, 회사명: {elm['name']}")