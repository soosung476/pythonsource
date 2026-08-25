import sys
import os
import urllib.request
from urllib.parse import urlparse


url = "http://www.encar.com/"

# encar 처럼 봇 차단이 있는 사이트는 기본 User-Agent로 요청하면
# 403, 406 에러가 발생하여 정상 페이지를 받지 못함.

req = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/151.0.0.0 Safari/537.36"
    }
)

mem = urllib.request.urlopen(req)
print(type(mem))
print("geturl :",mem.geturl()) # url
print("status :",mem.status) # 연결상태 200. html error code를 반환할 수도 있음.
print("headers :",mem.getheaders())
print("info :",mem.info()) # header 정보를 행단위로 보여줌
print("getcode: ",mem.getcode()) # mem.status

# 서버가 사용하는 문자 인코딩, 없으면 utf-8

encoding = mem.info().get_content_charset() or 'utf-8'

# 바이트를 500개만 자르면, 멀티바이트(한글, 한자, 특문) 중간에 끊김. => Error발생 가능
# unicodeDecodeError 가 반환될 수 있으므로, errors = 'ignore' 처리
raw = mem.read(500)
print("read: ", raw.decode(encoding,errors='ignore'))

print(urlparse('http://www.encar.co.kr?test=test').query)
