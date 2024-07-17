# SQLAlchemy 모듈 임포트
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from datetime import datetime  # datetime 모듈에서 datetime 클래스 import

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

    posts = relationship("Post", back_populates="author")  # 사용자와 게시글 간의 일대다 관계 설정

# 게시글 정보를 저장하는 데이터베이스 모델 클래스
class Post(Base):
    """
    게시글 정보를 저장하는 데이터베이스 모델 클래스.

    Attributes:
        __tablename__ (str): 데이터베이스 테이블 이름 "posts"
        id (int): 게시글 고유 식별자, 기본 키 및 인덱스
        title (str): 게시글 제목
        company_name (str): 회사 이름
        content (Text): 게시글 내용
        hashtags (str): 해시태그
        job_type (str): 직종
        career (str): 경력
        author_id (int): 작성자 고유 식별자, 외래 키
    """
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)  # 기본 키 및 인덱스 역할을 수행하는 정수형 컬럼.
    title = Column(String, index=True)  # 게시글 제목을 저장하는 문자열 컬럼
    company_name = Column(String, index=True)  # 회사 이름을 저장하는 문자열 컬럼
    content = Column(Text)  # 게시글 내용을 저장하는 텍스트형 컬럼
    hashtags = Column(String, index=True)  # 해시태그를 저장하는 문자열 컬럼
    job_type = Column(String, index=True)  # 직종을 저장하는 문자열 컬럼
    career = Column(String, index=True)  # 경력을 저장하는 문자열 컬럼
    deadline = Column(String, index=True)
    salary = Column(String, index=True)
    joblocation= Column(String, index=True)
    Education= Column(String,index=True)
    author_id = Column(Integer, ForeignKey("users.id"))  # 작성자 고유 식별자를 저장하는 정수형 외래 키 컬럼
    


    author = relationship("User", back_populates="posts")  # 게시글과 작성자 간의 일대다 관계 설정

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    name= Column(String,index=True)
    gender= Column(String,index=True)
    email= Column(String,index=True)
    phonenumber=Column(String,index=True)
    education=Column(String,index=True)
    location=Column(String,index=True)
    introduce=Column(String,index=True)

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)  # SQLite 데이터베이스 엔진을 생성하고 파일 경로를 설정함

# 데이터베이스 세션 생성기 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 세션 생성기를 설정하여 SQLAlchemy 세션을 만들 때 자동 커밋과 자동 플러시 기능을 비활성화하고,
# 위에서 생성한 데이터베이스 엔진과 연결(bind)함

# 데이터베이스에 선언된 모든 테이블 생성
Base.metadata.create_all(bind=engine)  # SQLAlchemy 모델에서 정의한 모든 테이블을 데이터베이스에 생성함
