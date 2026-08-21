from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy import Numeric, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Identity
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from dateutil.relativedelta import relativedelta

load_dotenv()
password = os.getenv("ORACLE_PASSWORD")
engine = create_engine(f"oracle+oracledb://python_user:{password}@localhost:1521/?service_name=FREEPDB1",echo=True)

class Base(DeclarativeBase):
    pass

class Transactions(Base):
    __tablename__ = "transactions"

    tx_id:Mapped[int] = mapped_column(Numeric(10), Identity(start = 1, increment = 1), primary_key=True)
    tx_type:Mapped[str] = mapped_column(String(20))
    amount:Mapped[int] = mapped_column(Numeric(20))
    memo:Mapped[str] = mapped_column(String(100))
    reg_date:Mapped[Optional[datetime]] = mapped_column(DateTime)

    def __repr__(self):
        return f"{self.tx_id}, {self.tx_type} {self.amount}원 -  {self.memo} ({self.reg_date}))>"



def add_transaction():
    while True:
        input_tx_type = input("수입/지출 중 하나를 입력해주세요 :").strip()
        if input_tx_type == "수입" or input_tx_type == "지출":
            break
        else :
            print("수입/지출만 입력해주세요")
        
    amount_input = input("금액 : ").strip()
    input_amount = 0
    if amount_input.isdigit():
        input_amount = int(amount_input)
    else :
        return
    input_memo = input("상세정보 : ").strip()
    raw_date = input("날짜 'YYYY-MM-DD' 엔터시 오늘").strip()
    if not raw_date:
        input_reg_date = datetime.now()
    else:
        input_reg_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    with Session(engine) as session:
        transaction = Transactions(tx_type=input_tx_type, amount = input_amount, memo = input_memo, reg_date = input_reg_date )
        session.add(transaction)
        session.commit()

        print(f"{transaction.tx_id} 가 등록되었습니다.")

def list_transaction():

    with Session(engine) as session:
        stmt = select(Transactions).order_by(Transactions.reg_date)
        found = False
        for transaction in session.scalars(stmt):
            found = True
            print(transaction)
        if not found :
            print("등록된 데이터가 없습니다.")

    #번호 [지출] 300000원 -용돈 (2026-08-18)
def monthly_summary():
    user_month = input("월별 합계금액 'YYYY-MM'을 입력해주세요 : ").strip()
    try:
        start = datetime.strptime(user_month + "-01", "%Y-%m-%d")
    except ValueError:
        print("YYYY-MM 형식으로 입력해주세요")
        return
    end = start + relativedelta(months=1)

    with Session(engine) as session:
        stmt = (
            select(Transactions.tx_type, func.sum(Transactions.amount).label("total_amount"))
            .where(Transactions.reg_date >= start, Transactions.reg_date < end)
            .group_by(Transactions.tx_type)
        )
        rows = session.execute(stmt).all()

    if not rows:
        print("요청하신 월 가계부 내역은 없습니다.\n")
        return

    print("-" * 50)
    for tx_type, total in rows:
        print(f"{tx_type}: {total:,}원")
    print("-" * 50)


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
    Base.metadata.create_all(engine)
    menu()

        