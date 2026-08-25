import requests
from bs4 import BeautifulSoup

url = "https://www.melon.com/chart/index.htm"

headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

tem_rank = soup.select("#tb_list tr .rank")[1:11]
rank = []
for i in tem_rank:
    rank.append(i.text)
print(rank)

temp_title = soup.select("#tb_list tr .wrap_song_info .rank01")[0:10]
title = []
for i in temp_title:
    title.append(i.text.strip())
print(title)

temp_author = soup.select("#tb_list tr .wrap_song_info .rank02>a")[0:10]
author = []
for i in temp_author:
    i = i.text.replace('\xa0', "")
    author.append(i.strip())
    
print(author)

for i in range(10):
    print(f"{rank[i]}위 | {title[i]} - {author[i]}")