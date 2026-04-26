# 전기차 충전소 현황 페이지. Choropleth 지도로 시각화.
#     충전 속도 선택 (전체/완속/급속)
#     보기 모드 (누적 증가율/절대 수)
#     슬라이더로 시간 변경
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
 
import pandas as pd
import streamlit as st
 
from backend.db.db_connect import get_connection
from streamlit_app.utils.map_handler import (
    load_geojson,
    merge_sidos_to_regions,
    prepare_map_data,
    draw_choropleth,
)
 
 
st.set_page_config(
    page_title="전기차 충전소 현황",
    page_icon="📈",
    layout="wide",
)
 
 
# 슬라이더/라디오 변경마다 DB 재조회를 피하기 위해 캐싱
@st.cache_data
def load_charger_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM ev_charger", conn)
    conn.close()
    return df
 
 
@st.cache_data
def load_map_geojson():
    return merge_sidos_to_regions(load_geojson())
 
 
st.title("전기차 충전소 현황")
st.caption("전국 8개 권역의 전기차 충전기 보급 추이 (2020년 ~ 현재)")
st.divider()
 
col1, col2 = st.columns(2)
 
with col1:
    speed = st.radio(
        "충전 속도",
        options=["전체", "완속", "급속"],
        horizontal=True,
    )
 
with col2:
    view_mode = st.radio(
        "보기 모드",
        options=["누적 증가율", "절대 수"],
        horizontal=True,
        help="절대 수: 시점별 충전기 보유량\n\n누적 증가율: 첫 시점(2020-12) 대비 증가율(%)",
    )
 
 
df_raw = load_charger_data()
geojson = load_map_geojson()
 
df_map = prepare_map_data(
    df_raw,
    period="6month",
    speed=speed,
    with_growth_rate=(view_mode == "누적 증가율"),
)
 
if view_mode == "절대 수":
    color_column = "count"
    color_max = df_map["count"].max()
    title = f"{speed} 충전기 분포"
else:
    color_column = "growth_rate"
    color_max = df_map["growth_rate"].max()
    title = f"{speed} 충전기 누적 증가율 (2020-12 = 100%)"
 
fig = draw_choropleth(
    df_map,
    geojson,
    animation_frame="month",
    color_max=color_max,
    title=title,
    color_column=color_column,
    color_scale="Blues",
)
 
st.plotly_chart(fig, use_container_width=True)
 
st.divider()
 
st.markdown(
    """
    #### 💡 제주도 데이터 해석 참고
    
    제주는 2012년 발표된 **CFI2030(2030 카본프리 아일랜드)** 정책으로 
    전국에서 가장 일찍 전기차 인프라 투자를 시작한 지역입니다.
    
    우리 데이터의 시작점인 2020년에 이미 인구당 충전기 수가 전국 최고 수준이었기 때문에,
    다른 지역의 폭발적 증가와 비교해 누적 증가율은 상대적으로 낮게 표시됩니다.
    
    **부족해서가 아니라 이미 충분해서** 더 늘릴 여지가 적었던 것입니다.
    """
)
 
st.caption(
    "데이터 출처: 공공데이터포털 (지역별 전기차 충전기 구축현황) · "
    "지도: southkorea-maps (CC BY 4.0)"
)