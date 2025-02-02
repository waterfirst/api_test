import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time

# 페이지 설정
st.set_page_config(page_title="Gemini API 테스트", page_icon="🚀", layout="wide")


def initialize_gemini():
    """
    Gemini API를 초기화하는 함수입니다.
    이 함수는 API 키를 설정하고 초기화 상태를 확인합니다.

    Returns:
        bool: API 초기화 성공 여부
    """
    try:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        # 모델 사용 가능 여부 테스트
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("테스트")
        return True
    except Exception as e:
        st.error(f"Gemini API 초기화 오류: {str(e)}")
        return False


def generate_gemini_response(
    prompt, context="당신은 창의적이고 혁신적인 AI 조수입니다."
):
    """
    Gemini API를 사용하여 응답을 생성합니다.

    Parameters:
        prompt (str): 사용자의 입력 메시지
        context (str): AI의 역할과 특성을 정의하는 컨텍스트

    Returns:
        str: 생성된 응답 또는 에러 메시지
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        full_prompt = f"{context}\n\n사용자 메시지: {prompt}\n\n당신의 응답:"

        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7, max_output_tokens=150, top_p=0.8, top_k=40
            ),
        )
        return response.text
    except Exception as e:
        st.error(f"응답 생성 중 오류 발생: {str(e)}")
        return None


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_initialized" not in st.session_state:
    st.session_state.api_initialized = initialize_gemini()

# UI 구성
st.title("🚀 Gemini API 테스트")
st.markdown("#### Google의 최신 AI 모델을 테스트해보세요")
st.markdown("---")

# API 상태 표시
if st.session_state.api_initialized:
    st.success("✅ Gemini API 연결 성공")
else:
    st.error("❌ Gemini API 연결 실패")
    st.info("API 키를 확인해주세요. (.streamlit/secrets.toml 파일의 GEMINI_KEY)")
    st.stop()

# 대화 인터페이스
chat_container = st.container()
with chat_container:
    # 이전 대화 표시
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        align = "right" if is_user else "left"
        color = "#f1c40f" if is_user else "#4285f4"

        st.markdown(
            f"""
        <div style="margin:10px; text-align:{align};">
            <div style="display:inline-block; 
                padding:12px 20px; 
                border-radius:15px; 
                background-color:{color}20;
                max-width:80%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <strong>{'사용자' if is_user else 'Gemini'}</strong> 
                {' 👤' if is_user else ' 🚀'}<br>
                {msg['content']}
                <div style="font-size:0.8em; color:#666; margin-top:5px;">
                    {msg['time']}
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

# 입력 영역
with st.container():
    user_input = st.text_input(
        "메시지를 입력하세요:",
        key="input",
        placeholder="창의적인 아이디어나 혁신적인 해결방안을 요청해보세요...",
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
            **Gemini 활용 팁:**
            1. 창의적인 아이디어 제안 요청
            2. 혁신적인 문제 해결 방안 탐색
            3. 다양한 관점에서의 분석 요청
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

    # Gemini 응답 생성
    with st.spinner("Gemini가 창의적인 응답을 생성하고 있습니다..."):
        response = generate_gemini_response(user_input)

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
    
    /* 메시지 영역 스타일링 */
    .stMarkdown {
        line-height: 1.5;
    }
</style>
""",
    unsafe_allow_html=True,
)
