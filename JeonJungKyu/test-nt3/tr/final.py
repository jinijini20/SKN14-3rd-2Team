import streamlit as st
import sys
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import re
from typing import List, Dict

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# RAG 시스템 import
from utils1.main import run_flexible_rag

# 환경변수 로드
load_dotenv()
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 뉴스 카테고리별 색상
CATEGORY_COLORS = {
    "경제": "#4CAF50",
    "기술": "#2196F3",
    "정치": "#FF9800",
    "사회": "#9C27B0",
    "문화": "#E91E63",
    "스포츠": "#FF5722",
    "기본": "#607D8B"
}

# Page configuration
st.set_page_config(
    page_title="재무 데이터 RAG 챗봇",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 통합 CSS (기존 + 뉴스 패널 스타일)
st.markdown("""
<style>
    /* 전체 레이아웃 */
    .main {
        height: 100vh;
        overflow: hidden;
        background-color: #f8f9fa;
    }
    .stApp {
        height: 100vh;
        overflow: hidden;
    }
    .block-container {
        height: 100vh;
        overflow: hidden;
        padding: 0;
        max-width: none;
    }

    /* 사이드바 스타일 */
    .sidebar {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
        padding: 1rem;
        height: 100vh;
        overflow-y: auto;
    }

    /* 메인 컨텐츠 영역 */
    .main-content {
        background-color: white;
        height: 100vh;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
    }

    /* 상단 바 */
    .top-bar {
        padding: 1rem 2rem;
        border-bottom: 1px solid #e9ecef;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: white;
    }

    /* 채팅 컨테이너 */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 2rem;
        background-color: white;
        max-height: calc(100vh - 200px);
    }

    /* 메시지 스타일 */
    .message {
        margin-bottom: 1rem;
        border-radius: 18px;
        max-width: 70%;
        word-wrap: break-word;
        position: relative;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .message.user {
        background: #007AFF;
        color: white;
        margin-left: auto;
        text-align: left;
        border-bottom-right-radius: 4px;
    }
    .message.assistant {
        background: #f1f3f4;
        color: #000;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }
    .message-time {
        font-size: 0.7rem;
        opacity: 0.6;
        margin-top: 0.25rem;
    }

    /* 대화 아이템 */
    .conversation-item {
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        background-color: transparent;
        cursor: pointer;
        transition: background-color 0.2s;
        border: none;
        text-align: left;
        width: 100%;
    }
    .conversation-item:hover {
        background-color: #e9ecef;
    }
    .conversation-item.active {
        background-color: #e8f0fe;
        color: #1a73e8;
    }

    /* 버튼 스타일 */
    .gemini-button {
        background-color: transparent;
        border: 1px solid #dadce0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #5f6368;
        cursor: pointer;
        transition: all 0.2s;
        width: 100%;
        text-align: left;
        margin-bottom: 0.5rem;
    }
    .gemini-button:hover {
        background-color: #f8f9fa;
        border-color: #dadce0;
    }

    /* 입력 필드 */
    .chat-input {
        border: 1px solid #dadce0;
        border-radius: 24px;
        padding: 0.75rem 1rem;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* 웰컴 메시지 */
    .welcome-message {
        text-align: center;
        color: #5f6368;
        font-size: 1.1rem;
        margin-top: 2rem;
    }

    /* 뉴스 패널 스타일 */
    .news-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #2196F3;
        transition: transform 0.2s ease;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    .news-title {
        font-size: 14px;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .news-description {
        color: #666;
        font-size: 12px;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    .news-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        color: #999;
        margin-bottom: 10px;
    }
    .category-badge {
        background: #f0f0f0;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 500;
    }
    .search-section {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .news-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: center;
    }
    .no-news {
        text-align: center;
        color: #999;
        font-style: italic;
        padding: 40px 20px;
    }
</style>
""", unsafe_allow_html=True)


# 뉴스 관련 함수들
def get_naver_news(query, display=10):
    url = 'https://openapi.naver.com/v1/search/news.json'
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        'query': query,
        'display': display,
        'start': 1,
        'sort': 'date'
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"API 호출 중 오류 발생: {e}")
        return None


def guess_category(title: str, description: str) -> str:
    text = (title + " " + description).lower()

    if any(word in text for word in ["경제", "금융", "투자", "기업"]):
        return "경제"
    elif any(word in text for word in ["기술", "ai", "인공지능", "반도체", "it", "테크"]):
        return "기술"
    elif any(word in text for word in ["정치", "정부", "대통령", "국회", "선거"]):
        return "정치"
    elif any(word in text for word in ["사회", "사건", "사고", "범죄"]):
        return "사회"
    elif any(word in text for word in ["문화", "예술", "영화", "음악", "연예"]):
        return "문화"
    elif any(word in text for word in ["스포츠", "축구", "야구", "농구", "올림픽"]):
        return "스포츠"
    else:
        return "기본"


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def time_ago(pub_date: str) -> str:
    try:
        date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
        now = datetime.now(date_obj.tzinfo)
        diff = now - date_obj

        if diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}시간 전"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}분 전"
        else:
            return "방금 전"
    except:
        return pub_date


