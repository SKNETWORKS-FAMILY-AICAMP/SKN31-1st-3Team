"""전기차 FAQ 페이지 - 보조금 FAQ / 전기차 일반 FAQ"""

import json
import os
import streamlit as st


st.set_page_config(
    page_title="전기차 FAQ",
    page_icon="❓",
    layout="wide",
)

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

SUBSIDY_FAQ_PATH = os.path.join(
    _THIS_DIR, "..", "..", "backend", "Dataset", "faq_data.json"
)
EV_FAQ_PATH = os.path.join(
    _THIS_DIR, "..", "..", "backend", "Dataset", "ev_faq_data.json"
)


@st.cache_data
def load_faq(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def show_faq(faq_list):
    """FAQ 리스트를 검색창 + expander로 표시."""
    search = st.text_input("질문 검색", placeholder="키워드를 입력하세요", key=faq_list[0]["question"])

    if search:
        keyword = search.lower()
        filtered = [
            item for item in faq_list
            if keyword in item["question"].lower()
            or keyword in item["answer"].lower()
        ]
    else:
        filtered = faq_list

    if not filtered:
        st.info("검색 결과가 없습니다.")
    else:
        st.caption(f"총 {len(filtered)}개 질문")
        for item in filtered:
            with st.expander(item["question"]):
                st.markdown(item["answer"])


# ============================================================
# 페이지
# ============================================================

st.title("전기차 FAQ")
st.divider()

tab1, tab2 = st.tabs(["💰 보조금 FAQ", "🚗 전기차 일반 FAQ"])

with tab1:
    st.caption("2026년 전기차 보조금 관련 자주 묻는 질문")
    faq_subsidy = load_faq(SUBSIDY_FAQ_PATH)
    show_faq(faq_subsidy)

with tab2:
    st.caption("전기차 관련 일반 궁금증")
    faq_ev = load_faq(EV_FAQ_PATH)
    show_faq(faq_ev)


st.divider()
st.caption("본 정보는 참고용이며 정확한 내용은 공식 발표를 확인하세요.")