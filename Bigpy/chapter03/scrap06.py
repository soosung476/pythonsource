import sys, io, urllib.request, urllib.parse
from urllib.parse import urlparse


API = "https://api.ipify.org"
values = {
    'format':'json'
}

print('before',values)
params= urllib.parse.urlencode(values)
print('after', params)

# 요청
url = API+"?"+params
print('요청 url = ',url)

# 읽기
data = urllib.request.urlopen(url).read()
text = data.decode('utf-8')
print(text)