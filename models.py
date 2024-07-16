#models.py
from sqlalchemy import Column, Integer, String, Date  # SQLAlchemy에서 컬럼, 정수, 문자열, 날짜 타입을 가져옴
from sqlalchemy.ext.declarative import declarative_base  # declarative_base를 가져와서 모델 클래스의 베이스를 정의
from sqlalchemy.orm import sessionmaker  # 세션 생성기를 가져옴
from sqlalchemy import create_engine  # 데이터베이스 엔진 생성을 위해 가져옴

DATABASE_URL = "sqlite:///./test.db"  # SQLite 데이터베이스 파일 경로를 설정

Base = declarative_base()  # 모델 클래스 생성을 위한 베이스 클래스 생성

class User(Base):  # User 모델 정의, Base 클래스를 상속받음
    __tablename__ = "users"  # 데이터베이스 테이블 이름을 "users"로 설정
    id = Column(Integer, primary_key=True, index=True)  # ID 컬럼, 기본 키 및 인덱스 설정
    email = Column(String, unique=True, index=True)  # 이메일 컬럼, 고유 및 인덱스 설정
    hashed_password = Column(String)  # 해시된 비밀번호 컬럼
    name = Column(String)  # 사용자 이름 컬럼
    gender = Column(String)  # 성별 컬럼
    country = Column(String)  # 출신 국가 컬럼
    birthdate = Column(Date)  # 생년월일 컬럼

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

engine = create_engine(DATABASE_URL)  # 데이터베이스 엔진 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # 세션 생성기 설정, 자동 커밋 및 플러시 비활성화, 엔진 바인딩

Base.metadata.create_all(bind=engine)  # 데이터베이스 테이블을 생성
