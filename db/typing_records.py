import random
import oracledb
import time

# 테이블 생성 typing_records
with oracledb.connect(user = "python_user", password = "54321", dsn = "localhost:1521/FREEPDB1") as conn:
    with conn.cursor() as cursor:
        sql = """CREATE TABLE typing_records (
                    record_id NUMBER(10) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    elapsed varchar2(20) not null,
                    accuracy varchar2(20) not null,
                    regdate DATE NOT NULL)"""
        try:cursor.execute(sql)
    
        except oracledb.DatabaseError as e:
            (error_obj,) = e.args
            if error_obj.code == 955:
                print(error_obj.message)
            else:
                raise



sentences = [
    "The quick brown fox jumps over the lazy dog",
    "Python is a powerful programming language",
    "Practise makes perfect every single day",
    "Oracle database stores data reliably",
    "Typing speed improves with daily practise",
]

# sentences 문장 중 임의의 문장을 출제후 사용자가 타이핑하는 시간을 잰 후 저장.
# 정확도 게산

# 걸린시간, 정확도, 날짜



target = random.choice(sentences)
print("해당 구문을 타이핑 하세요")
print ("-"*50)
print(target)
print ("-"*50)
input("준비되면 아무 키나 입력하세요") 
start = time.time()

count = 0
print("Start!!")
user_typed = input()
for a, b in zip(target, user_typed):
    if a != b:
        count += 1
count += abs(len(target)-len(user_typed))
accuracy = (1- (count/len(target)))*100
accuracy = format(accuracy, ".2f")
end = time.time()
elapsed = format(end - start, ".2f")

print(f"걸린 시간 {elapsed}초, 정확도 {accuracy}")



with oracledb.connect(user = "python_user", password = "54321", dsn = "localhost:1521/FREEPDB1") as conn:
    with conn.cursor() as cursor:
        sql = "INSERT INTO typing_records(elapsed, accuracy, regdate) values(:1,:2,sysdate)"
        cursor.execute(sql, (elapsed,accuracy))
        conn.commit()