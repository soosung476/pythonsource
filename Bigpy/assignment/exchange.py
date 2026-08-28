import requests
import json
from pathlib import Path
from datetime import datetime
BASE_DIR = Path(__file__).resolve().parent




url = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=KRW,JPY,EUR"

res = requests.get(url)
res.raise_for_status()
data = res.json()

today = datetime.now().strftime('%Y-%m-%d')
print(today)

# print(data)
symbols = ['KRW', 'JPY', 'EUR']
results = {"date":today}
for symbol in symbols:
    print(f"{data['amount']:.0f} {data['base']} = {data['rates'][symbol]} {symbol} ")
    results[symbol] = data['rates'][symbol]

print(results)

json_path = BASE_DIR/"exchange_today.json"
with open(json_path, 'w', encoding='utf-8')  as f:
    json.dump(results, f, ensure_ascii=False, indent=2)