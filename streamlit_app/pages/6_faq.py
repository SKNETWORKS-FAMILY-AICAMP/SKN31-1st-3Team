import streamlit as st
import time
import numpy as np
import json
import os
from utils.crawling_handler import crawl_pse_faq

st.title("FAQ")
st.text("자주 묻는 질문들을 모아봤습니다.")

col1, col2 = st.columns(2)

url= 'https://www.pse.com/ko/pages/electric-cars/electric-vehicles-faq'

faq_data = crawl_pse_faq(url)
items = list(faq_data.items())
halfway = (len(items) + 1) // 2  

with col1:
    for question, answer in items[:halfway]:
        with st.expander(question):
            st.write(answer)
