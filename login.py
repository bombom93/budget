import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="로그인", page_icon="🔐")

USER_FILE = Path("users.csv")

# 파일 없으면 기본 사용자 생성
if not USER_FILE.exists():
    pd.DataFrame([{"username": "admin", "password": "test123"}]).to_csv(USER_FILE, index=False)

# 로그인 처리
def login_form():
    st.title("🔐 로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        users = pd.read_csv(USER_FILE)
        if ((users["username"] == username) & (users["password"] == password)).any():
            st.session_state.auth = True
            st.session_state.username = username
            st.success("로그인 성공!")
            st.experimental_rerun()
        else:
            st.error("아이디 또는 비밀번호가 틀렸습니다.")

login_form()
