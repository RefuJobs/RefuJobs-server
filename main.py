from fastapi import FastAPI, Depends, HTTPException, status  # FastAPI 관련 모듈 임포트
from sqlalchemy.orm import Session  # SQLAlchemy ORM 세션 관련 모듈 임포트
from passlib.context import CryptContext  # PassLib 패스워드 해싱 관련 모듈 임포트
from pydantic import BaseModel, EmailStr  # Pydantic 모듈에서 BaseModel, EmailStr 임포트
from datetime import date, datetime, timedelta  # 날짜 및 시간 관련 모듈 임포트
from jose import JWTError, jwt  # JWT 관련 모듈 임포트
from fastapi.security import OAuth2PasswordBearer  # FastAPI OAuth2 비밀번호 베어러 임포트
from models import User, Post, SessionLocal, engine, Base  # 데이터베이스 모델 및 세션 관련 임포트

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()  # FastAPI 애플리케이션 객체 생성

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
    experience: str  # 경력

class PostCreate(PostBase):
    content: str  # 게시글 내용

class PostResponse(PostBase):
    id: int  # 게시글 ID
    author_id: int  # 작성자 ID
    created_at: datetime  # 작성 시간

    class Config:
        from_attributes = True  # ORM 모델과 호환되도록 설정

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
    )  # 새로운 User 객체를 생성하여 데이터베이스에 저장할 사용자 정보를 설정함
    db.add(new_user)  # 데이터베이스에 새로운 사용자 정보를 추가함
    db.commit()  # 변경 사항을 데이터베이스에 커밋함
    db.refresh(new_user)  # 데이터베이스에서 새로운 사용자 정보를 리프레시함
    return {"message": "User registered successfully"}  # 성공 메시지를 반환함

# 로그인 엔드포인트
@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    사용자 로그인을 처리하는 엔드포인트.
    입력된 이메일 주소와 비밀번호를 사용하여 사용자를 인증하고, 액세스 토큰을 반환함.

    Parameters:
    - user (UserLogin): 로그인을 위한 사용자 정보를 담은 Pydantic 모델
    - db (Session): SQLAlchemy 세션 객체

    Returns:
    - Token: 생성된 액세스 토큰과 토큰 타입을 담은 Pydantic 모델

    Raises:
    - HTTPException: 잘못된 이메일 주소 또는 비밀번호로 인해 인증에 실패했을 경우 401 예외를 발생시킴
    """
    db_user = authenticate_user(db, user.email, user.password)  # 사용자 인증을 수행함
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )  # 인증에 실패하면 HTTP 401 예외를 발생시킴
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 액세스 토큰의 만료 시간 설정
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )  # JWT를 사용하여 액세스 토큰을 생성함
    return {"access_token": access_token, "token_type": "bearer"}  # 생성된 액세스 토큰과 토큰 타입을 반환함

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 현재 사용자 가져오기 함수
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    현재 로그인된 사용자를 가져오는 함수.
    HTTP Bearer 토큰을 사용하여 사용자를 인증하고, 해당 사용자 정보를 반환함.

    Parameters:
    - db (Session): SQLAlchemy 세션 객체
    - token (str): HTTP Bearer 토큰

    Returns:
    - User: 현재 로그인된 사용자 정보를 담은 SQLAlchemy 모델

    Raises:
    - HTTPException: 사용자 인증에 실패했을 경우 401 예외를 발생시킴
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )  # 인증 실패 시 반환될 HTTP 401 예외 객체 생성

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # JWT 디코딩을 통해 페이로드 추출
        email: str = payload.get("sub")  # JWT 페이로드에서 서브젝트(sub) 정보 추출
        if email is None:
            raise credentials_exception  # 서브젝트 정보가 없으면 인증 실패 예외를 발생시킴
        token_data = TokenData(email=email)  # 추출한 이메일 정보로 TokenData 객체 생성
    except JWTError:
        raise credentials_exception  # JWT 디코딩 중 오류가 발생하면 인증 실패 예외를 발생시킴

    user = db.query(User).filter(User.email == token_data.email).first()  # 데이터베이스에서 이메일로 사용자 조회
    if user is None:
        raise credentials_exception  # 조회된 사용자가 없으면 인증 실패 예외를 발생시킴

    return user  # 인증된 사용자 정보를 반환함

# 보호된 엔드포인트
@app.get("/users/me", response_model=UserBase)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    로그인된 사용자의 정보를 가져오는 보호된 엔드포인트.
    현재 로그인된 사용자의 정보를 반환함.

    Parameters:
    - current_user (User): 현재 로그인된 사용자 정보를 담은 SQLAlchemy 모델

    Returns:
    - UserBase: 현재 로그인된 사용자의 기본 정보를 담은 Pydantic 모델
    """
    return current_user  # 현재 로그인된 사용자의 정보를 반환함

