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
    
