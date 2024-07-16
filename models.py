# models.py

# SQLAlchemy 모듈 임포트
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# SQLite 데이터베이스 파일 경로
DATABASE_URL = "sqlite:///./test.db"

# SQLAlchemy의 기본 모델 클래스를 선언
Base = declarative_base()

# 사용자 정보를 저장하는 데이터베이스 모델 클래스
class User(Base):
    """
    사용자 정보를 저장하는 데이터베이스 모델 클래스.

    Attributes:
        __tablename__ (str): 데이터베이스 테이블 이름 "users"
        id (int): 사용자 고유 식별자, 기본 키 및 인덱스
        email (str): 사용자 이메일 주소, 고유하고 인덱싱됨
        hashed_password (str): 해시된 사용자 비밀번호
        name (str): 사용자 이름
        gender (str): 사용자 성별
        country (str): 사용자 출신 국가
        birthdate (Date): 사용자 생년월일
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # 기본 키 및 인덱스 역할을 수행하는 정수형 컬럼
    email = Column(String, unique=True, index=True)  # 고유한 이메일 주소를 저장하는 문자열 컬럼
    hashed_password = Column(String)  # 해시된 비밀번호를 저장하는 문자열 컬럼
    name = Column(String)  # 사용자 이름을 저장하는 문자열 컬럼
    gender = Column(String)  # 사용자 성별을 저장하는 문자열 컬럼
    country = Column(String)  # 사용자 출신 국가를 저장하는 문자열 컬럼
    birthdate = Column(Date)  # 사용자 생년월일을 저장하는 날짜형 컬럼

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)  # SQLite 데이터베이스 엔진을 생성하고 파일 경로를 설정함

# 데이터베이스 세션 생성기 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 세션 생성기를 설정하여 SQLAlchemy 세션을 만들 때 자동 커밋과 자동 플러시 기능을 비활성화하고,
# 위에서 생성한 데이터베이스 엔진과 연결(bind)함

# 데이터베이스에 선언된 모든 테이블 생성
Base.metadata.create_all(bind=engine)  # SQLAlchemy 모델에서 정의한 모든 테이블을 데이터베이스에 생성함
