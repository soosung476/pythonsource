import sys
import io
from bs4 import BeautifulSoup   # pip install beautifulsoup4
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Py_Scrap" / "data"
SCRAP_DIR = BASE_DIR.parent/"Py_Scrap"

'''
<html>
<body>
<ul id="cars">
  <li id="ge">Genesis</li>
  <li id="av">Avante</li>
  <li id="so">Sonata</li>
  <li id="gr">Grandeur</li>
  <li id="tu">Tucson</li>
</ul>
</body>
</html>
'''

fp = open(SCRAP_DIR/"cars.html", encoding='utf-8')

soup = BeautifulSoup(fp, 'html.parser')
print(soup)


# 함수
def car_func(select):
    print("car_func", soup.select_one(select).string)

# 메인
car_func("#gr")                 # 가장 단순
car_func("li#gr")               # li 이면서 아이디가 gr
car_func("ul>#gr")              # ul의 직계자식중 아이디가 gr : 가장 많이 쓰이는 방법
car_func("#cars #gr")           # 아이디가 #cars이면서 그 아래 어딘가에 있는 아이디가 gr
car_func("#cars>#gr")           # 아이디가 #cars의 직계자식중 id가 gr
car_func("li[id='gr']")

print("-"*40)

# 람다식(매개변수:q)
car_lambda= lambda q: print("car_func: ", soup.select_one(q).string)

car_lambda("#gr")                 # 가장 단순
car_lambda("li#gr")               # li 이면서 아이디가 gr
car_lambda("ul>#gr")              # ul의 직계자식중 아이디가 gr : 가장 많이 쓰이는 방법
car_lambda("#cars #gr")           # 아이디가 #cars이면서 그 아래 어딘가에 있는 아이디가 gr
car_lambda("#cars>#gr")           # 아이디가 #cars의 직계자식중 id가 gr
car_lambda("li[id='gr']")


print("-"*40)
print("car_func", soup.select("li")[3].string) # select_one 한가지 엘리먼트, select가 전체
print("car_func", soup.find_all("li")[3].string) # find 가 한가지 엘리먼트, find_all 이 전체