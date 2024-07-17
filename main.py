from fastapi import FastAPI, Depends, HTTPException, status  # FastAPI 관련 모듈 임포트
from sqlalchemy.orm import Session  # SQLAlchemy ORM 세션 관련 모듈 임포트
from passlib.context import CryptContext  # PassLib 패스워드 해싱 관련 모듈 임포트
from pydantic import BaseModel, EmailStr  # Pydantic 모듈에서 BaseModel, EmailStr 임포트
from datetime import date, datetime, timedelta  # 날짜 및 시간 관련 모듈 임포트
from jose import JWTError, jwt  # JWT 관련 모듈 임포트
from fastapi.security import OAuth2PasswordBearer  # FastAPI OAuth2 비밀번호 베어러 임포트
from models import User, Post, SessionLocal, engine, Base  # 데이터베이스 모델 및 세션 관련 임포트
from fastapi.middleware.cors import CORSMiddleware



# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()  # FastAPI 애플리케이션 객체 생성

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용, 보안상 필요한 도메인으로 제한할 수도 있습니다.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 비밀번호 해시 알고리즘 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your_secret_key"  # JWT 서명을 위한 비밀 키
ALGORITHM = "HS256"  # JWT 알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 액세스 토큰 만료 시간 (분)

# Pydantic 모델 정의
class UserBase(BaseModel):
    email: EmailStr  # 사용자 이메일 주소
    name: str  # 사용자 이름
    gender: str  # 사용자 성별
    country: str  # 사용자 출신 국가
    birthdate: date  # 사용자 생년월일

class UserCreate(UserBase):
    password: str  # 사용자 비밀번호

class UserLogin(BaseModel):
    email: EmailStr  # 사용자 로그인 이메일 주소
    password: str  # 사용자 로그인 비밀번호

class Token(BaseModel):
    access_token: str  # 발급된 액세스 토큰
    token_type: str  # 토큰 타입 (Bearer)

class TokenData(BaseModel):
    email: str | None = None  # 토큰 데이터의 이메일 필드, 초기값은 None

class PostBase(BaseModel):
    title: str  # 게시글 제목
    company_name: str  # 회사 이름
    hashtags: str  # 해시태그
    job_type: str  # 직종
    career: str  # 경력
    deadline :str
    salary :str
    joblocation:str
    Education:str

class PostCreate(PostBase):
    content: str  # 게시글 내용

class PostResponse(PostBase):
    id: int  # 게시글 ID
    author_id: int  # 작성자 ID

    class Config:
        from_attributes = True  # ORM 모델과 호환되도록 설정

class PostResponse2(BaseModel):
    id: int
    company_name : str
    title: str
    hashtags : str
    author_id: int

# 데이터베이스 세션을 가져오는 의존성 함수
def get_db():
    """
    데이터베이스 세션을 가져오는 의존성 함수.
    FastAPI의 Depends 데코레이터를 통해 다른 함수에서 세션을 인자로 받을 수 있도록 함.
    """
    db = SessionLocal()  # 데이터베이스 세션을 생성함
    try:
        yield db  # 생성된 데이터베이스 세션을 반환함
    finally:
        db.close()  # 데이터베이스 세션을 닫음

# 비밀번호 해시화 함수
def get_password_hash(password):
    """
    비밀번호를 해시화하여 저장하기 위한 함수.
    passlib의 CryptContext를 사용하여 bcrypt 해시 알고리즘을 적용함.
    """
    return pwd_context.hash(password)

# 비밀번호 검증 함수
def verify_password(plain_password, hashed_password):
    """
    입력된 평문 비밀번호와 저장된 해시화된 비밀번호를 비교하여 일치 여부를 확인하는 함수.
    """
    return pwd_context.verify(plain_password, hashed_password)

# 사용자 인증 함수
def authenticate_user(db: Session, email: str, password: str):
    """
    사용자 로그인 인증을 위한 함수.
 
    Parameters:
    - db (Session): SQLAlchemy 세션 객체
    - email (str): 사용자 이메일 주소
    - password (str): 사용자 비밀번호

    Returns:
    - Optional[User]: 인증된 사용자 객체 또는 None

    설명:
    - 입력된 이메일 주소를 사용하여 데이터베이스에서 사용자를 조회함.
    - 조회된 사용자 객체가 없거나 입력된 비밀번호가 사용자의 해시된 비밀번호와 일치하지 않으면 None을 반환함.
    - 그렇지 않으면 인증된 사용자 객체를 반환함.
    """
    user = db.query(User).filter(User.email == email).first()  # 이메일 주소로 사용자를 조회함
    if not user or not verify_password(password, user.hashed_password):
        return None  # 사용자가 조회되지 않거나 비밀번호가 일치하지 않으면 None을 반환함
    return user  # 인증된 사용자 객체를 반환함

