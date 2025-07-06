import requests

print("--- 카카오 토큰 발급 도우미 ---")

# 1. 사용자 정보 입력받기
REST_API_KEY = input("1. Kakao Developers의 REST API 키를 입력하세요: ").strip()
REDIRECT_URI = input("2. Kakao Developers에 등록한 Redirect URI를 입력하세요 (예: https://localhost): ").strip()

# 2. 인증 코드 받기 위한 URL 생성 및 안내
auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code&scope=talk_message"
print("\n3. 아래 URL을 웹 브라우저에 복사하여 접속하세요.")
print("   로그인 및 동의 후, 리다이렉트된 페이지의 주소창에서 'code=' 뒷부분의 인증 코드를 복사해야 합니다.")
print(f"\n   [인증 URL]: {auth_url}\n")

AUTH_CODE = input("4. 위에서 복사한 인증 코드를 여기에 붙여넣으세요: ").strip()

# 3. 토큰 요청
token_url = "https://kauth.kakao.com/oauth/token"
data = {
    "grant_type": "authorization_code",
    "client_id": REST_API_KEY,
    "redirect_uri": REDIRECT_URI,
    "code": AUTH_CODE,
}

response = requests.post(token_url, data=data)

# 4. 응답 확인 및 토큰 출력
if response.status_code == 200:
    token_info = response.json()
    print("\n✅ 토큰 발급 성공!")
    print(f"   - Access Token: {token_info.get('access_token')}")
    print(f"   - Refresh Token: {token_info.get('refresh_token')}")
    print("\n[중요] 위의 'Refresh Token' 값을 복사하여 GitHub Secrets에 'KAKAO_REFRESH_TOKEN'으로 저장하세요.")
else:
    print(f"\n❌ 토큰 발급 실패 (HTTP {response.status_code})")
    print(f"   에러 응답: {response.text}")