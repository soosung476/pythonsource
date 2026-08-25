import pickle
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
file_path = DATA_DIR / "setting2.txt"

f = open(file_path, "rb")

setting = [{'title':'python program'}, {'author':'soldesk'}]
f.close()
print(setting)