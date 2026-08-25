import sys
import os
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup


url = "http://www.encar.com/"


headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
}


req = urllib.request.Request(url, headers=headers)
mem = urllib.request.urlopen(req)

encoding = mem.info().get_content_charset() or 'utf-8'
html = mem.read().decode(encoding, errors='ignore')

soup = BeautifulSoup(html, "html.parser")

# title 태그에서 텍스트 가져오기
title = soup.select_one("title")
# print("title :",title)
print("title :",title.text) # 자식 텍스트가 여러개일 경우 사용
# print("title :",title.string) # 자식이 텍스트 하나일 경우 사용
# string을 사용할 경우 내차팔기·내차사기 | None 값 나올 수도 있음 |를 기호로 취급할 경우.


# 속성값을 활용하여 텍스트 가져오기
description = soup.select_one("meta[name='description']")
print("description : ",description.get("content") if description else "없음")


keywords = soup.select_one("meta[name='keywords']")
print("keywords : ", keywords.get("content") if keywords else "없음")
