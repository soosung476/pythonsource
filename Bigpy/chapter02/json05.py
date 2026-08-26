import simplejson as json
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Py_Scrap" / "data"

import os.path, random
import requests
import urllib.request as req

url = "https://api.github.com/repositories"
savename = DATA_DIR / "repo.json"


if not os.path.exists(savename):
    req.urlretrieve(url,savename)

item = json.load(open(savename,'r',encoding='utf-8'))
print('Type: ', type(item))

for i in item:
    print(i["full_name"]+ " - "+i["owner"]["url"])


# load - s(string) : loads 데이타베이스에 이미 저장되어 있는 데이터 읽어오기
print("-"*50)
items = json.loads(open(savename,'r',encoding='utf-8').read())
print('Type: ', type(items))

# for i in items:
#     print(i["full_name"]+ " - "+i["owner"]["url"])