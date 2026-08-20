# 숫자야구게임
# 컴퓨터가 랜덤으로 1~9사이의 임의의 숫자를 3개 생성
# 사용자로부터 1~9 사이의 중복없는 3자리 숫자를 입력받기
# 345 -> 임의의 숫자와 비교 -> 숫자와 자리를 전부 맞추면 3스트라이크, 게임 종료
# 숫자만 맞추면 -> 볼
# 숫자와 위치를 맞추면 -> 스트라이크
# q를 입력 => 강제멈춤


# 오라클 연동
# baseball_records 테이블 생성
# record_id 자동증가
# 걸린 시간, 게임일자
import random
import time
import oracledb
import sys


def make_answer():
    '''1~9 중 중복없는 3자리 숫자 생성'''
    num_list = list(range(1,10))
    return random.sample(num_list, k=3)


def get_strike_ball(user_input, answer):
    strike= 0
    ball = 0
    for i in range(3):
        if user_input[i] == answer[i]:
            strike +=1
        elif answer[i] in user_input:
            ball += 1
    print(f"strike: {strike}, ball: {ball}")
    if strike == 3:
        return True
    else:
        return False


attempts = 0
is_quit = False
computer = make_answer()
start = time.time()


while True :

    user = input("숫자 3개를 입력하세요 (종료:q)").strip()
    if user == 'q':
        print("게임을 종료합니다.")
        is_quit = True
        break

    if len(user) != 3:
        print("3자리를 입력해주세요")
        continue

    if not user.isdigit():
        print("숫자가 아님")
        continue

    if '0' in user:
        print("0을 제외한 숫자를 넣어주세요")
        continue

    if len(set(user)) !=3:
        print("숫자가 중복되었습니다.")
        continue

    user_num = list(map(int,user))
    attempts += 1
    
    if get_strike_ball(user_num,computer):
        print("VICTORY")

        break

        
end = time.time()
elapsed = end - start


    
if is_quit:
    sys.exit()

print(f"시도횟수: {attempts}, 걸린시간 : {elapsed:.2f}초")

with oracledb.connect(
    user = "python_user",
    password = "54321",
    dsn = "localhost:1521/FREEPDB1"
) as conn:
    cursor = conn.cursor()


    try:
        cursor.execute(
            """CREATE TABLE baseball_records (
            record_id  NUMBER(10) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            play_time  NUMBER(10,2) NOT NULL,
            game_date  DATE DEFAULT SYSDATE NOT NULL
            )""" 
        )
    except oracledb.DatabaseError as e:
        error, = e.args
        if error.code != 955:
            print(error.message)
            raise

    sql = "INSERT INTO baseball_records (play_time) VALUES (:1)"
    cursor.execute(sql, (elapsed,))
    conn.commit()
