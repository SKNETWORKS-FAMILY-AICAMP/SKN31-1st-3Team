import streamlit as st
import time
import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.db_handler import get_data_from_db
import plotly.graph_objects as go

st.set_page_config(page_title="3_전기차점유율", page_icon="📈")

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

#----------------------------------------------------------------------------
st.title("전기차 등록 현황")
st.text("전기차 등록 비율의 증가 추이")
st.set_page_config(layout="wide")

@st.cache_data()
def load_registrated_car_data():
    rdf = pd.DataFrame(get_data_from_db("select * from ev_registration_by_year"))
    car = pd.DataFrame(get_data_from_db("select * from car_total"))
    evcar = pd.DataFrame(get_data_from_db("select * from electric_vehicle_count"))
    return rdf, car, evcar
temp = load_registrated_car_data()
rdf = temp[0]
car = temp[1]
evcar = temp[2]


# 1번째 줄 좌측 연도별 전기차 신규 등록 대수 그래프
col1,col2 = st.columns(2)

rdf['year_label'] = rdf['year'].astype(str).str.replace('2026', '2026.03', regex=False)

rdfgraph = go.Figure()
rdf_chart = rdf[rdf["year"] <= 2025] 


rdfgraph.add_trace(go.Scatter(
    x=rdf_chart["year"],
    y=rdf_chart["ev_car"],
    mode='lines',
    line=dict(color='rgba(0, 122, 255, 0.5)'),
    fill='tozeroy',
    fillcolor='rgba(0, 122, 255, 0.1)'
))

rdfgraph.update_layout(
    title=dict(
        text="연도별 전기차 신규 등록 대수(2017~2025)",
        x=0,
        y=0.9,
        font=dict(size=20)),
    xaxis=dict(
        type='category',
        categoryorder='array',
        categoryarray=rdf["year_label"].tolist()
    ),
    margin=dict(l=10, r=10, t=40, b=10),
    height=350,
    autosize=True
)

with col1:
    with st.container(border=True):
        st.plotly_chart(rdfgraph, use_container_width=True)

# 1번째 줄 우측 전체 자동차 대비 전기차 비중

# 전기차 연도별 마지막 월 누적 합계
ev_last = evcar.loc[evcar.groupby('year')['month'].idxmax()]
ev_yearly = ev_last.groupby('year')['count'].sum().reset_index()
ev_yearly.columns = ['year', 'ev_total']

# 전체 자동차 연도별 총계
car_yearly = car[['year', 'total']].copy()
car_yearly.columns = ['year', 'car_total']
car_yearly['year'] = car_yearly['year'].astype(int)

# 병합 및 비중 계산
df = pd.merge(ev_yearly, car_yearly, on='year')
df['ev_ratio'] = (df['ev_total'] / df['car_total'] * 100).round(2)

# 그래프
fig_ratio = go.Figure()

fig_ratio.add_trace(go.Bar(
    x=df["year"],
    y=df["ev_ratio"],
    marker_color='rgba(0, 122, 255, 0.6)'
))

fig_ratio.update_layout(
    title=dict(
        text="전체 자동차 대비 전기차 등록 비중",
        x=0,
        y=0.9,
        font=dict(size=20)),
    xaxis=dict(tickmode='linear'),
    yaxis=dict(ticksuffix="%"),
    margin=dict(l=10, r=10, t=40, b=10),
    height=350,
    autosize=True,
    bargap=0.5
)

with col2:
    with st.container(border=True):
        st.plotly_chart(fig_ratio, use_container_width=True)

# 2번째 줄

col3, col4, col5 = st.columns(3)

row_2022 = rdf.query('year == 2022').iloc[0]
row_2026 = rdf.query('year == 2026').iloc[0]

ratio_2022 = row_2022['ev_car'] / row_2022['car']
ratio_2026 = row_2026['ev_car'] / row_2026['car']

up = (ratio_2026 / ratio_2022 - 1)

with col3:
    with st.container(border=True):
        st.metric(label="2022년 신규 전기차 비중", value=f"{round(ratio_2022 * 100, 2)}%")

with col4:
    with st.container(border=True):
        st.metric(label="2026년 3월 신규 전기차 비중", value=f"{round(ratio_2026 * 100, 2)}%")

with col5:
    with st.container(border=True):
        st.metric(label="22년 대비 2026년 03월 기준 신규 전기차 증가율", value=f"{round(up * 100, 2)}%")

# 3번째 줄

rdf['ev_ratio'] = (rdf['ev_car'] / rdf['car'] * 100).round(1)
rdf['year_label'] = rdf['year'].astype(str).str.replace('2026', '2026.03', regex=False)

rdf_table = rdf[rdf["year"] >= 2022].copy()

rdf_table = rdf_table.drop(columns=['year'])
rdf_table = rdf_table.rename(columns={
    'year_label': '연도',
    'car': '자동차',
    'ev_car': '전기차',
    'ev_ratio': '전기차 비중(%)'
})
rdf_table = rdf_table[['연도', '자동차', '전기차', '전기차 비중(%)']]

rdf_table['자동차'] = rdf_table['자동차'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else '-')
rdf_table['전기차'] = rdf_table['전기차'].apply(lambda x: f"{int(x):,}")
rdf_table['전기차 비중(%)'] = rdf_table['전기차 비중(%)'].apply(lambda x: f"{x}%" if pd.notna(x) else '-')

st.dataframe(
    rdf_table,
    hide_index=True,
    use_container_width=False,
    width=600,
    column_config={
        '연도': st.column_config.TextColumn('연도', width=80),
        '자동차': st.column_config.TextColumn('자동차', width=150),
        '전기차': st.column_config.TextColumn('전기차', width=150),
        '전기차 비중(%)': st.column_config.TextColumn('전기차 비중(%)', width=100),
    }
)