# === Todo 관리 ===
# 1.추가 2.목록 3.완료처리 4.삭제 5.종료
# 선택 : 1

# 할일 내용을 입력하세요: 내용입력
# 등록되었습니다.

# === Todo 관리 ===
# 1.추가 2.목록 3.완료처리 4.삭제 5.종료
# 선택 : 2
# ---------------------
# 1. [미완료] 내용1 (2026-08-20 12:38:07)
#...


# === Todo 관리 ===
# 1.추가 2.목록 3.완료처리 4.삭제 5.종료
# 선택 : 3
# 완료 처리할 번호를 입력하세요 : 1
# 완료 처리되었습니다.


# === Todo 관리 ===
# 1.추가 2.목록 3.완료처리 4.삭제 5.종료
# 선택 : 4
# 삭제 처리할 번호를 입력하세요 : 1
# 삭제 되었습니다.



# 데이터베이스 테이블 구조
# todo_id 자동증가, pk
# title not null
# is_done number(1) default 0
# created_at DATE default sysdate



# 다 짜놓고 함수로 쪼갤 예정
# todo 추가 함수
import oracledb
conn = oracledb.connect(user="python_user", password="54321", dsn = "localhost:1521/FREEPDB1")
cursor= conn.cursor()

try:
    cursor.execute(
    """CREATE TABLE TODO (
    todo_id NUMBER(10) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR2(100) NOT NULL,
    is_done NUMBER(1) default 0,
    created_at DATE default sysdate NOT NULL
    )
    """
)

except oracledb.DatabaseError as e:
    error, = e.args
    if error.code != 955:
        print(error.message)
        raise


def ask_number(question:str):
    user_data = input(f"{question} ")
    try:
        user_number = int(user_data)
        return user_number
    except ValueError:
        print(f"에러 발생. 숫자를 입력해 주세요.")
        return


def add_todo():
    user_input = input("등록할 내용을 입력하세요: ").strip()
    if user_input == "":
        return
    sql = "INSERT INTO TODO (title) VALUES(:1)"
    cursor.execute(sql, (user_input,))
    conn.commit()
    print("등록되었습니다.")


def list_todo():
    cursor.execute("SELECT todo_id, title, is_done, TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') from TODO ORDER BY todo_id")
    print("-"*20)
    found = False
    for row in cursor:
        found = True
        is_completed = ""
        if row[2] == 0:
            is_completed = "미완료"
        else:
            is_completed = "완료"
        print(f"{row[0]}. [{is_completed}] {row[1]} ({row[3]})")
    if not found:
        print("등록된 할 일이 없습니다.")
def update_todo():

    user_choice = ask_number("완료 처리할 번호를 입력해주세요: ")
    if user_choice is None:
        return
    
    sql = "update TODO set is_done = 1 where todo_id = :1"
    cursor.execute(sql, (user_choice,))
    if cursor.rowcount == 1:
        conn.commit()
        print("완료 되었습니다.")
    else :
        print("정확한 값을 집어넣어 주세요.")
        
    

    
def delete_todo() :
    user_choice = ask_number("삭제 처리할 번호를 입력해주세요: ")
    if user_choice is None:
        return
    sql = "delete from TODO where todo_id = :1"
    cursor.execute(sql, (user_choice,))
    if cursor.rowcount == 1:
        conn.commit()
        print("삭제 되었습니다.")
    else :
        print("정확한 값을 집어넣어 주세요.")

def menu():
    while True:
        print("=== Todo 관리 ===")
        print("1.추가 2.목록 3.완료처리 4.삭제 5.종료")

        choice = input("선택 : ")


        if choice == '1':
            add_todo()
        elif choice == '2':
            list_todo()
        elif choice == '3':
            update_todo()
        elif choice == '4':
            delete_todo()
        elif choice =='5':
            break
        else :
            print("번호를 확인해 주세요")
    



if __name__ == "__main__":
    try:
        menu()
    finally:
        cursor.close()
        conn.close()