# 액세스 토큰 생성 함수
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    JWT를 사용하여 액세스 토큰을 생성하는 함수.

    Parameters:
    - data (dict): JWT에 포함될 데이터
    - expires_delta (timedelta | None): 만료 시간을 설정하는 timedelta 객체 (기본값: None)

    Returns:
    - str: 생성된 JWT 액세스 토큰

    설명:
    - 입력된 데이터를 복사하여 to_encode에 저장함.
    - expires_delta가 주어졌을 경우, 현재 시간에 expires_delta를 더하여 만료 시간을 계산함.
      expires_delta가 주어지지 않으면 기본적으로 15분 후의 시간을 만료 시간으로 설정함.
    - to_encode에 만료 시간(exp)을 추가함.
    - SECRET_KEY를 사용하여 ALGORITHM 알고리즘으로 to_encode를 인코딩하여 JWT를 생성함.
    """
    to_encode = data.copy()  # 입력된 데이터를 복사하여 새로운 딕셔너리 to_encode에 저장함
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # expires_delta가 주어졌을 때의 만료 시간 계산
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # 기본적인 만료 시간 설정 (15분 후)
    to_encode.update({"exp": expire})  # to_encode 딕셔너리에 만료 시간(exp)을 추가함
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # JWT를 생성하여 encoded_jwt에 저장함
    return encoded_jwt  # 생성된 JWT 액세스 토큰을 반환함

# 회원가입 엔드포인트
@app.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    사용자 회원가입을 처리하는 엔드포인트.
    입력된 사용자 정보를 데이터베이스에 저장하고, 성공 메시지를 반환함.
    
    Parameters:
    - user (UserCreate): 회원가입을 위한 사용자 정보를 담은 Pydantic 모델
    - db (Session): SQLAlchemy 세션 객체
    
    Returns:
    - dict: 성공적으로 등록된 사용자 메시지
    
    Raises:
    - HTTPException: 이미 등록된 이메일 주소를 사용하여 회원가입을 시도했을 경우 400 예외를 발생시킴
    """
    db_user = db.query(User).filter(User.email == user.email).first()  # 데이터베이스에서 이메일로 사용자를 조회함
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )  # 이미 등록된 이메일 주소일 경우 HTTP 400 예외를 발생시킴
    hashed_password = get_password_hash(user.password)  # 입력된 비밀번호를 해시화하여 저장함
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        gender=user.gender,
        country=user.country,
        birthdate=user.birthdate
    )  # 입력된 사용자 정보로 새로운 User 객체를 생성함
    db.add(new_user)  # 데이터베이스에 새로운 사용자 정보를 추가함
    db.commit()  # 데이터베이스의 변경 사항을 커밋함
    db.refresh(new_user)  # 데이터베이스에서 최신 상태로 사용자 정보를 새로고침함
    return {"message": "User registered successfully"}  # 회원가입 성공 메시지를 반환함

# 로그인 엔드포인트
@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    사용자 로그인을 처리하는 엔드포인트.
    입력된 이메일 주소와 비밀번호를 검증하여, 액세스 토큰을 발급함.
    
    Parameters:
    - user (UserLogin): 사용자 로그인 정보를 담은 Pydantic 모델
    - db (Session): SQLAlchemy 세션 객체
    
    Returns:
    - Token: 발급된 액세스 토큰
    
    Raises:
    - HTTPException: 잘못된 이메일 주소 또는 비밀번호로 로그인 시도했을 경우 401 예외를 발생시킴
    """
    db_user = authenticate_user(db, user.email, user.password)  # 사용자 로그인 인증을 수행함
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )  # 인증에 실패한 경우 HTTP 401 예외를 발생시킴
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 액세스 토큰의 만료 시간 설정
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )  # 인증된 사용자 정보를 바탕으로 액세스 토큰을 생성함
    return {"access_token": access_token, "token_type": "bearer"}  # 발급된 액세스 토큰을 반환함

# 게시글 작성 엔드포인트
@app.post("/posts/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """
    사용자가 게시글을 작성하는 엔드포인트.
    입력된 게시글 정보를 데이터베이스에 저장하고, 작성된 게시글을 반환함.
    
    Parameters:
    - post (PostCreate): 게시글 작성을 위한 정보를 담은 Pydantic 모델
    - db (Session): SQLAlchemy 세션 객체
    
    Returns:
    - PostResponse: 작성된 게시글 정보를 담은 Pydantic 모델
    """
    db_post = Post(**post.dict(), author_id=1)  # 입력된 게시글 정보로 Post 객체를 생성함
    db.add(db_post)  # 데이터베이스에 새로운 게시글 정보를 추가함
    db.commit()  # 데이터베이스의 변경 사항을 커밋함
    db.refresh(db_post)  # 데이터베이스에서 최신 상태로 게시글 정보를 새로고침함
    return db_post  # 작성된 게시글 정보를 반환함

# 게시글 목록 조회 엔드포인트
@app.get("/posts/", response_model=list[PostResponse2])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    게시글 목록을 조회하는 엔드포인트.
    입력된 페이징 파라미터에 따라 데이터베이스에서 게시글을 조회하고, 조회된 게시글 목록을 반환함.
    
    Parameters:
    - skip (int): 건너뛸 게시글 개수
    - limit (int): 조회할 게시글 개수
    - db (Session): SQLAlchemy 세션 객체
    
    Returns:
    - list[PostResponse]: 조회된 게시글 목록을 담은 리스트
    """
    posts = db.query(Post).offset(skip).limit(limit).all()  # 데이터베이스에서 게시글을 조회함
    return [
        PostResponse2(id=post.id,company_name=post.company_name,hashtags=post.hashtags, title=post.title, author_id=post.author_id)
        for post in posts
    ]

