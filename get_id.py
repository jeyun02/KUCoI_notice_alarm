import requests
import json

# --- 1. 여기에 본인의 정보 입력 ---
REST_API_KEY = "b133753522abe37b3111a446c20a3ec4"  # 카카오 개발자센터에서 확인한 REST API 키 (숫자)
REDIRECT_URI = "http://localhost:8000"  # 카카오 개발자센터에 등록한 Redirect URI
AUTH_CODE = "LM7H2OjwufO5aJRtHwK1dlyjW0SKEDfFFE7vpV3dmuzCm7H7O0Vr9QAAAAQKFyEtAAABl9-ei2vOkqTnJF629A"       # 브라우저 주소창에서 얻은 인증 코드

# --- 2. 토큰 요청 URL 및 헤더/바디 설정 ---
token_url = "https://kauth.kakao.com/oauth/token"
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "grant_type": "authorization_code",
    "client_id": REST_API_KEY,
    "redirect_uri": REDIRECT_URI,
    "code": AUTH_CODE,
}

# --- 3. POST 요청 보내기 ---
response = requests.post(token_url, headers=headers, data=data)

# --- 4. 응답 확인 및 토큰 추출 ---
if response.status_code == 200:
    token_info = response.json()
    print("토큰 발급 성공!")
    print(f"Access Token: {token_info.get('access_token')}")
    print(f"Refresh Token: {token_info.get('refresh_token')}")
    print(f"Expires in (seconds): {token_info.get('expires_in')}")
    print("\n--- 토큰 정보를 안전한 곳에 복사해 두세요! ---")
    print("이 Access Token을 GitHub Actions Secrets에 KAKAO_ACCESS_TOKEN으로 저장합니다.")
else:
    print("토큰 발급 실패!")
    print(f"에러 코드: {response.status_code}")
    print(f"에러 응답: {response.json()}")