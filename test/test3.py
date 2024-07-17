import requests

BASE_URL = "http://172.16.7.191:8000"  # FastAPI 서버의 주소 (로컬 환경에서는 포트 번호에 주의하세요)

def login_user(email, password):
    url = f"{BASE_URL}/login"
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, json=data)
    return response

def create_resume(access_token, title,name, gender, email, phonenumber,education,location,introduce):
    url = f"{BASE_URL}/resumes/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "title":title,
        "name": name,
        "gender":gender,
        "email":email,
        "phonenumber":phonenumber,
        "education":education,
        "location":location,
        "introduce":introduce
        
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
    return None

def read_resumes(access_token):
    url = f"{BASE_URL}/resumes/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
    return None

def delete_resume(access_token, resume_id):
    url = f"{BASE_URL}/resumes/{resume_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
    return None

def update_resume(access_token, resume_id,title,name, gender, email, phonenumber,education,location,introduce):
    url = f"{BASE_URL}/resumes/{resume_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "title":title,
        "name": name,
        "gender":gender,
        "email":email,
        "phonenumber":phonenumber,
        "education":education,
        "location":location,
        "introduce":introduce
    }
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
    return None

# 로그인
login_response = login_user(
    email="testuser2@example.com",
    password="password2"
)

if login_response.status_code == 200:
    access_token = login_response.json().get("access_token")
    print(f"Login successful! Access Token: {access_token}")
else:
    print(f"Login failed: {login_response.json()}")

# 이력서 생성
# if access_token:
#     create_resume_response = create_resume(
#         access_token=access_token,
#         title="더미",
#         name= "더미",
#         gender = "더미",
#         email = "더미",
#         phonenumber = "더미",
#         education = "더미",
#         location = "더미",
#         introduce = "더미"
#     )

#     if create_resume_response and create_resume_response.status_code == 200:
#         print("Resume created successfully!")
#     elif create_resume_response:
#         print(f"Failed to create resume: {create_resume_response.json()}")

# # 이력서 수정
# if access_token:
#     resume_id_to_update = 1  # 수정할 이력서의 ID 입력
#     update_resume_response = update_resume(
#         access_token=access_token,
#         resume_id=resume_id_to_update,
#         title="이력서입니다",
#         name= "김나연",
#         gender = "Fmale",
#         email = "email2@naver.com",
#         phonenumber = "010-2222-2222",
#         education = "초졸",
#         location = "대구",
#         introduce = "시켜만주신다면 열심히 하겠습니다"
#     )

#     if update_resume_response and update_resume_response.status_code == 200:
#         print("Resume updated successfully!")
#     elif update_resume_response:
#         print(f"Failed to update resume: {update_resume_response.json()}")

# # 이력서 삭제
# if access_token:
#     resume_id_to_delete = 3  # 삭제할 이력서의 ID 입력
#     delete_resume_response = delete_resume(access_token, resume_id_to_delete)

#     if delete_resume_response and delete_resume_response.status_code == 200:
#         print("Resume deleted successfully!")
#     elif delete_resume_response:
#         print(f"Failed to delete resume: {delete_resume_response.json()}")

# 이력서 조회
# if access_token:
#     read_resumes_response = read_resumes(access_token)

#     if read_resumes_response and read_resumes_response.status_code == 200:
#         resumes = read_resumes_response.json()
#         print("Resumes retrieved successfully:")
#         print(resumes)
#     elif read_resumes_response:
#         print(f"Failed to retrieve resumes: {read_resumes_response.json()}")