# 개별 게시글 조회 엔드포인트
@app.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """
    특정 게시글을 조회하는 엔드포인트.
    입력된 게시글 ID를 사용하여 데이터베이스에서 게시글을 조회하고, 조회된 게시글을 반환함.
    
    Parameters:
    - post_id (int): 조회할 게시글의 ID
    - db (Session): SQLAlchemy 세션 객체
    
    Returns:
    - PostResponse: 조회된 게시글 정보를 담은 Pydantic 모델
    
    Raises:
    - HTTPException: 해당 게시글 ID가 존재하지 않을 경우 404 예외를 발생시킴
    """
    post = db.query(Post).filter(Post.id == post_id).first()  # 게시글 ID를 사용하여 데이터베이스에서 게시글을 조회함
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")  # 게시글이 존재하지 않으면 HTTP 404 예외를 발생시킴
    return post  # 조회된 게시글 정보를 반환함

# 게시글 수정 엔드포인트
@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db)):
    """
    사용자가 게시글을 수정하는 엔드포인트.
    입력된 게시글 ID와 수정할 정보를 사용하여 데이터베이스에서 게시글을 수정하고, 수정된 게시글을 반환함.
    
    Parameters:
    - post_id (int): 수정할 게시글의 ID
    - post (PostCreate): 수정할 게시글 정보를 담은 Pydantic 모델
    - db (Session): SQLAlchemy 세션 객체
    
    Returns:
    - PostResponse: 수정된 게시글 정보를 담은 Pydantic 모델
    
    Raises:
    - HTTPException: 해당 게시글 ID가 존재하지 않을 경우 404 예외를 발생시킴
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()  # 게시글 ID를 사용하여 데이터베이스에서 게시글을 조회함
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")  # 게시글이 존재하지 않으면 HTTP 404 예외를 발생시킴
    for key, value in post.dict().items():
        setattr(db_post, key, value)  # 입력된 수정 정보로 게시글 객체를 업데이트함
    db.commit()  # 데이터베이스의 변경 사항을 커밋함
    db.refresh(db_post)  # 데이터베이스에서 최신 상태로 게시글 정보를 새로고침함
    return db_post  # 수정된 게시글 정보를 반환함

# 게시글 삭제 엔드포인트
@app.delete("/posts/{post_id}", response_model=dict)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """
    사용자가 게시글을 삭제하는 엔드포인트.
    입력된 게시글 ID를 사용하여 데이터베이스에서 게시글을 삭제하고, 삭제 성공 메시지를 반환함.
    
    Parameters:
    - post_id (int): 삭제할 게시글의 ID
    - db (Session): SQLAlchemy 세션 객체
    
    Returns:
    - dict: 게시글 삭제 성공 메시지
    
    Raises:
    - HTTPException: 해당 게시글 ID가 존재하지 않을 경우 404 예외를 발생시킴
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()  # 게시글 ID를 사용하여 데이터베이스에서 게시글을 조회함
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")  # 게시글이 존재하지 않으면 HTTP 404 예외를 발생시킴
    db.delete(db_post)  # 데이터베이스에서 게시글을 삭제함
    db.commit()  # 데이터베이스의 변경 사항을 커밋함
    return {"message": "Post deleted successfully"}  # 게시글 삭제 성공 메시지를 반환함
@app.get("/")
async def root():
    return {"message": "I love you"}
