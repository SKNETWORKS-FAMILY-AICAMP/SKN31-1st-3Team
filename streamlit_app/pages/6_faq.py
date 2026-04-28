import streamlit as st
import time
import numpy as np
import json
import os
from utils.crawling_handler import crawl_pse_faq

st.set_page_config(
    page_title="전기차 FAQ",
    page_icon="❓",
    layout="wide",
)

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

SUBSIDY_FAQ_PATH = os.path.join(
    _THIS_DIR, "..", "..", "backend", "Dataset", "faq_data.json"
)


@st.cache_data
def load_faq(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def show_faq(faq_list):
    """FAQ 리스트를 검색창 + expander로 표시."""
    search = None # st.text_input("질문 검색", placeholder="키워드를 입력하세요", key=faq_list[0]["question"]) 

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
        for item in filtered:
            with st.expander(item["question"]):
                st.markdown(item["answer"])


# ============================================================
# 페이지
url= 'https://www.pse.com/ko/pages/electric-cars/electric-vehicles-faq'
faq_data = crawl_pse_faq(url)
items = list(faq_data.items())
over = (len(items) + 1) // 2  

st.title("FAQ")
st.text("자주 묻는 질문들을 모아 봤습니다.")
st.divider()

tab1, tab2 = st.tabs(["보조금 FAQ", "전기차 FAQ"])

with tab1:
    faq_subsidy = load_faq(SUBSIDY_FAQ_PATH)
    show_faq(faq_subsidy)

with tab2:
    for question, answer in items[:over]:
        with st.expander(question):
            st.write(answer)


st.divider()
st.caption("본 정보는 참고용이며 정확한 내용은 공식 발표를 확인하세요.")