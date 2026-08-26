import requests, json
# 쿠키 활용, 타임아웃 설정, POST 요청

# 쿠키 객체 생성
jar = requests.cookies.RequestsCookieJar()

# /cookies 경로에서 사용할 쿠키 설정 (name = kim)
jar.set('name','kim',domain = 'httpbin.org',path='/cookies')

# get 요청
r = requests.get('http://httpbin.org/cookies', cookies=jar)
r.raise_for_status()
# print(r.text)

# timeout 설정
# 3초안에 응답 안하면 예외처리 해버리고 강제 종료.
r = requests.get('https://github.com', timeout=3)
# print(r.text)

r = requests.post('http://httpbin.org/post', data={'name':'kim'}, cookies=jar)
# print(r.text)


payload1 = {'key1':'values1','key2':'values2'} # dict
payload2 = (('key1','values1'),('key2','values2')) # tuple
payload3 = {'some':'nice'}

r = requests.post('http://httpbin.org/post', data=payload1)
print(r.text)
print("-"*40)
r = requests.post('http://httpbin.org/post', data=payload2)
print(r.text)
print("-"*40)
r = requests.post('http://httpbin.org/post', data=payload3)
print(r.text)
print("-"*40)