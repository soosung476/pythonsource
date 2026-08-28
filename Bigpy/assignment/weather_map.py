import os
from dotenv import load_dotenv
from pathlib import Path
import requests
import csv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")



def get_weather(city):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
    "q":city,
    "appid":API_KEY,
    "lang":"kr",
    "units":"metric"
}
    res = requests.get(url, params=params)
    data = res.json()
    # print(data)
    return data

def main():
    results = []
    cities = ['ddd','Seoul','Busan','Incheon','Daegu','gwangju']
    print("=== 도시별 현재 날씨 ===")
    for city in cities:
        result = get_weather(city)
        if result['cod']=='404':
            
            print(f"{city}: 조회 실패")
        else :
            print(f"{city}: {result['main']['temp']}도, {result['weather'][0]['description']}")
            results.append({"도시":city,
                            "기온":result['main']['temp'],
                            "날씨":result['weather'][0]['description']
                            })

    hottest = max(results, key=lambda x: x['기온'])
    coolest = min(results, key=lambda x : x['기온'])
    
    print(f"가장 더운 도시:{hottest['도시']}({hottest['기온']}) ")
    print(f"가장 시원한 도시:{coolest['도시']}({coolest['기온']}) ")

    csv_path = BASE_DIR/"weather_today.csv"
    fieldnames = ["도시","기온","날씨"]
    with open(csv_path, 'w', encoding='utf-8') as f:

        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    
    
if __name__ =="__main__":
    main()