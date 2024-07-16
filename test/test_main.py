#test_main.py
import pytest
import sys, os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from models import Base, User, get_db as get_testing_db
from main import app, get_db

# 테스트용 데이터베이스 연결 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 초기화 및 세션 설정
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 회원가입 및 로그인 테스트
def test_register_and_login():
    # 회원가입 테스트
    register_data = {
        "email": "testuser@gmail.com",
        "password": "testpassword",
        "name": "Test User",
        "gender": "Male",
        "country": "Testland",
        "birthdate": "2000-01-01"
    }
    response = client.post("/register", json=register_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    # 로그인 테스트
    login_data = {
        "email": "testuser@gmail.com",
        "password": "testpassword"
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

# 현재 사용자 정보 조회 테스트
def test_read_users_me():
    login_data = {
        "email": "testuser@gmail.com",
        "password": "testpassword"
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "testuser@gamil.com"
    assert user_data["name"] == "Test User"
    assert user_data["gender"] == "Male"
    assert user_data["country"] == "Testland"
    assert user_data["birthdate"] == "2000-01-01"
