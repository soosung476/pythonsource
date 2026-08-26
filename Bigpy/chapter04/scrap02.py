import requests, json

s = requests.Session()
url = "http://httpbin.org/get" # test용 api
r = s.get(url)
print(r.status_code)
print(r.ok)

print("---------------------------------------")
r = s.get('https://jsonplaceholder.typicode.com/posts/1')
print('1: ',r.text)
print('2: ', r.json())
print('3: ', r.json().keys())
print('4: ', r.json().values())
print('5: ', r.encoding)
print('6: ', r.content)
print('7: ', r.raw)

print("---------------------------------------")
# 세션 시작

with requests.Session() as s:
    # Get으로 stream 요청
    r = s.get('http://httpbin.org/stream/20', stream= True)
    if r.status_code ==200:
        for line in r.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                print(data)
    else :
        print(f"요청을 실패해습니다. 상태코드: {r.status_code}")