# RAG 응답 생성 함수 (스트림 방식)
def generate_response_stream(user_input: str):
    """
    RAG 시스템을 사용하여 사용자 입력에 대한 응답을 스트림으로 생성합니다.
    """
    try:
        # RAG 시스템 호출 (스트림 방식으로 가정)
        # run_flexible_rag가 generator를 반환한다고 가정
        for chunk in run_flexible_rag(user_input):
            yield chunk
    except Exception as e:
        # RAG 시스템 오류 시 fallback 응답
        st.error(f"RAG 시스템 오류: {str(e)}")
        fallback_response = generate_fallback_response(user_input)
        # fallback 응답을 스트림처럼 처리
        for word in fallback_response.split():
            yield word + " "
            import time
            time.sleep(0.05)  # 시각적 효과를 위한 딜레이


def generate_fallback_response(user_input: str) -> str:
    """
    RAG 시스템 오류 시 사용할 fallback 응답을 생성합니다.
    """
    user_input_lower = user_input.lower()

    if "재무" in user_input_lower or "매출" in user_input_lower or "실적" in user_input_lower:
        return "죄송합니다. 현재 RAG 시스템에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
    elif "안녕" in user_input_lower or "hello" in user_input_lower:
        return "안녕하세요! 재무 데이터에 대해 궁금한 점이 있으시면 언제든지 물어보세요."
    else:
        return "죄송합니다. 현재 시스템에 문제가 발생하여 정확한 답변을 드릴 수 없습니다. 잠시 후 다시 시도해주세요."


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "search_query" not in st.session_state:
    st.session_state.search_query = "경제"


# 대화 관리 함수들
def generate_conversation_id():
    return f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def create_new_conversation():
    conv_id = generate_conversation_id()
    st.session_state.conversations[conv_id] = {
        "id": conv_id,
        "title": f"대화 {len(st.session_state.conversations) + 1}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": []
    }
    st.session_state.current_conversation_id = conv_id
    st.session_state.messages = []
    return conv_id


def save_conversation(conv_id):
    if conv_id and conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["messages"] = st.session_state.messages.copy()
        st.session_state.conversations[conv_id]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_conversation(conv_id):
    if conv_id in st.session_state.conversations:
        st.session_state.current_conversation_id = conv_id
        st.session_state.messages = st.session_state.conversations[conv_id]["messages"].copy()


