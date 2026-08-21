# csv 파일의 내용을 테이블에 insert 하기 (단, 테이블이 비어 있는 경우)

# 테이블의 내용을 읽어서 무작위 문제 내기 (중복x)
# Question #1 : 'apple'의 뜻은?
# 1. 버스
# 2. 남편
# 3. 수줍은
# 4. 사과
# 보기 3개는 무작위로 meaning에서 뽑음

# 결과 : 3 / 5 정답

# 결과를 테이블에 저장하기
# record_id, total, correct, regdate

import oracledb
import csv
import random
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR/"data"/"words.csv"

conn= oracledb.connect(user = "python_user", password="54321", dsn = "localhost:1521/FREEPDB1")
cursor = conn.cursor()


def load_words_from_csv():
    with open (CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        return [tuple(row) for row in reader]
    # [(apple,사과),...] 형태로 100개 나옴



def seed_words_if_empty():
    cursor.execute("SELECT COUNT(*) FROM words")
    count = cursor.fetchone()[0]
    if count >0:
        print(f"이미 words 테이블에 {count}개 있음. 건너뜀")
        return

    data = load_words_from_csv()
    sql = "INSERT INTO words (word, meaning) VALUES (:1, :2)"
    cursor.executemany(sql,data)
    conn.commit()


def run_quiz():

    cursor.execute("SELECT word, meaning FROM words")
    rows = cursor.fetchall()
    TOTAL = 5
    # rows의 결과는 [(apple,사과),(banana,바나나),(),...] 형태로 나오겠지?
    # rows에 랜덤으로 하나를 뽑자.
    quiz_list = random.sample(rows,TOTAL)
    # quiz_list 에는 [(),(),(),(),()] 다섯 개의 튜플값이 리스트 형태로 들어간다
    
    all_meanings = [ m for w, m in rows ]
    count_correct = 0
    # 이제 문제를 낼 때마다 rows에서 quiz_list에 없는 값 3개를 뽑아서 가져오는거야.
    for i, (word, correct) in enumerate(quiz_list, start=1):
        # 보기값 3개 뽑기
        wrong = random.sample([ m for m in all_meanings if m != correct ], 3)
        options = wrong + [correct]
        random.shuffle(options)

        answer_no = options.index(correct) + 1   # 정답 번호
        print(f"\n Question #{i} : {word}의 뜻은?")
        for number, option in enumerate(options, start=1):
            print(f"{number}. {option}")


        while True:
            user_input = input("정답번호는? : ")
            if user_input.isdigit() and 1<= int(user_input) <=4:
                user_answer= int(user_input)
                break
            else :
                print("번호를 입력해 주세요.")

        if(user_answer == answer_no):
            print("정답입니다!")
            count_correct += 1

        else :
            print("오답입니다.")         
    print(f"\n 결과 : {count_correct}/{TOTAL} 정답")

    sql = "INSERT INTO quiz_records (TOTAL, CORRECT, REGDATE) VALUES (:1, :2, :3)"
    cursor.execute(sql, (TOTAL, count_correct, datetime.now()))
    conn.commit()


if __name__ == "__main__":
    try:
        seed_words_if_empty()
        run_quiz()
    finally:
        cursor.close()
        conn.close()