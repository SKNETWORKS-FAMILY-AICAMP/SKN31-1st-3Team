import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import requests
from bs4 import BeautifulSoup
from utils.db_handler import get_data_from_db
import plotly.express as px

TANK_GAS = 50
TANK_DIESEL = 55
BATTERY = 60
###########################################크롤링 함수 #########################################################################
def get_current_x_price(url):
    try:
        rq = requests.get(url, headers=headers)
    except Exception as e:
        print("error:", e)
        return

    soup = BeautifulSoup(rq.text, "html.parser")

    sections = soup.select("div.grid.grid-cols-2.gap-4")
    temp = []
    
    for section in sections:
        h3_list = section.select("h3.text-title4-b")
        for h3 in h3_list:
            temp.append(h3.text)
    return temp
##########################################################################################################################
url1 = "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%ED%9C%98%EB%B0%9C%EC%9C%A0/%EC%84%9C%EC%9A%B8"
url2 = "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%EA%B3%A0%EA%B8%89%EC%9C%A0/%EC%84%9C%EC%9A%B8"
url3 = "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%EA%B2%BD%EC%9C%A0/%EC%84%9C%EC%9A%B8"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ko-KR,ko;q=0.9",
}
####################크롤링 해온 휘발유, 고급유, 경유 [오늘 서울 평균가, 오늘 전국 평균가]################################################
l1 = get_current_x_price(url1)
l2 = get_current_x_price(url2)
l3 =get_current_x_price(url3)

st.title("⛽ 유가 변동 분석")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("⛽ 오늘 휘발유 가격", f"{l1[1]}/L")

with col2:
    st.metric("🛢 오늘 경유 가격", f"{l3[1]}/L")

with col3:
    st.metric("💎 오늘 고급유 가격", f"{l2[1]}/L")

##########################DB 쿼리로 값 가져오기 #################################################################################
st.divider()
query = """
SELECT 
    f.date,
    f.regular_price,
    f.premium_price,
    d.price AS diesel_price,
    e.price AS electric_price
FROM fuel_price f
LEFT JOIN diesel_price d ON f.date = d.date
JOIN e_price e ON f.date = e.date
ORDER BY f.date;
"""
df = get_data_from_db(query)
######################################풀 주유/ 충전 값 계산 ###################################################################
df_calc = df.copy()

df_calc["regular_gas_full"] = df_calc["regular_price"] * TANK_GAS
df_calc["premium_gas_full"] = df_calc["premium_price"] * TANK_GAS
df_calc["diesel_full"] = df_calc["diesel_price"] * TANK_DIESEL
df_calc["electric_full"] = df_calc["electric_price"] * BATTERY

#########################################################################################################################


##############Line 그래프##############################################################################################
mode = st.toggle("🚗 풀충 / 풀주유 기준으로 보기")
if not mode:
    # 👉 기본 단가 그래프
    st.subheader("📈 유가 / 전기요금 추이 (단가)")

    fig = px.line(
        df,
        x="date",
        y=["regular_price", "premium_price", "diesel_price", "electric_price"],
        labels={"value": "가격", "variable": "종류"},
        color_discrete_map={
        "regular_price": "#f87171", 
        "premium_price": "#fb923c",  
        "diesel_price": "#60a5fa",    
        "electric_price": "#00E5FF"   
    }
    )

    fig.for_each_trace(lambda t: t.update(name={
        "regular_price": "⛽ 휘발유",
        "premium_price": "💎 고급유",
        "diesel_price": "🛢 경유",
        "electric_price": "⚡ 전기요금"
    }[t.name]))

    fig.update_layout(
        yaxis_title="가격 (원 / L, kWh)",
        xaxis_title="년도"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    # 👉 풀충 / 풀주유 그래프
    st.subheader("🚗 풀충 / 풀주유 기준 비용")
    st.caption("📌 평균 승용차 기준: 휘발유 50L / 경유 55L / 전기 60kWh")

    fig2 = px.line(
        df_calc,
        x="date",
        y=["regular_gas_full", "premium_gas_full", "diesel_full", "electric_full"],
        labels={"value": "총 비용 (원)", "variable": "종류"},
        color_discrete_map={
        "regular_gas_full": "#f87171", 
        "premium_gas_full": "#fb923c",  
        "diesel_full": "#60a5fa",    
        "electric_full": "#00E5FF"   
    }
    )

    fig2.for_each_trace(lambda t: t.update(name={
        "regular_gas_full": "⛽ 휘발유 (50L)",
        "premium_gas_full": "💎 고급유",
        "diesel_full": "🛢 경유 (55L)",
        "electric_full": "⚡ 전기 (60kWh)"
    }[t.name]))

    fig2.update_layout(
        yaxis_title="1회 충전/주유 비용 (원)",
        xaxis_title="년도"
    )

    st.plotly_chart(fig2, use_container_width=True)
###############################################################################################################################

#### 변동 그래프 ################################################################################################################
st.divider()
vol = df[["regular_price", "premium_price", "diesel_price", "electric_price"]].std().reset_index()
vol.columns = ["type", "value"]

# 이름 바꾸기
name_map = {
    "regular_price": "⛽ 휘발유",
    "premium_price": "💎 고급유",
    "diesel_price": "🛢 경유",
    "electric_price": "⚡ 전기"
}
vol["type"] = vol["type"].map(name_map)

# 그래프
fig_vol = px.bar(
    vol,
    x="type",
    y="value",
    color="type",
    color_discrete_map={
        "⛽ 휘발유": "#f87171",
        "💎 고급유": "#fb923c",
        "🛢 경유": "#60a5fa",
        "⚡ 전기": "#00E5FF"
    },
    text="value"
)

# 스타일
fig_vol.update_traces(
    texttemplate="%{text:.0f}",
    textposition="outside"
)

fig_vol.update_layout(
    title="📊 변동성 비교",
    showlegend=False,
    height=250,   # 🔥 크기 줄임 (기존의 반 느낌)
    margin=dict(l=10, r=10, t=40, b=10)
)
col1, col2 = st.columns([2,1])

with col1:
    st.plotly_chart(fig_vol, use_container_width=False)

############# 변동 막대 그래프 설명 ###########################################
with col2:
    st.markdown("""
📊 **변동성 계산 기준**

- 각 에너지원의 가격 변동 폭을 비교하기 위해 **표준편차(Standard Deviation)** 사용  
- 값이 클수록 → 가격 변동이 큼  
- 값이 작을수록 → 가격이 안정적  

👉 ⚡ 전기요금은 변동성이 낮고  
👉 ⛽ 유가는 변동성이 큰 특징이 있음
""")

#######################################사용자한테 절감효과 보여주기#######################################################
st.divider()
st.write("📊 **500Km 주행 기준 절감률**")
latest = df_calc.iloc[-1]

fuel_map = {
    "일반 휘발유": "regular_gas_full",
    "고급 휘발유": "premium_gas_full",
    "경유": "diesel_full"
}

# 👉 사용자 선택 UI
fuel_type = st.selectbox("비교할 연료 선택", list(fuel_map.keys()))

col = fuel_map[fuel_type]

# 👉 계산
diff_percent = (
    (latest[col] - latest["electric_full"])
    / latest[col] * 100
)

col1, col2, col3 = st.columns(3)
col1.metric(
    label="절감률",
    value=f"{diff_percent:.2f}%"
)
col2.metric(
    label="연료비",
    value=f"{latest[col]:,.0f}원"
)
col3.metric(
    label="전기차 비용",
    value=f"{latest['electric_full']:,.0f}원"
)