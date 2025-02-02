import streamlit as st
from openai import OpenAI
import time
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="GPT-4 테스트", layout="wide")


# OpenAI API 설정
def initialize_openai():
    """OpenAI API 클라이언트 초기화"""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_KEY"])
        return client
    except Exception as e:
        st.error(f"OpenAI API 초기화 오류: {str(e)}")
        return None


# 응답 생성 함수
def generate_gpt4_response(
    client, prompt, system_message="당신은 논리적이고 분석적인 AI 조수입니다."
):
    """GPT-4를 사용하여 응답 생성"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"GPT-4 응답 생성 오류: {str(e)}")
        return None


# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = initialize_openai()

# UI 구성
st.title("🤖 GPT-4 API 테스트")
st.markdown("---")

# API 상태 확인
if st.session_state.client:
    st.success("✅ GPT-4 API 연결됨")
else:
    st.error("❌ GPT-4 API 연결 실패")
    st.stop()

# 입력 영역
user_input = st.text_input("메시지를 입력하세요:", key="input")

if st.button("전송") and user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
    )

    # GPT-4 응답 생성
    response = generate_gpt4_response(st.session_state.client, user_input)

    if response:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
                "time": datetime.now().strftime("%H:%M:%S"),
            }
        )

# 대화 표시
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    align = "right" if is_user else "left"
    color = "#f1c40f" if is_user else "#2ecc71"

    st.markdown(
        f"""
    <div style="margin:10px; text-align:{align};">
        <div style="display:inline-block; 
            padding:8px 15px; 
            border-radius:15px; 
            background-color:{color}20;
            max-width:70%;">
            <strong>{'사용자' if is_user else 'GPT-4'}</strong><br>
            {msg['content']}
            <div style="font-size:0.8em; color:#666;">{msg['time']}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# 대화 초기화 버튼
if st.button("대화 초기화"):
    st.session_state.messages = []
    st.rerun()
