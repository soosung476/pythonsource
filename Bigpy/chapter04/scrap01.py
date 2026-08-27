import requests

# s = requests.Session()
url = "http://httpbin.org/get" # test용 api
headers = { 'user-agent':'myPythonApp_1.0.0'}

with requests.Session() as s:
    r=s.get(url,headers=headers)
    print(r.text)