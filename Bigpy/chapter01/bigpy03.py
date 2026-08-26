import pandas as pd
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Py_Scrap" / "data"
file_path = DATA_DIR / "sample.xlsx"

user_list = pd.read_excel(file_path, sheet_name = 'Sheet1', engine='openpyxl')
print(user_list)