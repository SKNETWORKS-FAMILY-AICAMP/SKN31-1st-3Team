import streamlit as st
import json
import os

st.set_page_config(
    page_title="전기차 FAQ",
    page_icon="❓",
    layout="wide",
)

# ============================================================
# 경로 설정
# ============================================================
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

SUBSIDY_FAQ_PATH = os.path.join(
    _THIS_DIR, "..", "..", "backend", "Dataset", "ev_vs_faq.json"
)

PSE_FAQ_PATH = os.path.join(
    _THIS_DIR, "..", "..", "backend", "Dataset", "pse_faq.json"
)


# ============================================================
# 데이터 로드
# ============================================================
@st.cache_data
def load_faq(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# FAQ 데이터 형식 통일
# ============================================================
def normalize_faq(faq_data):
    """
    dict 형태와 list 형태의 FAQ 데이터를
    [{"question": "...", "answer": "..."}] 형태로 통일
    """

    if isinstance(faq_data, dict):
        return [
            {"question": question, "answer": answer}
            for question, answer in faq_data.items()
        ]

    elif isinstance(faq_data, list):
        return faq_data

    else:
        return []


# ============================================================
# PSE FAQ에서 보여줄 질문만 선택
# ============================================================
def pick_faq(faq_data):
    faq_list = normalize_faq(faq_data)

    include_keywords = [
        "전기차는 실제로 환경에 더 좋은가요",
        "EV 배터리 생산이 환경에 미치는 영향",
        "EV 배터리를 제거하면",
        "BEV와 PHEV의 차이점",
        "전기 트럭을 이용할 수 있나요",
        "EV는 한 번 충전으로 얼마나 멀리",
        "겨울 날씨",
        "EV 배터리는 안전한가요",
        "배터리를 교체해야 하나요",
    ]

    picked = []

    for item in faq_list:
        question = item.get("question", "")

        if any(keyword in question for keyword in include_keywords):
            picked.append(item)

    return picked


# ============================================================
# FAQ 출력 함수
# ============================================================
def show_faq(faq_data):
    """FAQ 데이터를 expander로 표시."""

    faq_list = normalize_faq(faq_data)

    if not faq_list:
        st.info("FAQ 데이터가 없습니다.")
        return

    for item in faq_list:
        question = item.get("question", "질문 없음")
        answer = item.get("answer", "답변 없음")

        with st.expander(question):
            st.markdown(answer)


# ============================================================
# 페이지
# ============================================================
st.title("FAQ")
st.text("자주 묻는 질문들을 모아 봤습니다.")
st.divider()

tab1, tab2 = st.tabs(["전기차 FAQ", "보조금 FAQ"])

with tab1:
    faq_pse = load_faq(PSE_FAQ_PATH)
    picked_pse = pick_faq(faq_pse)
    show_faq(picked_pse)

with tab2:
    faq_subsidy = load_faq(SUBSIDY_FAQ_PATH)
    show_faq(faq_subsidy)
    
st.divider()
st.caption("본 정보는 참고용이며 정확한 내용은 공식 발표를 확인하세요.")

if st.button("🏠 메인 대시보드로 돌아가기", use_container_width=True):
    st.switch_page("app_demo.py") # 메인 파일명에 맞춰 수정 (보통 app.py 또는 main.py)