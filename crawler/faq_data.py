import requests
from bs4 import BeautifulSoup
import pandas as pd
import json




url = "https://www.pse.com/ko/pages/electric-cars/electric-vehicles-faq"
data = requests.get(url)
soup = BeautifulSoup(data.text, "lxml")

titles = soup.select('div.row.help-container div.topic-wrapper div.panel.panel-default div.title-collapse p')
answers = soup.select('div.row.help-container div.topic-wrapper div.panel.panel-default div.panel-collapse p')

t=[]
a=[]
faq = []
for title in titles:
    text = title.text.strip()
    if text:
        t.append(text)

for answer in answers:
    text = answer.text.strip()
    if text:
        a.append(text)

faq = {a:b for a, b in zip(t,a)}


with open("./data.json","w",encoding='utf-8') as f:
    json.dump(faq, f, ensure_ascii = False, indent=4)