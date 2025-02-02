import streamlit as st
from anthropic import Anthropic
import time
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="Claude API 테스트", page_icon="🎩", layout="wide")


def initialize_claude():
    """
    Claude API 클라이언트를 초기화합니다.
    API 키는 .streamlit/secrets.toml 파일에서 관리됩니다.
    """
    try:
        client = Anthropic(api_key=st.secrets["ANTHROPIC_KEY"])
        return client
    except Exception as e:
        st.error(f"Claude API 초기화 오류: {str(e)}")
        return None


def generate_claude_response(
    client, prompt, system_message="당신은 철학적이고 분석적인 AI 조수입니다."
):
    """
    Claude API를 사용하여 응답을 생성합니다.

    Parameters:
    - client: Anthropic API 클라이언트
    - prompt: 사용자 입력 메시지
    - system_message: AI의 페르소나를 설정하는 시스템 메시지
    """
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=150,
            temperature=0.7,
            messages=[{"role": "user", "content": f"{system_message}\n\n{prompt}"}],
        )
        return response.content[0].text
    except Exception as e:
        st.error(f"Claude 응답 생성 오류: {str(e)}")
        return None


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = initialize_claude()

# UI 구성
st.title("🎩 Claude API 테스트")
st.markdown("---")

# API 연결 상태 표시
if st.session_state.client:
    st.success("✅ Claude API 연결됨")
else:
    st.error("❌ Claude API 연결 실패")
    st.info("API 키를 확인해주세요. (.streamlit/secrets.toml 파일)")
    st.stop()

# 입력 영역
with st.container():
    user_input = st.text_input(
        "메시지를 입력하세요:",
        key="input",
        placeholder="질문이나 대화 주제를 입력해주세요...",
    )

    col1, col2 = st.columns([4, 1])
    with col1:
        send_button = st.button("💬 전송", use_container_width=True)
    with col2:
        clear_button = st.button("🗑 초기화", use_container_width=True)

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

    # Claude 응답 생성
    with st.spinner("Claude가 응답을 생성하고 있습니다..."):
        response = generate_claude_response(st.session_state.client, user_input)

        if response:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "time": datetime.now().strftime("%H:%M:%S"),
                }
            )

# 대화 초기화
if clear_button:
    st.session_state.messages = []
    st.rerun()

# 대화 내용 표시
st.markdown("### 💭 대화 내용")
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    align = "right" if is_user else "left"
    color = "#f1c40f" if is_user else "#9b59b6"

    st.markdown(
        f"""
    <div style="margin:10px; text-align:{align};">
        <div style="display:inline-block; 
            padding:12px 20px; 
            border-radius:15px; 
            background-color:{color}20;
            max-width:80%;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
            <strong>{'사용자' if is_user else 'Claude'}</strong> 
            {' 👤' if is_user else ' 🎩'}<br>
            {msg['content']}
            <div style="font-size:0.8em; color:#666; margin-top:5px;">
                {msg['time']}
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# 추가 스타일링
st.markdown(
    """
<style>
    /* 입력창 스타일링 */
    [data-testid="stTextInput"] input {
        height: 50px;
        font-size: 16px;
        border-radius: 10px;
    }
    
    /* 버튼 스타일링 */
    [data-testid="stButton"] button {
        height: 45px;
        border-radius: 10px;
        font-weight: 500;
    }
    
    /* 메시지 컨테이너 스타일링 */
    .stMarkdown {
        line-height: 1.5;
    }
</style>
""",
    unsafe_allow_html=True,
)
