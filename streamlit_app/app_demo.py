import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os
import json
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

from utils.crawling_handler import get_current_x_price, crawl_pse_faq
from utils.db_handler import get_fuel_data_processed, get_share_data_processed
from utils.map_handler import create_ev_map
from utils.kakao_map_handler import get_distance, to_float, calculate_costs


# -------------------
# 페이지 기본 설정 및 디자인 
# -------------------
st.set_page_config(
    page_title="쥬피썬더: EV 비용 분석 플랫폼",
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed" 
)

st.markdown("""
<style>
    /* 전체 배경색 변경 (초경량 그레이) */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Streamlit 기본 헤더/푸터 숨기기 (더 깔끔하게) */
    #MainMenu, footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 메인 콘텐츠 영역 여백 조정 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 제목 스타일 커스텀 */
    h1 {
        color: #1E293B;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
    }
    
    h2, h3 {
        color: #334155;
        font-weight: 700;
        margin-top: 1.5rem;
    }

    /* 카드형 레이아웃 스타일 (뉴모피즘 라이트) */
    .ev-card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        border: 1px solid #E2E8F0;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------
# 상단 내비게이션 메뉴
# -------------------
selected = option_menu(
    None,
    ["대시보드", "유가 분석", "점유율 트렌드", "충전 인프라", "시뮬레이터"],
    icons=["grid-1x2", "graph-down-arrow", "pie-chart-fill", "ev-station", "calculator"],
    orientation="horizontal",
    default_index=0,
    styles={
        "container": {
            "padding": "10px !important",
            "background-color": "#FFFFFF",
            "border-radius": "1rem",
            "box-shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            "border": "1px solid #E2E8F0",
            "margin": "0 auto 2rem auto", # 중앙 정렬을 위해 auto 사용
            "max-width": "1400px",       # 와이드 모드에서 너무 퍼지지 않게 너비 제한
        },
        "icon": {
            "color": "#00A3FF",
            "font-size": "1.1rem"
        },
        "nav-link": {
            "font-size": "1rem",
            "font-weight": "500",
            "text-align": "center",
            "margin": "0px 5px",        # 아이템 간 간격 최적화
            "padding": "10px 0px",      # 패딩 조정
            "border-radius": "0.5rem",
            "color": "#475569",
            "--hover-color": "#F1F5F9",
            "flex": "1 1 0%",           # 각 메뉴가 동일한 가로 비율을 갖도록 설정
        },
        "nav-link-selected": {
            "background-color": "#E0F2FE",
            "color": "#00A3FF",
            "font-weight": "700",
        },
    }
)

# -------------------
# 1. 대시보드
# -------------------
if selected == "대시보드":
    st.markdown("<h1>⚡ 쥬피썬더: EV 비용 분석 플랫폼</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 1.1rem;'>SKN31기 1차 프로젝트: 데이터 기반 전기차 전환 경제성 분석 서비스</p>", unsafe_allow_html=True)
    st.write("---")
    
    top_col1, top_col2 = st.columns([1, 2], gap="large")

    with top_col1:
        # [왼쪽] 팀 정체성 카드
        st.markdown(f"""
        <div class="ev-card" style="border: 2px solid #00A3FF; background-color: #E0F2FE; height: 380px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 3rem; color: #00A3FF; text-align: center; margin-bottom: 1rem;">
                <span style="opacity: 0.5;">⛽</span> <span style="font-size: 4rem;">⚡</span> <span style="opacity: 0.5;">💰</span>
            </div>
            <h3 style="margin-top:0; color: #00A3FF; text-align: center;">SKN31기 분석팀</h3>
            <p style="color: #0369A1; text-align: center; font-size: 0.95rem; line-height: 1.8;">
                흩어져 있는 <b>유가·전기료·인프라</b> 데이터를<br>
                <span style="color: #00A3FF; font-weight: 700;">SQL</span>로 통합 구축하고,<br>
                사용자 맞춤형 <span style="color: #00A3FF; font-weight: 700;">비용 시뮬레이션</span>을 통해<br>
                전기차 전환의 <b>확실한 경제적 기준</b>을 제시합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # [왼쪽] 주요 기능 카드 (기획안의 🚀 주요 기능 반영)
        st.markdown(f"""
        <div class="ev-card">
            <h3 style="margin-top:0;">🚀 핵심 분석 기능</h3>
            <p style="color: #64748B; margin-bottom: 1.5rem;">데이터 기반의 4가지 핵심 인사이트를 확인하세요.</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div style="border: 1px solid #E2E8F0; padding: 1.5rem; border-radius: 1rem; background-color: #F8FAFC;">
                    <div style="font-size: 1.5rem; color: #00A3FF;">📈</div>
                    <div style="font-weight: 700; color: #1E293B; margin-top: 0.5rem;">보급률 트렌드</div>
                    <div style="font-size: 0.85rem; color: #64748B;">최근 10년 등록 데이터 분석</div>
                </div>
                <div style="border: 1px solid #E2E8F0; padding: 1.5rem; border-radius: 1rem; background-color: #F8FAFC;">
                    <div style="font-size: 1.5rem; color: #00A3FF;">⛽</div>
                    <div style="font-weight: 700; color: #1E293B; margin-top: 0.5rem;">에너지 비용 분석</div>
                    <div style="font-size: 0.85rem; color: #64748B;">유가 vs 전기료 변동 추이</div>
                </div>
                <div style="border: 1px solid #E2E8F0; padding: 1.5rem; border-radius: 1rem; background-color: #F8FAFC;">
                    <div style="font-size: 1.5rem; color: #00A3FF;">🗺️</div>
                    <div style="font-weight: 700; color: #1E293B; margin-top: 0.5rem;">인프라 맵</div>
                    <div style="font-size: 0.85rem; color: #64748B;">지역별 충전 시설 분포 현황</div>
                </div>
                <div style="border: 1px solid #E2E8F0; padding: 1.5rem; border-radius: 1rem; background-color: #F8FAFC;">
                    <div style="font-size: 1.5rem; color: #00A3FF;">🧮</div>
                    <div style="font-weight: 700; color: #1E293B; margin-top: 0.5rem;">비용 계산기</div>
                    <div style="font-size: 0.85rem; color: #64748B;">실제 예상 절감액 시뮬레이션</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with top_col2:
        # [오른쪽] 프로젝트 배경 및 필요성 (기획안 📌 내용 반영)
        st.markdown(f"""
        <div class="ev-card" style="height: 380px;">
            <h3 style="margin-top:0; color: #1E293B;">📌 프로젝트 배경 및 목표</h3>
            <div style="margin-top: 1.2rem;">
                <p style="color: #475569; line-height: 1.7; font-size: 1.05rem;">
                    전기차 전환을 고민하는 가장 큰 이유는 <b>"정말 돈이 절약되는가?"</b>에 대한 확신 부족입니다. 
                    유가, 전기료, 충전 인프라 등 파편화된 데이터를 하나로 통합했습니다.
                </p>
                <ul style="color: #475569; line-height: 2.0; font-size: 1rem; margin-top: 1rem;">
                    <li>🎯 <b>데이터 통합:</b> 내연차 vs 전기차의 동일 기준 비용 비교</li>
                    <li>🎯 <b>개인화 분석:</b> 주행 패턴을 반영한 실제 비용 효율 도출</li>
                    <li>🎯 <b>의사결정 지원:</b> 현실적인 전기차 선택 기준 제시</li>
                </ul>
            </div>
            <div style="display: flex; gap: 10px; margin-top: 1.5rem;">
                <span style="background-color: #E0F2FE; color: #00A3FF; padding: 7px 18px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">#전기차_경제성</span>
                <span style="background-color: #E0F2FE; color: #00A3FF; padding: 7px 18px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">#데이터_시각화</span>
                <span style="background-color: #E0F2FE; color: #00A3FF; padding: 7px 18px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">#비용_시뮬레이션</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
 
    # 1. FAQ HTML 정의 (핵심 5가지 질문)
        faq_html = """
<div class="ev-card" style="margin-top: 1.5rem;">
<h3 style="margin-top:0; color: #1E293B;">❓ FAQ</h3>
<p style="color: #64748B; margin-bottom: 1.5rem;">전기차 구매 전 가장 많이 궁금해하시는 핵심 질문입니다.</p>
<div style="display: flex; flex-direction: column; gap: 0.8rem;">
<details style="border: 1px solid #E2E8F0; padding: 1rem; border-radius: 1rem; background-color: #F8FAFC; cursor: pointer;">
<summary style="font-weight: 700; color: #1E293B; list-style: none; display: flex; justify-content: space-between; align-items: center;">
<span>Q. EV 배터리는 안전한가요? </span>
<span style="color: #00A3FF;">▼</span>
</summary>
<div style="margin-top: 0.8rem; font-size: 0.9rem; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 0.8rem; line-height: 1.6;">
네.전기 자동차는 운전과 관련된 배기가스 배출량을 엄격하게 살펴보면 가스 구동 자동차보다 환경에 더 좋습니다
</div>
</details>
<details style="border: 1px solid #E2E8F0; padding: 1rem; border-radius: 1rem; background-color: #F8FAFC; cursor: pointer;">
<summary style="font-weight: 700; color: #1E293B; list-style: none; display: flex; justify-content: space-between; align-items: center;">
<span>Q. 전기차는 실제로 환경에 더 좋은가요?</span>
<span style="color: #00A3FF;">▼</span>
</summary>
<div style="margin-top: 0.8rem; font-size: 0.9rem; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 0.8rem; line-height: 1.6;">
100세대 이상 아파트의 경우 신축은 총 주차대수의 5%, 기축은 2% 이상 충전시설 설치가 의무화되어 있습니다.
</div>
</details>
<details style="border: 1px solid #E2E8F0; padding: 1rem; border-radius: 1rem; background-color: #F8FAFC; cursor: pointer;">
<summary style="font-weight: 700; color: #1E293B; list-style: none; display: flex; justify-content: space-between; align-items: center;">
<span>Q. 겨울철 전기차 주행거리 감소 해결법은?</span>
<span style="color: #00A3FF;">▼</span>
</summary>
<div style="margin-top: 0.8rem; font-size: 0.9rem; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 0.8rem; line-height: 1.6;">
히트펌프 시스템이 탑재된 차량을 선택하거나, 주행 전 예약 공조 기능을 활용하면 배터리 효율을 높일 수 있습니다.
</div>
</details>
<details style="border: 1px solid #E2E8F0; padding: 1rem; border-radius: 1rem; background-color: #F8FAFC; cursor: pointer;">
<summary style="font-weight: 700; color: #1E293B; list-style: none; display: flex; justify-content: space-between; align-items: center;">
<span>Q. 전기차 배터리 무상 보증 기간은?</span>
<span style="color: #00A3FF;">▼</span>
</summary>
<div style="margin-top: 0.8rem; font-size: 0.9rem; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 0.8rem; line-height: 1.6;">
대부분의 제조사에서 핵심 부품에 대해 10년/16만km 이상의 무상 보증을 제공하고 있습니다.
</div>
</details>
<details style="border: 1px solid #E2E8F0; padding: 1rem; border-radius: 1rem; background-color: #F8FAFC; cursor: pointer;">
<summary style="font-weight: 700; color: #1E293B; list-style: none; display: flex; justify-content: space-between; align-items: center;">
<span>Q. 완속 충전과 급속 충전의 차이는?</span>
<span style="color: #00A3FF;">▼</span>
</summary>
<div style="margin-top: 0.8rem; font-size: 0.9rem; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 0.8rem; line-height: 1.6;">
급속은 30분 내외로 80% 충전이 가능하며, 완속은 5~10시간 소요되나 배터리 수명 관리에 유리합니다.
</div>
</details>
</div>
<div style="margin-top: 1.5rem; text-align: center;">
<a href="https://www.ev.or.kr" target="_blank" style="text-decoration: none;">
<div style="background-color: #00A3FF; color: white; padding: 12px 20px; border-radius: 0.8rem; font-weight: 700; display: inline-block;">
🔍 무공해차 누리집에서 더 확인하기
</div>
</a>
</div>
</div>
"""
        st.markdown(faq_html, unsafe_allow_html=True)
        if st.button("🔍 전체 FAQ 리스트 확인하기", use_container_width=True):
        # 팀원이 만든 상세 FAQ 페이지 파일명으로 이동
            st.switch_page("pages/6_faq.py") # 실제 파일 경로에 맞게 수정해줘!
            
# -------------------
# 2. 유가분석
# ------------------- 
elif selected == "유가 분석":  

    st.markdown("<h1>⛽ 유가 변동 분석</h1>", unsafe_allow_html=True)
    
    # 1. 상단 실시간 가격 (크롤링 호출)
    urls = {
        "휘발유": "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%ED%9C%98%EB%B0%9C%EC%9C%A0/%EC%84%9C%EC%9A%B8",
        "고급유": "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%EA%B3%A0%EA%B8%89%EC%9C%A0/%EC%84%9C%EC%9A%B8",
        "경유": "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%EA%B2%BD%EC%9C%A0/%EC%84%9C%EC%9A%B8"
    }
    
    l1 = get_current_x_price(urls["휘발유"])
    l2 = get_current_x_price(urls["고급유"])
    l3 = get_current_x_price(urls["경유"])

    # 메트릭 카드 디자인
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("⛽ 오늘 휘발유 가격", f"{l1[1]}/L")

    with col2:
        st.metric("🛢 오늘 경유 가격", f"{l3[1]}/L")

    with col3:
        st.metric("💎 오늘 고급유 가격", f"{l2[1]}/L")

    # 2. 데이터 처리 및 그래프
    df, df_calc = get_fuel_data_processed()
    st.divider()

    mode = st.toggle("🚗 풀충 / 풀주유 기준으로 보기")
    
    if not mode:
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
    # 3. 변동성 및 절감률 섹션
    st.divider()
    vol = df[["regular_price", "premium_price", "diesel_price", "electric_price"]].std().reset_index()
    vol.columns = ["type", "value"]
    
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

# =========================
# 3. 점유율 트렌드
# ========================= 
elif selected == "점유율 트렌드":

    # load & 
    rdf, df_ratio = get_share_data_processed()

    st.markdown("<h1>📈 전기차 등록 및 점유율 현황</h1>", unsafe_allow_html=True)
    st.write("전기차 등록 비율의 증가 추이를 분석합니다.")
    st.write("---")

    # [1번째 줄] 차트 레이아웃
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            rdf_chart = rdf[rdf["year"] <= 2025] 
            rdfgraph = go.Figure()
            rdfgraph.add_trace(go.Scatter(
                x=rdf_chart["year"], y=rdf_chart["ev_car"],
                mode='lines', fill='tozeroy',
                line=dict(color='rgba(0, 122, 255, 0.5)'),
                fillcolor='rgba(0, 122, 255, 0.1)'
            ))
            rdfgraph.update_layout(
                title="연도별 전기차 신규 등록 대수(2017~2025)",
                height=350, margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(rdfgraph, use_container_width=True)

    with col2:
        with st.container(border=True):
            fig_ratio = go.Figure()
            fig_ratio.add_trace(go.Bar(
                x=df_ratio["year"], y=df_ratio["ev_ratio"],
                marker_color='rgba(0, 122, 255, 0.6)'
            ))
            fig_ratio.update_layout(
                title="전체 자동차 대비 전기차 등록 비중",
                yaxis=dict(ticksuffix="%"),
                height=350, margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_ratio, use_container_width=True)

    # [2번째 줄] 주요 지표 (Metric)
    st.write("")
    col3, col4, col5 = st.columns(3)
    
    row_2022 = rdf.query('year == 2022').iloc[0]
    row_2026 = rdf.query('year == 2026').iloc[0]
    r22, r26 = row_2022['ev_car']/row_2022['car'], row_2026['ev_car']/row_2026['car']
    up = (r26 / r22 - 1)

    with col3:
        with st.container(border=True):
            st.metric("2022년 신규 전기차 비중", f"{round(r22 * 100, 2)}%")
    with col4:
        with st.container(border=True):
            st.metric("2026년 3월 신규 전기차 비중", f"{round(r26 * 100, 2)}%")
    with col5:
        with st.container(border=True):
            st.metric("22년 대비 신규 전기차 증가율", f"{round(up * 100, 2)}%", delta="Increased")

    # [3번째 줄] 상세 데이터 테이블 (비중 컬럼 포함)
    st.write("---")
    st.subheader("📋 연도별 상세 등록 데이터 (2022~2026.03)")
    
    # 테이블용 데이터 가공
    rdf_table = rdf[rdf["year"] >= 2022].copy()
    
    # 비중 계산 (소수점 1자리)
    rdf_table['ev_ratio'] = (rdf_table['ev_car'] / rdf_table['car'] * 100).round(1)
    
    # 천 단위 콤마 및 퍼센트 기호 추가 (표시용)
    display_df = rdf_table.copy()
    display_df['car'] = display_df['car'].apply(lambda x: f"{int(x):,}")
    display_df['ev_car'] = display_df['ev_car'].apply(lambda x: f"{int(x):,}")
    display_df['ev_ratio'] = display_df['ev_ratio'].apply(lambda x: f"{x}%")
    
    st.dataframe(
        display_df[['year_label', 'car', 'ev_car', 'ev_ratio']],
        column_config={
            "year_label": st.column_config.TextColumn("연도(기준)", width="medium"),
            "car": st.column_config.TextColumn("전체 자동차 (대)", width="medium"),
            "ev_car": st.column_config.TextColumn("전기차 등록수 (대)", width="medium"),
            "ev_ratio": st.column_config.TextColumn("전기차 비중 (%)", width="small"),
        },
        use_container_width=True,
        hide_index=True
    )

# =========================
# 4. 충전 인프라
# ========================= 
elif selected == "충전 인프라":
    
    st.markdown("<h1>🔌 전기차 충전 인프라 현황</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>전국 8개 권역의 전기차 충전기 보급 추이 (2020년 ~ 현재)</p>", unsafe_allow_html=True)
    st.write("---")

    # 1. 제어 필터 (디자인 일관성을 위해 ev-card 스타일 적용 가능)
    with st.container():
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            speed = st.radio(
                "⚡ 충전 속도 선택",
                options=["전체", "완속", "급속"],
                horizontal=True,
                key="map_speed"
            )
        with f_col2:
            view_mode = st.radio(
                "📊 보기 모드",
                options=["누적 증가율", "절대 수"],
                horizontal=True,
                help="절대 수: 시점별 보유량 / 누적 증가율: 2020년 대비 성장폭(%)",
                key="map_mode"
            )

    # 2. 지도 렌더링
    st.write("") # 간격
    fig = create_ev_map(speed, view_mode)
    st.plotly_chart(fig, use_container_width=True)

    # 3. 인사이트 카드 (기존 마크다운을 ev-card 스타일로 래핑)
    st.markdown("""
    <div class="ev-card" style="background-color: #F1F5F9; border: none;">
        <h4 style="margin-top:0;">💡 지역별 인프라 해석 가이드</h4>
        <p style="color: #475569; font-size: 0.95rem;">
            <b>제주도:</b> 2012년 CFI2030 정책으로 가장 먼저 인프라를 구축한 지역입니다. 
            이미 충분한 기수를 확보했기에 증가율은 낮아 보일 수 있으나, <b>인구 대비 보급률은 전국 최고 수준</b>입니다.<br><br>
            <b>수도권 및 광역시:</b> 최근 3년간 절대 수와 증가율이 동시에 폭발적으로 상승하고 있으며, 
            특히 '급속 충전기' 비중이 빠르게 늘어나는 추세입니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.caption("데이터 출처: 공공데이터포털 (지역별 전기차 충전기 구축현황) · 지도: southkorea-maps")

# =========================
# 5. 시뮬레이터
# ========================= 
elif selected == "시뮬레이터":
    st.markdown("<h1>🧮 출퇴근 비용 시뮬레이터</h1>", unsafe_allow_html=True)
    
    # 1. 실시간 유가 데이터 로드 (유틸리티 재사용)
    urls = {
        "휘발유": "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%ED%9C%98%EB%B0%9C%EC%9C%A0/%EC%84%9C%EC%9A%B8",
        "경유": "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%EA%B2%BD%EC%9C%A0/%EC%84%9C%EC%9A%B8"
    }
    l1 = get_current_x_price(urls["휘발유"])
    l2 = get_current_x_price(urls["경유"])
    
    prices = {
        'gas': l1[1] if len(l1)>1 else "1,650",
        'diesel': l2[1] if len(l2)>1 else "1,550",
        'ev': 300 # 전기차 충전 단가는 고정 혹은 입력
    }
    eff = {'ice': 12, 'ev': 5.5} # 평균 연비

    # 2. 상단 현황판
    st.markdown(f"""
    <div class="ev-card" style="background-color: #F8FAFC;">
        <p style="margin-bottom:10px; color:#64748B;">📊 오늘의 유가 기준 (전국 평균)</p>
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div><small>휘발유</small><br><b>{prices['gas']}</b></div>
            <div><small>경유</small><br><b>{prices['diesel']}</b></div>
            <div><small>전기차(kWh)</small><br><b>{prices['ev']}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. 주소 입력 섹션
    st.markdown("### 📍 나의 출퇴근 경로 설정")
    col1, col2 = st.columns(2)
    with col1:
        start_addr = st.text_input("🏠 출발지 (집)", placeholder="예: 서울 강남구 테헤란로 1")
    with col2:
        end_addr = st.text_input("🏢 도착지 (회사)", placeholder="예: 판교역")

    # 주소 검색 도움말
    with st.expander("🔎 주소 검색 도우미"):
        postcode_html = """
        <script src="//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js"></script>
        <button onclick="new daum.Postcode({oncomplete: function(data) {alert('선택된 주소: ' + data.address);}}).open();" 
                style="padding:8px 12px; border-radius:5px; border:1px solid #ddd; cursor:pointer;">
            📍 도로명 주소 찾기 창 열기
        </button>
        """
        components.html(postcode_html, height=50)

    # 4. 계산 실행
    if st.button("💸 왕복 비용 계산하기", use_container_width=True, type="primary"):
        with st.spinner("경로를 탐색하고 비용을 계산 중입니다..."):
            km = get_distance(start_addr, end_addr)
            
            if km:
                round_km, res_list, savings = calculate_costs(km, prices, eff)
                
                st.balloons()
                st.success(f"📏 예상 왕복 주행 거리: **{round_km:.2f} km**")
                
                # 결과 테이블을 예쁜 카드로 출력
                st.write("### 📋 유종별 유지비 분석")
                st.table(pd.DataFrame(res_list))
                
                # 최종 결과 카드
                st.markdown(f"""
                <div class="ev-card" style="border-left: 5px solid #00C851;">
                    <h4>🏁 분석 결과</h4>
                    <p>내연기관차 대신 전기차로 출퇴근 시 하루 <b>약 {savings:,}원</b> 절약됩니다.</p>
                    <p style="font-size: 1.2rem;">☕ {f"이 돈이면 한 달에 커피 <b>{int((savings*20)/4500)}잔</b>을 더 마실 수 있어요!" if savings > 0 else "티끌 모아 태산! 전기차와 함께 경제적인 드라이빙을 시작하세요."}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("주소를 정확히 입력해 주세요. (예: 시/군/구 포함)")

    st.caption("※ 본 계산은 직선/도로 상황에 따른 추정치이며 실제 주행 환경에 따라 차이가 발생할 수 있습니다.")

