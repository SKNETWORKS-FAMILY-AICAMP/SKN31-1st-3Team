import requests
from bs4 import BeautifulSoup
import json
import os


url = "https://ev-vs.com/blog/ev-subsidy-faq-2026"

response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

faq = []

for h3 in soup.select("h3"):
    question = h3.get_text(strip=True)
    
    answer_parts = []
    for sibling in h3.find_next_siblings():
        if sibling.name in ["h3", "h2"]: #h3 h2 만나면중단
            break
        
        text = sibling.get_text(separator=" ", strip=True)
        if text:
            answer_parts.append(text)
    
    answer = "\n".join(answer_parts)
    
    faq.append({
        "question": question,
        "answer": answer
    })


_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_THIS_DIR, "..", "backend", "Dataset", "faq_data.json")

with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(faq, f, ensure_ascii=False, indent=4)
