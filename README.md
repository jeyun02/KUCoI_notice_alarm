# KUCoI_notice_alarm

고려대학교 정보대학 공지사항을 크롤링하여 새로운 공지사항이 있을 경우 카카오톡으로 알림을 보내는 프로젝트입니다. GitHub Actions를 사용하여 매일 자동으로 실행됩니다.

## 목표

- **자동화**: 매일 정해진 시간에 자동으로 공지사항 웹페이지를 확인합니다.
- **필터링**: 오늘 또는 어제 게시된 새로운 공지사항만 필터링합니다.
- **알림**: 새로운 공지사항의 제목과 링크를 개인 카카오톡으로 전송합니다.

## 주요 기술
- **언어**: Python
- **라이브러리**: `requests`, `beautifulsoup4`
- **자동화**: GitHub Actions
- **알림**: KakaoTalk Message API

## 설정 방법

### 1단계: Kakao Developers 설정 및 인증 코드 발급 (최초 1회)

1.  **애플리케이션 생성**: [Kakao Developers](https://developers.kakao.com/)에서 새 애플리케이션을 생성합니다.
2.  **REST API 키 확인**: `내 애플리케이션 > 앱 설정 > 요약 정보`에서 **REST API 키**를 복사해 둡니다.
3.  **Redirect URI 등록**: `내 애플리케이션 > 제품 설정 > 카카오 로그인`에서 **Redirect URI**를 등록합니다. (예: `https://localhost`)
4.  **동의 항목 설정**: `내 애플리케이션 > 제품 설정 > 카카오 로그인 > 동의항목`에서 **'카카오톡 메시지 전송(나에게 보내기)'** 권한을 '필수 동의'로 설정합니다.
5.  **인증 코드 발급**: 아래 URL의 `{REST_API_KEY}`와 `{REDIRECT_URI}`를 본인의 정보로 채운 뒤, 웹 브라우저 주소창에 입력하여 접속합니다.
    ```
    https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code&scope=talk_message
    ```
    - 카카오 계정으로 로그인하고 '동의하고 계속하기' 버튼을 누르면, 설정한 Redirect URI로 이동하면서 주소창에 `code=` 뒷부분에 인증 코드가 나타납니다. 이 코드를 복사합니다.

### 2단계: Refresh Token 발급 (최초 1회)

- 터미널(명령 프롬프트, PowerShell 등)에서 아래 `curl` 명령어를 실행하여 **access_token**과 **refresh_token**을 발급받습니다.
- `{REST_API_KEY}`, `{REDIRECT_URI}`, `{인증_코드}` 부분을 1단계에서 얻은 값으로 채워주세요.

```bash
curl -v -X POST "https://kauth.kakao.com/oauth/token" \
 -H "Content-Type: application/x-www-form-urlencoded" \
 -d "grant_type=authorization_code" \
 -d "client_id={REST_API_KEY}" \
 -d "redirect_uri={REDIRECT_URI}" \
 -d "code={위에서_발급받은_인증_코드}"
```
- 실행 결과로 받은 JSON 데이터에서 `refresh_token` 값을 복사합니다. 이 토큰은 약 1개월간 유효하며, 만료되기 전에 갱신됩니다.

### 3단계: GitHub Repository Secrets 설정

    - 이 저장소의 `Settings > Secrets and variables > Actions`로 이동합니다.
    - `New repository secret`을 클릭하여 아래의 정보를 저장합니다.
      - `KAKAO_REST_API_KEY`: 1단계에서 확인한 REST API 키
      - `KAKAO_REFRESH_TOKEN`: 2단계에서 발급받은 Refresh Token

### 4단계: GitHub Actions 실행

    - `.github/workflows/daily_notice.yml` 파일에 정의된 스케줄에 따라 워크플로우가 자동으로 실행됩니다.
    - 수동으로 실행하려면 저장소의 `Actions` 탭에서 워크플로우를 선택하고 `Run workflow`를 클릭합니다.

## 로컬에서 실행하기

1.  저장소를 클론하고 해당 디렉토리로 이동합니다.
    ```bash
    git clone https://github.com/{your-username}/KUCoI_notice_alarm.git
    cd KUCoI_notice_alarm
    ```

2.  가상 환경을 생성하고 활성화합니다.
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  필요한 라이브러리를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

4.  스크립트를 실행합니다.
    ```bash
    python main.py
    ```