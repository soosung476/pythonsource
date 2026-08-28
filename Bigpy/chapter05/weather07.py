import requests
import json
from dotenv import load_dotenv
from collections import defaultdict # 키가 없어도 에러 없이 빈 리스트를 만들어 주는 딕셔너리
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
Py_Scrap = BASE_DIR.parent/"Py_Scrap"
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")



def get_5day_forecast(city):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q":city,
        "appid":API_KEY,
        "units": "metric",
        "lang":"kr"
    }

    res= requests.get(url, params=params)
    if res.status_code ==404:
        return None
    res.raise_for_status()
    data = res.json()
    # print(data)
    daily =  defaultdict(list)

    for item in data['list']:
        date = item['dt_txt'].split(" ")[0] # "2026-08-28 03:00:00" split 해서 날짜만 가져오기.
        daily[date].append(item)

    results = []
    for date, items in daily.items():
        temps = [i['main']['temp'] for i in items]
        weather_desc = items[len(items)//2]['weather'][0]['description'] # 날짜별 중간 시점 날씨를 대표

        results.append({
            "날짜": date,
            "최고기온": round(max(temps),1),
            "최저기온": round(min(temps),1),
            "날씨": weather_desc
        })
    return results # 5일치 날씨 반환

def main():
    city="Seoul"
    forecast = get_5day_forecast(city)
    
    # 예외처리
    if forecast is None:
        print("도시를 찾을 수 없음")
        return

    print(f"=== {city} 5일 예보 ===")

    for day in forecast:
        print(f"날짜: {day['날짜']} | 최고 {day['최고기온']}도 / 최저 {day['최저기온']}도 | 날씨: {day['날씨']}")

    json_path = BASE_DIR/"weather_5days.json"
    with open(json_path,'w',encoding='utf-8') as f:
        json.dump(forecast, f, ensure_ascii=False, indent=2)

    print("\n저장 완료 : weather_5days.json")
if __name__=="__main__":
    main()