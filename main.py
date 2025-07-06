import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin

# --- 설정 ---
# 크롤링할 카테고리 및 URL
CATEGORIES = {
    "공지사항 - 학부": "https://info.korea.ac.kr/info/board/notice_under.do",
    "공지사항 - 대학원": "https://info.korea.ac.kr/info/board/notice_grad.do",
    "장학공지 - 학부": "https://info.korea.ac.kr/info/board/scholarship_under.do",
    "장학공지 - 대학원": "https://info.korea.ac.kr/info/board/scholarship_grad.do",
    "행사 및 소식": "https://info.korea.ac.kr/info/board/news.do",
    "진로정보 - 채용": "https://info.korea.ac.kr/info/board/course_job.do",
    "진로정보 - 교육": "https://info.korea.ac.kr/info/board/course_program.do",
    "진로정보 - 인턴": "https://info.korea.ac.kr/info/board/course_intern.do",
    "진로정보 - 공모전": "https://info.korea.ac.kr/info/board/course_competition.do",
}

# 카카오 API 정보
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_TALK_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

def get_all_new_notices():
    """
    정의된 모든 카테고리의 공지사항 페이지를 크롤링하여
    오늘 또는 어제 올라온 공지사항의 제목과 링크를 반환합니다.
    """
    # 어제 날짜를 'YYYY.MM.DD' 형식으로 준비
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y.%m.%d')
    
    all_new_notices = []
    
    for category, url in CATEGORIES.items():
        print(f"[{category}] 페이지 확인 중...")
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"  - 웹 페이지를 가져오는 중 오류 발생: {e}")
            continue # 다음 카테고리로 넘어감

        soup = BeautifulSoup(response.text, 'html.parser')
        # 제공된 HTML 구조에 맞는 선택자로 변경
        notice_table = soup.select_one('div.t_list > table.w')
        if not notice_table:
            print(f"  - 공지사항 테이블을 찾을 수 없습니다.")
            continue
        
        for row in notice_table.select('tbody > tr'):
            columns = row.select('td')
            # 일반 공지사항 행은 보통 5개의 컬럼(번호, 제목, 작성자, 조회수, 등록일)을 가짐
            if len(columns) < 5:
                continue

            title_td = row.select_one('td.txt_left')
            date_td = columns[-1] # 마지막 td가 등록일
            
            if not title_td or not date_td:
                continue
                
            post_date = date_td.get_text(strip=True)
            
            if post_date == yesterday: # 어제 날짜와 일치하는 경우만
                link_tag = title_td.find('a')
                if link_tag and 'href' in link_tag.attrs:
                    title = link_tag.get_text(strip=True)
                    link = urljoin(url, link_tag['href']) # 기준 URL을 현재 카테고리 URL로 사용

                    all_new_notices.append({'category': category, 'title': title, 'link': link})
                    
    return all_new_notices

def refresh_kakao_token(rest_api_key, refresh_token):
    """
    Refresh Token을 사용하여 새로운 Access Token을 발급받습니다.
    """
    payload = {
        'grant_type': 'refresh_token',
        'client_id': rest_api_key,
        'refresh_token': refresh_token,
    }
    try:
        response = requests.post(KAKAO_TOKEN_URL, data=payload)
        response.raise_for_status()
        token_info = response.json()
        
        if 'access_token' not in token_info:
            print(f"❌ 카카오 토큰 갱신 실패: 응답에 access_token이 없습니다. {token_info}")
            return None
            
        print("✅ 카카오 Access Token 갱신 성공")
        return token_info['access_token']
    except requests.exceptions.RequestException as e:
        print(f"❌ 카카오 토큰 갱신 API 요청 중 오류 발생: {e}")
        if e.response:
            print(f"    응답 내용: {e.response.text}")
        return None

def _send_kakao_request(template_object, access_token):
    """카카오톡 메시지 전송 API를 호출하는 내부 헬퍼 함수"""
    if not access_token:
        print("Access Token이 없어 카카오톡 메시지를 보낼 수 없습니다.")
        return False

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {'template_object': json.dumps(template_object)}

    try:
        response = requests.post(KAKAO_TALK_URL, headers=headers, data=payload)
        response.raise_for_status()
        result = response.json()
        if result.get('result_code') == 0:
            return True
        else:
            print(f"❌ 카카오톡 메시지 전송 실패: {result}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 카카오톡 API 요청 중 오류 발생: {e}")
        return False

def send_notice_message(notice, access_token):
    """
    주어진 공지사항 정보를 카카오톡 '나에게 보내기'를 통해 전송합니다.
    """
    template_object = {
        "object_type": "text",
        "text": f"📢 새로운 [{notice['category']}] 알림\n\n- 제목: {notice['title']}",
        "link": { "web_url": notice['link'], "mobile_web_url": notice['link'] },
        "button_title": "공지사항 바로가기"
    }
    if _send_kakao_request(template_object, access_token):
        print(f"✅ 카카오톡 메시지 전송 성공: \"{notice['title']}\"")

def send_status_message(text, access_token):
    """스크립트 실행 상태(결과)를 카카오톡으로 전송합니다."""
    template_object = {
        "object_type": "text",
        "text": text,
        "link": {"web_url": "https://info.korea.ac.kr/info/board/notice_under.do"},
        "button_title": "정보대학 바로가기"
    }
    if _send_kakao_request(template_object, access_token):
        print(f"✅ 카카오톡 상태 메시지 전송 성공.")

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 공지사항 확인 시작...")
    
    # GitHub Secrets에서 환경 변수 읽기
    kakao_rest_api_key = os.getenv('KAKAO_REST_API_KEY')
    kakao_refresh_token = os.getenv('KAKAO_REFRESH_TOKEN')

    if not kakao_rest_api_key or not kakao_refresh_token:
        print("환경 변수 KAKAO_REST_API_KEY 또는 KAKAO_REFRESH_TOKEN이 설정되지 않았습니다.")
        print("스크립트를 종료합니다.")
        return

    # 1. 토큰 갱신
    new_access_token = refresh_kakao_token(kakao_rest_api_key, kakao_refresh_token)
    
    if not new_access_token:
        print("Access Token을 갱신할 수 없어 스크립트를 종료합니다.")
        return

    # 2. 공지사항 크롤링
    notices = get_all_new_notices()
    
    # 3. 메시지 전송
    if not notices:
        print("결과: 어제자 새로운 공지사항이 없습니다.")
        status_text = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}]\n어제자 신규 공지사항이 없습니다."
        send_status_message(status_text, new_access_token)
    else:
        print(f"결과: {len(notices)}개의 어제자 공지사항을 찾았습니다.")
        for notice in notices:
            send_notice_message(notice, new_access_token)
            
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 공지사항 확인 완료.")

if __name__ == "__main__":
    main()