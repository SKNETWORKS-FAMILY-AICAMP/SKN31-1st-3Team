# Contents of ~/my_app/streamlit_app.py
import streamlit as st
from utils.db_handler import get_data_from_db

st.title("🚗 자동차 등록대수 현황")

# 테이블 1: 자동차 등록 대수
query1 = "SELECT * FROM car_total"
df_car = get_data_from_db(query1)

# 스트림릿 화면에 출력
st.subheader("🚗 자동차 등록 대수")
st.dataframe(df_car)
