import streamlit as st
import streamlit.components.v1 as components
from utils.kakao_map_handler import get_distance
from streamlit_app.utils.crawling_handler import get_current_x_price
import pandas as pd


# 01_config
st.set_page_config(
    page_title= "SKN31기 1차 프로젝트 데모",    
    page_icon= "🚗",
    layout= "wide",
)
#실시간 보통 휘발유, 경유 가격 크롤링
url1 = "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%ED%9C%98%EB%B0%9C%EC%9C%A0/%EC%84%9C%EC%9A%B8"
url2 = "https://www.oilnow.co.kr/%EC%A3%BC%EC%9C%A0%EC%86%8C-%EA%B0%80%EA%B2%A9%EB%B9%84%EA%B5%90/%EA%B2%BD%EC%9C%A0/%EC%84%9C%EC%9A%B8"

l1 = get_current_x_price(url1)
l2 = get_current_x_price(url2)

# 1. 고정 상수 설정 (가격은 정수형)
GASOLINE_PRICE = l1[1]
DIESEL_PRICE = l2[1]
EV_CHARGING_PRICE = 300
ICE_EFFICIENCY = 12    # 12km/L
EV_EFFICIENCY = 5.5    # 5.5km/kWh

# 페이지 설정
st.set_page_config(page_title="하루 출퇴근 비용 계산기", page_icon="⛽", layout="wide")

# 헤더 섹션
st.write(f"""
# 🧐 매달 나가는 기름값, 정말 이대로 괜찮을까요? 
전국 평균 **휘발유 {GASOLINE_PRICE}원** 시대.  
내연기관차와 전기차의 유지비를 비교하고 오늘 하루 얼마나 아낄 수 있는지 확인해 보세요.
""")

# 2. 유가 현황판 (상단 고정 디스플레이)
st.subheader("📊 오늘의 유가 현황 (오일 나우 전국 평균 기준)")
h_col1, h_col2, h_col3 = st.columns(3)

h_col1.metric("보통휘발유", f"{GASOLINE_PRICE} 원")
h_col2.metric("경유", f"{DIESEL_PRICE} 원")
h_col3.metric("전기차 충전(kWh)", f"{EV_CHARGING_PRICE} 원")

st.markdown("---")

st.subheader("📍 나의 출퇴근 경로")
st.info("📌 도로명 주소 또는 지번 주소 형식으로 입력해주세요.\n예: 서울 강남구 테헤란로 123 / 경기 수원시 장안구 율전동 99-1")

col1, col2 = st.columns(2)

with col1:
    start_addr = st.text_input(
        "🏠 출발지 (집)",
        placeholder="예: 인천 연수구 송도동"
    )

with col2:
    end_addr = st.text_input(
        "🏢 도착지 (회사)",
        placeholder="예: 수원 장안구"
    )

# 👉 중간 버튼 (공통)
st.markdown("### 🔎 도로명 / 지번 찾기")

postcode_html = """
<script src="//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js"></script>

<button onclick="execDaumPostcode()" 
        style="padding:10px 16px; font-size:14px;">
📍 주소 검색하기
</button>

<script>
function execDaumPostcode() {
    new daum.Postcode({
        oncomplete: function(data) {
            document.getElementById("address").value = data.address;
        }
    }).open();
}
</script>
"""

components.html(postcode_html, height=80)

def to_float(x):
    x = str(x).replace(",", "").strip()
    x = str(x).replace("원","")
    return float(x)


# 4. 계산 및 출력
if st.button("💸 오늘 하루 왕복 비용 계산하기", use_container_width=True, type="primary"):
    km = get_distance(start_addr, end_addr)
    
    if km:
        round_trip_km = km * 2
        st.divider()
        # 주행 거리는 소수점 2자리까지 표시
        st.success(f"📏 오늘의 예상 왕복 주행 거리: **{round_trip_km:.2f} km**")
        
        # 비용 계산 (결과값 정수 처리)
        gas_daily = int((round_trip_km / ICE_EFFICIENCY) * to_float(GASOLINE_PRICE))
        diesel_daily = int((round_trip_km / ICE_EFFICIENCY) * to_float(DIESEL_PRICE))
        ev_daily = int((round_trip_km / EV_EFFICIENCY) * to_float(EV_CHARGING_PRICE))
        
        # 결과 테이블 구성
        results = [
            {"유종": "⛽ 보통휘발유", "단가": f"{GASOLINE_PRICE}원/L", "오늘의 왕복 비용": f"{gas_daily}원"},
            {"유종": "⛽ 자동차용경유", "단가": f"{DIESEL_PRICE}원/L", "오늘의 왕복 비용": f"{diesel_daily}원"},
            {"유종": "⚡ 전기차(EV)", "단가": f"{EV_CHARGING_PRICE}원/kWh", "오늘의 왕복 비용": f"{ev_daily}원 (절약! ✅)"}
        ]
        
        st.write("### 📋 오늘의 유종별 비용 비교")
        st.table(pd.DataFrame(results))
        
        # 5. 최종 결론 메시지
        daily_savings = gas_daily - ev_daily
        st.markdown(f"### 🏁 분석 결과")
        st.info(f"오늘 휘발유차 대신 전기차를 이용했다면 **약 {daily_savings:,}원**을 아낄 수 있었습니다.")
        
        # 생활 밀착형 비유 (커피값)
        coffee_count = int(daily_savings / 4500)
        if coffee_count >= 1:
            st.write(f"☕ 이 금액이면 퇴근길에 **커피 {coffee_count}잔**을 사서 기분 좋게 집에 갈 수 있어요!")
        else:
            st.write(f"🪙 매일 조금씩 모여 큰 돈이 됩니다. 지금 바로 전기차를 고려해보세요!")
            
    else:
        st.error("주소를 찾을 수 없습니다. 도로명 주소로 정확하게 입력해 주세요.")

st.markdown("---")
st.caption("※ 본 계산은 직선거리 기준이며, 실제 도로 주행 상황에 따라 유류비는 가감될 수 있습니다.")