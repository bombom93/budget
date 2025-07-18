import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="로그인", page_icon="🔐", layout="centered")
st.title("🔐 가계부 로그인/회원가입")

USER_FILE = Path("users.csv")
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# 초기 사용자 데이터 생성
if not USER_FILE.exists() or USER_FILE.stat().st_size == 0:
    df = pd.DataFrame([{"username": "admin", "password": "test123"}])
    df.to_csv(USER_FILE, index=False)

# 탭 선택: 로그인 / 회원가입
selected_tab = st.radio("", ["로그인", "회원가입"], horizontal=True)

# 로그인 폼
if selected_tab == "로그인":
    st.subheader("🔑 로그인")
    username = st.text_input("아이디", key="login_user")
    password = st.text_input("비밀번호", type="password", key="login_pass")

    if st.button("로그인"):
        try:
            users = pd.read_csv(USER_FILE)
            if not all(col in users.columns for col in ["username", "password"]):
                st.error("users.csv 파일에 'username' 또는 'password' 컬럼이 없습니다.")
                st.stop()
        except pd.errors.EmptyDataError:
            st.error("사용자 데이터가 비어있습니다. 회원가입을 먼저 진행해주세요.")
            st.stop()

        if ((users["username"] == username) & (users["password"] == password)).any():
            st.session_state.auth = True
            st.session_state.username = username
            st.success("로그인 성공!")
            st.switch_page("pages/main.py")
        else:
            st.error("아이디 또는 비밀번호가 틀렸습니다.")

# 회원가입 폼
elif selected_tab == "회원가입":
    st.subheader("📝 회원가입")
    new_user = st.text_input("새 아이디", key="new_user")
    new_pass = st.text_input("새 비밀번호", type="password", key="new_pass")

    if st.button("회원가입"):
        if new_user.strip() == "" or new_pass.strip() == "":
            st.warning("모든 항목을 입력해주세요.")
        else:
            try:
                users = pd.read_csv(USER_FILE)
                if not all(col in users.columns for col in ["username", "password"]):
                    users = pd.DataFrame(columns=["username", "password"])
            except pd.errors.EmptyDataError:
                users = pd.DataFrame(columns=["username", "password"])

            if new_user in users["username"].values:
                st.error("이미 존재하는 아이디입니다.")
            else:
                new_entry = pd.DataFrame([[new_user, new_pass]], columns=["username", "password"])
                new_entry.to_csv(USER_FILE, mode="a", index=False, header=not USER_FILE.exists() or USER_FILE.stat().st_size == 0)
                st.success("회원가입 성공! 로그인 탭으로 이동해 주세요.")
