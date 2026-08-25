import sys, io, urllib.request, urllib.parse
from urllib.parse import urlparse


API = "https://mois.go.kr/gpms/view/jsp/rss/rss.jsp"

key_value = {
    'ctxCd':'1012',
    
}
# key_value['ctxCd'] = '1013'
params= urllib.parse.urlencode(key_value)
print(params)

URL = API + "?" + params
data = urllib.request.urlopen(URL).read()
text = data.decode('utf-8')
print(text)