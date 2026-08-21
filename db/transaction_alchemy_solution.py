import os
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from sqlalchemy import (
    URL,
    DateTime,
    Identity,
    Numeric,
    String,
    create_engine,
    func,
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

load_dotenv()

password = os.getenv("ORACLE_PASSWORD")
if not password:
    raise RuntimeError("ORACLE_PASSWORD 환경변수가 설정되지 않았습니다.")

# f-string으로 URL을 만들면 비밀번호에 @ / : # 같은 문자가 있을 때 파싱이 깨진다.
# URL.create()는 자동으로 이스케이프해준다.
engine = create_engine(
    URL.create(
        "oracle+oracledb",
        username="python_user",
        password=password,
        host="localhost",
        port=1521,
        query={"service_name": "FREEPDB1"},
    ),
    echo=False,
)


class Base(DeclarativeBase):
    pass


class Transactions(Base):
    __tablename__ = "transactions"

    # Numeric 컬럼은 파이썬에서 Decimal로 돌아오므로 Mapped[int]가 아니라 Mapped[Decimal]
    tx_id: Mapped[Decimal] = mapped_column(
        Numeric(10), Identity(start=1, increment=1), primary_key=True
    )
    tx_type: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal] = mapped_column(Numeric(20))
    # Oracle은 빈 문자열('')을 NULL로 저장한다. NOT NULL이면 ORA-01400이 난다.
    memo: Mapped[Optional[str]] = mapped_column(String(100))
    reg_date: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        day = self.reg_date.strftime("%Y-%m-%d") if self.reg_date else "날짜없음"
        return f"{self.tx_id}. [{self.tx_type}] {self.amount:,}원 - {self.memo or '-'} ({day})"


# ---------- 입력 헬퍼 ----------

def ask_tx_type() -> str:
    while True:
        value = input("수입/지출 중 하나를 입력해주세요 : ").strip()
        if value in ("수입", "지출"):
            return value
        print("수입/지출만 입력해주세요.")


def ask_amount() -> Decimal:
    while True:
        raw = input("금액 : ").strip().replace(",", "")
        if raw.isdigit() and int(raw) > 0:
            return Decimal(raw)
        print("0보다 큰 숫자만 입력해주세요.")


def ask_memo() -> Optional[str]:
    memo = input("상세정보 : ").strip()
    return memo or None


def ask_reg_date() -> datetime:
    while True:
        raw = input("날짜 'YYYY-MM-DD' (엔터 시 오늘) : ").strip()
        if not raw:
            # datetime.now()는 시분초가 붙어 다른 값과 형식이 어긋난다. 자정으로 통일.
            return datetime.combine(date.today(), time.min)
        try:
            return datetime.strptime(raw, "%Y-%m-%d")
        except ValueError:
            print("YYYY-MM-DD 형식으로 입력해주세요.")


# ---------- 기능 ----------

def add_transaction() -> None:
    transaction = Transactions(
        tx_type=ask_tx_type(),
        amount=ask_amount(),
        memo=ask_memo(),
        reg_date=ask_reg_date(),
    )

    # expire_on_commit=False: commit 후 tx_id를 읽을 때 재조회(SELECT)가 발생하지 않는다.
    with Session(engine, expire_on_commit=False) as session:
        try:
            session.add(transaction)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"등록에 실패했습니다: {e}")
            return

    print(f"{transaction.tx_id}번 내역이 등록되었습니다.")


def list_transaction() -> None:
    with Session(engine) as session:
        stmt = select(Transactions).order_by(
            Transactions.reg_date.asc(), Transactions.tx_id.asc()
        )
        transactions = session.scalars(stmt).all()

    if not transactions:
        print("등록된 데이터가 없습니다.")
        return

    print("-" * 50)
    for transaction in transactions:
        print(transaction)
    print("-" * 50)


def monthly_summary() -> None:
    user_month = input("월별 합계금액 'YYYY-MM'을 입력해주세요 : ").strip()
    try:
        start = datetime.strptime(user_month, "%Y-%m")
    except ValueError:
        print("YYYY-MM 형식으로 입력해주세요.")
        return

    end = start + relativedelta(months=1)

    with Session(engine) as session:
        stmt = (
            select(Transactions.tx_type, func.sum(Transactions.amount))
            .where(Transactions.reg_date >= start, Transactions.reg_date < end)
            .group_by(Transactions.tx_type)
        )
        totals = dict(session.execute(stmt).all())

    if not totals:
        print("요청하신 월의 가계부 내역은 없습니다.\n")
        return

    income = totals.get("수입", Decimal(0))
    expense = totals.get("지출", Decimal(0))

    print("-" * 50)
    print(f"{user_month} 수입 : {income:,}원")
    print(f"{user_month} 지출 : {expense:,}원")
    print(f"{user_month} 잔액 : {income - expense:,}원")
    print("-" * 50)


def menu() -> None:
    while True:
        print("\n1. 내역 추가,  2. 전체 조회,  3. 월별 합계,  4. 종료")
        user_input = input("선택해주세요 : ").strip()

        if user_input == "1":
            add_transaction()
        elif user_input == "2":
            list_transaction()
        elif user_input == "3":
            monthly_summary()
        elif user_input == "4":
            print("종료합니다.")
            break
        else:
            print("잘못된 값을 입력하셨습니다.")


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    menu()