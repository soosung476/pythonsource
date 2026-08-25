import pickle
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
file_path = DATA_DIR / "setting.txt"
# pickle 모듈은 파이썬 객체를 파일로 저장하고 읽어들임
# 저장된 상태에서 프로그램이 종료되면 객체는 자동 소멸됨

'''
f = open(DATA_DIR / "setting.txt", "wb")
setting = [{'title':'python program'}, {'author':'soldesk'}]
pickle.dump(setting,f)
f.close()

'''

f = open(file_path, "wb")
try:
    setting = [{'title':'python program'}, {'author':'soldesk'}]
    pickle.dump(setting, f)

except Exception as e:
    print(e)
finally:
    f.close()