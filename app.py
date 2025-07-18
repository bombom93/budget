import streamlit as st
import pandas as pd

USER_FILE = "users.csv"

# -------------------------------
# 사용자 인증 관련 함수
# -------------------------------
def load_users():
    try:
        return pd.read_csv(USER_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "password"])

def save_user(username, password):
    users = load_users()
    if username in users["username"].values:
        return False
    users = pd.concat([users, pd.DataFrame([{"username": username, "password": password}])], ignore_index=True)
    users.to_csv(USER_FILE, index=False)
    return True

def login_form():
    st.set_page_config(page_title="로그인", page_icon="🔐")
    st.title("🔐 가계부 로그인 / 회원가입")
    tabs = st.tabs(["로그인", "회원가입"])

    with tabs[0]:
        username = st.text_input("아이디", key="login_user")
        password = st.text_input("비밀번호", type="password", key="login_pw")
        if st.button("로그인"):
            users = load_users()
            if ((users["username"] == username) & (users["password"] == password)).any():
                st.session_state.auth = True
                st.session_state.username = username
                st.success(f"{username}님, 환영합니다!")
                st.switch_page("가계부 메인")
            else:
                st.error("❌ 아이디 또는 비밀번호가 잘못되었습니다.")

    with tabs[1]:
        new_user = st.text_input("새 아이디", key="new_user")
        new_pw = st.text_input("새 비밀번호", type="password", key="new_pw")
        if st.button("회원가입"):
            if not new_user or not new_pw:
                st.warning("아이디와 비밀번호를 모두 입력하세요.")
            elif save_user(new_user, new_pw):
                st.success("✅ 회원가입 성공! 로그인 해주세요.")
            else:
                st.error("❌ 이미 존재하는 아이디입니다.")

# -------------------------------
# 로그인 상태 초기화 및 보호
# -------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------------------
# 로그인 폼 호출
# -------------------------------
login_form()
