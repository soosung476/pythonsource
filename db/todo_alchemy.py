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

load_dotenv()
password = os.getenv("ORACLE_PASSWORD")
engine = create_engine(f"oracle+oracledb://python_user:{password}@localhost:1521/?service_name=FREEPDB1",echo=True)


class Base(DeclarativeBase):
    pass

class Todo(Base):
    __tablename__ = "TODO"

    todo_id:Mapped[int] = mapped_column(Numeric(10), Identity(start = 1, increment = 1), primary_key=True)
    title:Mapped[str] = mapped_column(String(200))
    is_done:Mapped[bool] = mapped_column(default=False)
    # Optional[datetime] : 값이 None 혹으 datetime
    created_at:Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    # created_at:Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.sysdate())

    def __repr__(self):
        status = "완료" if self.is_done else "미완료"
        return f"{self.todo_id}, {self.title}[{status}] {self.is_done} {self.created_at})>"


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
    with Session(engine) as session:
        todo = Todo(title = user_input)
        session.add(todo)
        session.commit()
        print(f"{todo.todo_id}. 등록되었습니다.")


def list_todo():
    with Session(engine) as session:
        print("-"*20)
        found = False
        stmt = select(Todo).order_by(Todo.todo_id)
        for todo in session.scalars(stmt):
            found = True
            print(todo)
        if not found:
            print("등록된 할 일이 없습니다.")

def update_todo():
    user_choice = ask_number("완료 처리할 번호를 입력해주세요: ")
    if user_choice is None:
        return
    with Session(engine) as session:
        selected = session.get(Todo,int(user_choice))
        selected.is_done = True
        session.commit()
        print("완료 되었습니다.")
        
    
def delete_todo() :
    user_choice = ask_number("삭제 처리할 번호를 입력해주세요: ")
    if user_choice is None:
        return
    with Session(engine) as session:
            selected = session.get(Todo,int(user_choice))
            session.delete(selected)
            session.commit()
            print("삭제 되었습니다.")

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
    Base.metadata.create_all(engine)
    menu()
