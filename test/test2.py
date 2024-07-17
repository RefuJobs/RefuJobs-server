import requests

BASE_URL = "http://172.16.7.192:8000"  # FastAPI 서버의 주소

def read_post(post_id: int):
    url = f"{BASE_URL}/posts/{post_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        return response.json()  # 조회된 게시글 정보를 JSON 형식으로 반환
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")

    return None

# 특정 게시글 ID로 조회 테스트
post_id_to_read = 2  # 조회할 게시글의 ID 입력

post_info = read_post(post_id_to_read)

if post_info:
    print(f"Post found:\n{post_info}")
else:
    print(f"Post not found or failed to retrieve.")