# 사이드바 (대화 관리)
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0;">
        <h3 style="margin-bottom: 1rem; color: #5f6368;">재무 데이터 RAG</h3>
    </div>
    """, unsafe_allow_html=True)

    # 새 대화 생성 버튼
    if st.button("✏️ 새 채팅", use_container_width=True, key="new_chat"):
        create_new_conversation()
        st.rerun()

    st.markdown("---")

    # 저장된 대화 목록
    st.markdown("**최근**")

    if st.session_state.conversations:
        for conv_id, conv_data in st.session_state.conversations.items():
            is_active = conv_id == st.session_state.current_conversation_id

            if st.button(f"💬 {conv_data['title']}", key=f"conv_{conv_id}", help="대화 로드"):
                load_conversation(conv_id)
                st.rerun()
    else:
        st.markdown("저장된 대화가 없습니다.", help="새 대화를 시작해보세요")

    st.markdown("---")

    # 하단 정보
    st.markdown("""
    <div style="position: fixed; bottom: 1rem; left: 1rem; font-size: 0.8rem; color: #5f6368;">
        <div>대한민국 서울특별시</div>
        <div style="color: #1a73e8;">IP 주소 기반 • 위치 업데이트</div>
    </div>
    """, unsafe_allow_html=True)

# 메인 레이아웃 (채팅 + 뉴스)
col_chat, col_news = st.columns([70, 30])

# 왼쪽: 채팅 영역
with col_chat:
    # 상단 바
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown("### 재무 데이터 RAG 챗봇")
    with col2:
        st.markdown("")
    with col3:
        if st.button("업그레이드", key="upgrade"):
            st.info("업그레이드 기능 준비 중")

    st.markdown("---")

    # 채팅 메시지 표시
    with st.container(height=500):
        if not st.session_state.messages:
            # 웰컴 메시지
            st.markdown("""
            <div class="welcome-message">
                안녕하세요! RAG 시스템을 통해 재무 데이터에 대해 질문해보세요.<br>
                <small style="color: #888;">예: "삼성전자 2023년 재무제표 알려줘"</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 채팅 메시지 표시
            for msg in st.session_state.messages:
                role_class = "user" if msg["role"] == "user" else "assistant"
                time_str = datetime.now().strftime("%H:%M")

                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 10px; align-items: flex-end;">
                        <div class="message-time" style="color: #888888; font-size: 0.75rem; margin-right: 8px; margin-bottom: 5px;">{time_str}</div>
                        <div class="message {role_class}" style="max-width: 80%;">
                            <div style="background: #007AFF; padding: 10px 15px; border-radius: 30px; display: inline-block; color: white;">{msg["content"]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-start; margin-bottom: 10px; align-items: flex-end;">
                        <div class="message {role_class}" style="max-width: 80%;">
                            <div style="background: #f1f3f4; padding: 10px 15px; border-radius: 30px; display: inline-block; color: #000;">{msg["content"]}</div>
                        </div>
                        <div class="message-time" style="color: #888888; font-size: 0.75rem; margin-left: 8px; margin-bottom: 5px;">{time_str}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # 입력 영역
    user_input = st.chat_input("재무 데이터 RAG에게 물어보기")

    if user_input:
        # 새 대화가 없으면 자동 생성
        if not st.session_state.current_conversation_id:
            create_new_conversation()

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate response using RAG system (streaming)
        with st.spinner("RAG 시스템에서 답변을 생성하는 중..."):
            try:
                # 스트림 응답을 받기 위한 placeholder
                response_placeholder = st.empty()
                full_response = ""

                # 스트림 방식으로 응답 생성
                for chunk in generate_response_stream(user_input):
                    full_response += chunk
                    # 실시간으로 응답 업데이트
                    response_placeholder.markdown(f"""
                    <div style="display: flex; justify-content: flex-start; margin-bottom: 10px; align-items: flex-end;">
                        <div class="message assistant" style="max-width: 80%;">
                            <div style="background: #f1f3f4; padding: 10px 15px; border-radius: 30px; display: inline-block; color: #000;">{full_response}</div>
                        </div>
                        <div class="message-time" style="color: #888888; font-size: 0.75rem; margin-left: 8px; margin-bottom: 5px;">{datetime.now().strftime('%H:%M')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # 스트림 완료 후 placeholder 제거
                response_placeholder.empty()
                bot_reply = full_response

            except Exception as e:
                bot_reply = f"죄송합니다. RAG 시스템에서 오류가 발생했습니다: {str(e)}"
                st.error("RAG 시스템 연결에 문제가 있습니다. 시스템 관리자에게 문의하세요.")

        # Add bot reply to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        # 자동 저장
        if st.session_state.current_conversation_id:
            save_conversation(st.session_state.current_conversation_id)

        st.rerun()

# 오른쪽: 뉴스 패널
with col_news:
    st.markdown("""
    <div class="news-header">
        <h2 style="margin: 0; font-size: 20px;">📰 실시간 뉴스</h2>
        <p style="margin: 0px 0 0 0; font-size: 14px; opacity: 0.9;"></p>
    </div>
    """, unsafe_allow_html=True)

    # 검색 섹션
    with st.container():
        st.markdown('<div class="search-section">', unsafe_allow_html=True)

        # 검색 입력
        search_query = st.text_input(
            "검색 키워드",
            value=st.session_state.search_query,
            placeholder="키워드를 입력하세요...",
            label_visibility="collapsed"
        )

        if st.button("🔄 새로고침", key="refresh_btn", use_container_width=True):
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # 뉴스 표시
    if NAVER_CLIENT_ID and NAVER_CLIENT_SECRET:
        with st.container(height=600):
            with st.spinner("뉴스를 불러오는 중..."):
                news_data = get_naver_news(search_query)

                if news_data and news_data.get('items'):
                    # 뉴스 항목 표시
                    for i, item in enumerate(news_data['items']):
                        title = remove_html_tags(item.get('title', ''))
                        description = remove_html_tags(item.get('description', ''))
                        pub_date = item.get('pubDate', '')
                        link = item.get('link', '')

                        # 카테고리 추측
                        category = guess_category(title, description)
                        category_color = CATEGORY_COLORS.get(category, CATEGORY_COLORS["기본"])

                        # 시간 경과 계산
                        time_diff = time_ago(pub_date)

                        # 뉴스 카드
                        st.markdown(f"""
                        <div class="news-card" style="border-left-color: {category_color};">
                            <div class="news-meta">
                                <span class="category-badge" style="background: {category_color}; color: white;">
                                    {category}
                                </span>
                                <span>{time_diff}</span>
                            </div>
                            <div class="news-title">
                                <a href="{link}" target="_blank" style="text-decoration: none; color: #1f77b4;">
                                    {title}
                                </a>
                            </div>
                            <div class="news-description">
                                {description[:120]}{'...' if len(description) > 120 else ''}
                            </div>
                            <div style="text-align: right;">
                                <a href="{link}" target="_blank" style="font-size: 11px; color: #ff6b6b; text-decoration: none;">
                                    📖 원문 보기
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # 구분선 (마지막 항목 제외)
                        if i < len(news_data['items']) - 1:
                            st.markdown("<hr style='margin: 5px 0; border: none; height: 1px; background: #eee;'>",
                                        unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="no-news">
                        <p>📭 뉴스를 불러올 수 없습니다.</p>
                        <p>검색 키워드를 변경해보세요.</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 네이버 API 키가 설정되지 않았습니다.")
        st.info("`.env` 파일에 다음 내용을 추가하세요:")
        st.code("""
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
        """, language="bash")