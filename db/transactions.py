import oracledb
from datetime import datetime
conn = oracledb.connect(user="python_user", password="54321", dsn = "localhost:1521/FREEPDB1")
cursor= conn.cursor()


def add_transaction():
    while True:
        tx_type = input("수입/지출 중 하나를 입력해주세요 :").strip()
        if tx_type == "수입" or tx_type == "지출":
            break
        else :
            print("수입/지출만 입력해주세요")
        
    amount_input = input("금액 : ").strip()
    amount = 0
    if amount_input.isdigit:
        amount = int(amount_input)
    else :
        return
    
    memo = input("상세정보 : ").strip()
    reg_date = input("날짜 'YYYY-MM-DD' 엔터시 오늘").strip()
    if not reg_date:
        reg_date = datetime.now().strftime("%Y-%m-%d")
    sql = "INSERT INTO TRANSACTIONS(tx_type, amount, memo, reg_date) VALUES (:1, :2, :3, TO_DATE(:4 , 'YYYY-MM-DD'))"
    cursor.execute(sql, (tx_type, amount, memo, reg_date,))
    conn.commit()
    
def list_transaction():


    sql = "select tx_id, tx_type, amount, memo, reg_date  from TRANSACTIONS order by reg_date"
    cursor.execute(sql)
    found = False

    for row in cursor:
        found = True
        print(f"{row[0]} [{row[1]}] {row[2]}원 - {row[3]} ({row[4]})")

    if not found :
        print("등록된 데이터가 없습니다.")

    #번호 [지출] 300000원 -용돈 (2026-08-18)
def monthly_summary():
    user_month = input("월별 합계금액 'YYYY-MM'을 입력해주세요")

    sql = """SELECT t.TX_TYPE , sum(t.AMOUNT )
                FROM TRANSACTIONS t 
                WHERE t.REG_DATE >= TO_DATE(:ym||'-01', 'YYYY-MM-DD')
                AND t.REG_DATE < ADD_MONTHS(TO_DATE(:ym||'-01', 'YYYY-MM-DD'),1)
                GROUP BY t.TX_TYPE 
                """
    cursor.execute(sql, {"ym": user_month})
    rows = cursor.fetchall()
    if not rows:
        print("해당 월의 내역은 없습니다.")
        return
    for row in rows:
        print(f"{row[0]}: {row[1]}원")

def menu():
    while True:
        print("1. 내역 추가,  2. 전체 조회,  3. 월별 합계,  4. 종료")
        user_input = input("선택해주세요 : ")
        
        if user_input =='1':
            add_transaction()
        elif user_input =='2':
            list_transaction()
        elif user_input =='3':
            monthly_summary()
        elif user_input =='4':
            break
        else:
            print("잘못된 값을 입력하셨습니다.")


if __name__ == "__main__":
    try:
        menu()
    finally:
        conn.close()
        