@app.post("/posts/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    새로운 게시글을 작성하는 엔드포인트.

    Parameters:
    - post (PostCreate): 게시글 생성을 위한 데이터를 담은 Pydantic 모델
    - db (Session): SQLAlchemy 세션 객체
    - current_user (User): 현재 로그인된 사용자 정보를 담은 SQLAlchemy 모델

    Returns:
    - PostResponse: 생성된 게시글의 정보를 담은 Pydantic 모델
    """
    db_post = Post(**post.dict(), author_id=current_user.id)  # 게시글 데이터를 사용하여 새로운 Post 객체 생성
    db.add(db_post)  # 데이터베이스에 새로운 게시글 추가
    db.commit()  # 변경 사항을 데이터베이스에 커밋
    db.refresh(db_post)  # 데이터베이스에서 새로운 게시글 정보를 리프레시
    return db_post  # 생성된 게시글의 정보를 반환

@app.get("/posts/", response_model=list[PostResponse])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    게시글 목록을 조회하는 엔드포인트.

    Parameters:
    - skip (int): 조회할 게시글의 시작 위치 (기본값: 0)
    - limit (int): 조회할 게시글의 최대 개수 (기본값: 10)
    - db (Session): SQLAlchemy 세션 객체

    Returns:
    - list[PostResponse]: 조회된 게시글 목록을 담은 Pydantic 모델 리스트
    """
    posts = db.query(Post).offset(skip).limit(limit).all()  # 데이터베이스에서 게시글 조회
    return posts  # 조회된 게시글 목록을 반환

@app.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """
    특정 게시글을 조회하는 엔드포인트.

    Parameters:
    - post_id (int): 조회할 게시글의 ID
    - db (Session): SQLAlchemy 세션 객체

    Returns:
    - PostResponse: 조회된 게시글의 정보를 담은 Pydantic 모델

    Raises:
    - HTTPException: 게시글을 찾을 수 없을 경우 404 예외를 발생시킴
    """
    post = db.query(Post).filter(Post.id == post_id).first()  # 게시글 ID로 게시글 조회
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")  # 게시글을 찾을 수 없을 경우 404 예외 발생
    return post  # 조회된 게시글의 정보를 반환

@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    특정 게시글을 수정하는 엔드포인트.

    Parameters:
    - post_id (int): 수정할 게시글의 ID
    - post (PostCreate): 수정할 게시글 데이터를 담은 Pydantic 모델
    - db (Session): SQLAlchemy 세션 객체
    - current_user (User): 현재 로그인된 사용자 정보를 담은 SQLAlchemy 모델

    Returns:
    - PostResponse: 수정된 게시글의 정보를 담은 Pydantic 모델

    Raises:
    - HTTPException: 게시글을 찾을 수 없거나 수정 권한이 없을 경우 404 또는 403 예외를 발생시킴
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()  # 게시글 ID로 게시글 조회
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")  # 게시글을 찾을 수 없을 경우 404 예외 발생
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")  # 수정 권한이 없을 경우 403 예외 발생
    for key, value in post.dict().items():
        setattr(db_post, key, value)  # 게시글 데이터를 업데이트
    db.commit()  # 변경 사항을 데이터베이스에 커밋
    db.refresh(db_post)  # 데이터베이스에서 수정된 게시글 정보를 리프레시
    return db_post  # 수정된 게시글의 정보를 반환

@app.delete("/posts/{post_id}", response_model=dict)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    특정 게시글을 삭제하는 엔드포인트.

    Parameters:
    - post_id (int): 삭제할 게시글의 ID
    - db (Session): SQLAlchemy 세션 객체
    - current_user (User): 현재 로그인된 사용자 정보를 담은 SQLAlchemy 모델

    Returns:
    - dict: 삭제된 게시글에 대한 성공 메시지

    Raises:
    - HTTPException: 게시글을 찾을 수 없거나 삭제 권한이 없을 경우 404 또는 403 예외를 발생시킴
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()  # 게시글 ID로 게시글 조회
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")  # 게시글을 찾을 수 없을 경우 404 예외 발생
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")  # 삭제 권한이 없을 경우 403 예외 발생
    db.delete(db_post)  # 게시글을 데이터베이스에서 삭제
    db.commit()  # 변경 사항을 데이터베이스에 커밋
    return {"message": "Post deleted successfully"}  # 삭제된 게시글에 대한 성공 메시지 반환

@app.get("/")
async def root():
    """
    루트 경로에 대한 간단한 테스트용 메시지 반환 엔드포인트.
    """
    return {"message": "I love you"}
