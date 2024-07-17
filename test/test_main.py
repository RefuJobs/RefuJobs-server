import requests

BASE_URL = "http://192.168.62.13:8000"  # FastAPI 서버의 주소 (로컬 환경에서는 포트 번호에 주의하세요)

def login_user(email, password):
    url = f"{BASE_URL}/login"
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, json=data)
    return response

def create_post(access_token, title, company_name, hashtags, job_type, career, content):
    url = f"{BASE_URL}/posts/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "company_name": company_name,
        "hashtags": hashtags,  # 해시태그는 문자열로 전달
        "job_type": job_type,
        "career": career,
        "content": content
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

def read_posts(access_token):
    url = f"{BASE_URL}/posts/"
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

def delete_post(access_token, post_id):
    url = f"{BASE_URL}/posts/{post_id}"
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

# 로그인
login_response = login_user(
    email="testuser1@example.com",
    password="password1"
)

if login_response.status_code == 200:
    access_token = login_response.json().get("access_token")
    print(f"Login successful! Access Token: {access_token}")
else:
    print(f"Login failed: {login_response.json()}")

# 게시글 작성
# if access_token:
#     create_post_response = create_post(
#         access_token=access_token,
#         title="신입채용공고",
#         company_name="조조컴퍼니",
#         hashtags="#조조, #가족같은분위기",  # 해시태그를 문자열로 전달
#         job_type="문관",
#         career="1번이상의 전쟁참여경험",
#         content="천하통일까지 함께하실 분들 모집"
#     )

#     if create_post_response and create_post_response.status_code == 200:
#         print("Post created successfully!")
#     elif create_post_response:
#         print(f"Failed to create post: {create_post_response.json()}")

# 게시글 삭제
if access_token:
    post_id_to_delete = 1  # 삭제할 게시글의 ID 입력
    delete_post_response = delete_post(access_token, post_id_to_delete)

    if delete_post_response and delete_post_response.status_code == 200:
        print("Post deleted successfully!")
    elif delete_post_response:
        print(f"Failed to delete post: {delete_post_response.json()}")

# # 게시글 조회
# if access_token:
#     read_posts_response = read_posts(access_token)

#     if read_posts_response and read_posts_response.status_code == 200:
#         posts = read_posts_response.json()
#         print("Posts retrieved successfully:")
#         print(posts)
#     elif read_posts_response:
#         print(f"Failed to retrieve posts: {read_posts_response.json()}")
