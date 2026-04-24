import streamlit as st
from utils.db_handler import get_data_from_db

st.title("⚡2_유가변동 욱!!!!!!!!!!!!!!")

# 1. 쿼리 작성
query = "SELECT year, region, count FROM electric_vehicle_count"

# 2. 유틸 함수 호출
df = get_data_from_db(query)

# 3. 화면 출력
if not df.empty:
    pivoted_df = df.pivot_table(index='year', columns='region', values='count', aggfunc='sum')
    st.line_chart(pivoted_df)
else:
    st.error("데이터를 가져오지 못했습니다.")