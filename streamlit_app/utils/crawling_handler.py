import requests
from bs4 import BeautifulSoup
import json
import os
import streamlit as st


# =========================
# 공통 설정
# =========================
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ko-KR,ko;q=0.9",
}


# =========================
# 공통 유틸
# =========================
def get_soup(url: str):
    """HTML 가져와서 BeautifulSoup 반환"""
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return BeautifulSoup(res.text, "lxml")


def save_json(data, path):
    """JSON 저장"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# =========================
# 1. 가격 크롤링 (Streamlit 캐시)
# =========================
@st.cache_data
def get_current_x_price(url: str):
    soup = get_soup(url)

    sections = soup.select("div.grid.grid-cols-2.gap-4")
    result = []

    for section in sections:
        h3_list = section.select("h3.text-title4-b")
        for h3 in h3_list:
            text = h3.get_text(strip=True)
            if text:
                result.append(text)

    return result


#url = "https://ev-vs.com/blog/ev-subsidy-faq-2026"
# =========================
# 2. EV-VS FAQ 크롤링 (EV subsidy)
# =========================
def crawl_ev_subsidy_faq(url: str):
    soup = get_soup(url)

    faq = []

    for h3 in soup.select("h3"):
        question = h3.get_text(strip=True)

        answers = []
        for sib in h3.find_next_siblings():
            if sib.name in ["h2", "h3"]:
                break

            text = sib.get_text(" ", strip=True)
            if text:
                answers.append(text)

        faq.append({
            "question": question,
            "answer": "\n".join(answers)
        })

    return faq


# =========================
# 3. PSE FAQ 크롤링
# =========================
def crawl_pse_faq(url: str):
    soup = get_soup(url)

    titles = soup.select(
        "div.row.help-container div.topic-wrapper div.panel.panel-default div.title-collapse p"
    )
    answers = soup.select(
        "div.row.help-container div.topic-wrapper div.panel.panel-default div.panel-collapse p"
    )

    t = [x.get_text(strip=True) for x in titles if x.get_text(strip=True)]
    a = [x.get_text(strip=True) for x in answers if x.get_text(strip=True)]

    faq = {q: a for q, a in zip(t, a)}
    return faq
