import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

# 초기화
if "auth" not in st.session_state:
    st.session_state.auth = False
if "username" not in st.session_state:
    st.session_state.username = ""

# 로그인 상태 확인
if not st.session_state.auth:
    st.warning("로그인이 필요합니다. 초기화면으로 이동합니다.")
    st.page_link("login.py", label="🔑 로그인하러 가기")
    st.stop()

# 사용자별 파일
username = st.session_state.username
DATA_FILE = f"{username}_budget.csv"
BUDGET_FILE = f"{username}_budget_settings.csv"

# -------------------------------
# 데이터 함수
# -------------------------------
def load_data():
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["날짜"])
        if "날짜" not in df.columns:
            raise ValueError("날짜 컬럼 없음")
        return df
    except:
        return pd.DataFrame(columns=["날짜", "구분", "카테고리", "금액", "결제수단", "메모"])

def save_data(new_data):
    df = load_data()
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def load_budget():
    try:
        return pd.read_csv(BUDGET_FILE, index_col="카테고리")
    except:
        return pd.DataFrame(columns=["카테고리", "예산"]).set_index("카테고리")

def save_budget(budget_df):
    budget_df.to_csv(BUDGET_FILE)

# -------------------------------
# 앱 본문
# -------------------------------
st.set_page_config(page_title="가계부 메인", page_icon="💰")
st.title(f"💰 {username}님의 가계부")

with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("날짜", date.today())
        category_type = st.selectbox("구분", ["지출", "수입"])
        category = st.selectbox("카테고리", ["식비", "간식", "교통", "의복/미용", "쿠팡/마트", "세금", "보험", "기타", "가족 경조사", "지인 경조사", "급여", "성과금", "금융수입", "기타수입"])
    with col2:
        payment = st.selectbox("결제수단", ["체크카드","신용카드", "현금", "이체"])
        amount = st.number_input("금액", min_value=0, step=100)
    memo = st.text_input("메모 (선택)")

    submitted = st.form_submit_button("저장하기")
    if submitted:
        new_row = pd.DataFrame({
            "날짜": [date_input],
            "구분": [category_type],
            "카테고리": [category],
            "금액": [amount],
            "결제수단": [payment],
            "메모": [memo]
        })
        save_data(new_row)
        st.success("저장 완료!")

# -------------------------------
# 필터링 및 출력
# -------------------------------
df = load_data()
year_month = "선택된 기간 없음"
if not df.empty:
    df["년"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month
    df["주차"] = df["날짜"].dt.isocalendar().week

    기준 = st.radio("조회 기준", ["월별", "주간", "연도별"])

    if 기준 == "월별":
        ym_options = sorted(df[["년", "월"]].drop_duplicates().apply(lambda x: f"{x['년']}-{x['월']:02}", axis=1), reverse=True)
        year_month = st.selectbox("월 선택", ym_options)
        y, m = map(int, year_month.split("-"))
        df_filtered = df[(df["년"] == y) & (df["월"] == m)]

    elif 기준 == "주간":
        week_options = sorted(df["주차"].unique(), reverse=True)
        selected_week = st.selectbox("주차 선택", week_options)
        df_filtered = df[df["주차"] == selected_week]
        year_month = f"{selected_week}주차"

    elif 기준 == "연도별":
        year_options = sorted(df["년"].unique(), reverse=True)
        selected_year = st.selectbox("연도 선택", year_options)
        df_filtered = df[df["년"] == selected_year]
        year_month = f"{selected_year}년"
else:
    df_filtered = pd.DataFrame()

# 예산 설정
st.subheader("📌 예산 설정")
budget_df = load_budget()
edited_budget = st.data_editor(
    budget_df.reindex(columns=["예산"]).fillna(0),
    num_rows="dynamic",
    key="budget_editor"
)
if st.button("💾 예산 저장"):
    save_budget(edited_budget)
    st.success("예산이 저장되었습니다!")

# 내역 요약
st.subheader(f"📊 {year_month} 내역 요약")
if not df_filtered.empty:
    total_income = df_filtered[df_filtered["구분"] == "수입"]["금액"].sum()
    total_expense = df_filtered[df_filtered["구분"] == "지출"]["금액"].sum()
    net_balance = total_income - total_expense

    st.markdown(f"""
    **총 수입:** {total_income:,.0f}원  
    **총 지출:** {total_expense:,.0f}원  
    **잔액:** {net_balance:,.0f}원
    """)

    st.dataframe(df_filtered[["날짜", "구분", "카테고리", "금액", "결제수단", "메모"]].sort_values("날짜", ascending=False))

    # 지출 요약
    expense_summary = df_filtered[df_filtered["구분"] == "지출"].groupby("카테고리")["금액"].sum()
    st.subheader("📂 지출 카테고리별 요약")
    for cat, spent in expense_summary.items():
        budget = edited_budget["예산"].get(cat, 0)
        remaining = budget - spent
        percent = min(int((spent / budget) * 100), 100) if budget > 0 else 0
        st.write(f"**{cat}**: {spent:,.0f}원 / {budget:,.0f}원 ({remaining:,.0f}원 남음)")
        st.progress(percent)

    # Pie Chart
    st.subheader("🍕 지출 비율(Pie Chart)")
    fig1, ax1 = plt.subplots()
    ax1.pie(expense_summary.values, labels=expense_summary.index, autopct="%1.1f%%")
    st.pyplot(fig1)

    # Line Chart
    st.subheader("📈 월별 지출 추이(Line Chart)")
    monthly = df[df["구분"] == "지출"].groupby(["년", "월"])["금액"].sum().reset_index()
    monthly["연-월"] = monthly["년"].astype(str) + "-" + monthly["월"].astype(str)
    st.line_chart(monthly.set_index("연-월")["금액"])
else:
    st.info("선택된 기간의 데이터가 없습니다.")
