import requests

res = requests.get("https://randomuser.me/api/")
data = res.json()
user = data['results'][0]

print(user['name']['first'], user['name']['last']) # 중첩 딕셔너리 접근