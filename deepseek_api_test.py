import streamlit as st
import requests
import json
from datetime import datetime
import time

# 페이지 설정
st.set_page_config(page_title="DeepSeek API 테스트", page_icon="🧠", layout="wide")


class DeepSeekClient:
    """DeepSeek API와의 통신을 관리하는 클래스"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def generate_response(
        self, prompt, system_message="당신은 기술적이고 실용적인 AI 조수입니다."
    ):
        """
        DeepSeek API를 사용하여 응답을 생성합니다.

        Parameters:
            prompt (str): 사용자 입력 메시지
            system_message (str): AI의 역할 설정

        Returns:
            str: 생성된 응답 또는 None (에러 발생 시)
        """
        try:
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 150,
                "temperature": 0.7,
            }

            response = requests.post(self.api_url, headers=self.headers, json=payload)

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                st.error(f"API 오류: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            st.error(f"응답 생성 중 오류 발생: {str(e)}")
            return None


def initialize_deepseek():
    """DeepSeek API 클라이언트를 초기화합니다."""
    try:
        client = DeepSeekClient(st.secrets["DEEPSEEK_KEY"])
        # API 연결 테스트
        test_response = client.generate_response("테스트")
        return client if test_response else None
    except Exception as e:
        st.error(f"DeepSeek API 초기화 오류: {str(e)}")
        return None


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = initialize_deepseek()

# UI 구성
st.title("🧠 DeepSeek API 테스트")
st.markdown("#### 기술적이고 실용적인 AI 응답을 경험해보세요")
st.markdown("---")

# API 상태 표시
if st.session_state.client:
    st.success("✅ DeepSeek API 연결됨")
else:
    st.error("❌ DeepSeek API 연결 실패")
    st.info(
        """
    **문제 해결 방법:**
    1. API 키가 올바르게 설정되었는지 확인 (.streamlit/secrets.toml 파일)
    2. 네트워크 연결 상태 확인
    3. API 사용량 제한 확인
    """
    )
    st.stop()

# 채팅 인터페이스
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        align = "right" if is_user else "left"
        color = "#f1c40f" if is_user else "#e74c3c"

        st.markdown(
            f"""
        <div style="margin:10px; text-align:{align};">
            <div style="display:inline-block; 
                padding:12px 20px; 
                border-radius:15px; 
                background-color:{color}20;
                max-width:80%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <strong>{'사용자' if is_user else 'DeepSeek'}</strong> 
                {' 👤' if is_user else ' 🧠'}<br>
                {msg['content']}
                <div style="font-size:0.8em; color:#666; margin-top:5px;">
                    {msg['time']}
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

# 입력 인터페이스
with st.container():
    user_input = st.text_input(
        "메시지를 입력하세요:",
        key="input",
        placeholder="기술적인 질문이나 실용적인 문제에 대해 물어보세요...",
    )

    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        send_button = st.button("💬 전송", use_container_width=True)
    with col2:
        clear_button = st.button("🗑 초기화", use_container_width=True)
    with col3:
        if st.button("ℹ️ 도움말", use_container_width=True):
            st.info(
                """
            **DeepSeek 활용 팁:**
            1. 구체적인 기술 문제 해결 요청
            2. 실용적인 구현 방법 문의
            3. 코드 분석 및 최적화 요청
            4. 기술적 개념 설명 요청
            """
            )

# 메시지 처리
if send_button and user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
    )

    # DeepSeek 응답 생성
    with st.spinner("DeepSeek가 기술적 분석을 수행하고 있습니다..."):
        response = st.session_state.client.generate_response(user_input)

        if response:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "time": datetime.now().strftime("%H:%M:%S"),
                }
            )

    st.rerun()

# 대화 초기화
if clear_button:
    st.session_state.messages = []
    st.rerun()

# 스타일링
st.markdown(
    """
<style>
    /* 입력창 스타일링 */
    [data-testid="stTextInput"] input {
        height: 50px;
        font-size: 16px;
        border-radius: 10px;
        padding: 0 15px;
    }
    
    /* 버튼 스타일링 */
    [data-testid="stButton"] button {
        height: 45px;
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    [data-testid="stButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* 메시지 스타일링 */
    .stMarkdown {
        line-height: 1.5;
    }
</style>
""",
    unsafe_allow_html=True,
)
