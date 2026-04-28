import requests
import math
from dotenv import load_dotenv
import os

"""_summary_
1. get_coords_and_trans(address) 
>> 주소 인풋 주소 변환

2. get_distance(addr1, addr2) 
>> 출발지 - 도착지 거리 리턴

3. to_float(x)
>> 금액 문자열에 부동 소수점 변환 

4. calculate_costs(km, prices, eff)
>> 왕복 거리 & 유종별 비용 계산 
   
"""

# REST API 키를 여기에 직접 넣거나 secrets에서 가져옵니다.
load_dotenv()
REST_API_KEY = os.getenv("KAKAO_API")

def get_coords_and_trans(address):
    headers = {"Authorization": f"KakaoAK {REST_API_KEY}"}
    
    # 1. 주소 검색 (위경도 추출)
    addr_url = "https://dapi.kakao.com/v2/local/search/address.json"
    res = requests.get(addr_url, params={"query": address}, headers=headers).json()
    
    if not res['documents']:
        return None
    
    doc = res['documents'][0]
    x, y = doc['x'], doc['y'] # 경도, 위도

    # 2. WTM 좌표로 변환 (미터 단위 계산을 위해)
    trans_url = "https://dapi.kakao.com/v2/local/geo/transcoord.json"
    params = {"x": x, "y": y, "output_coord": "WTM"}
    trans_res = requests.get(trans_url, params=params, headers=headers).json()
    
    return trans_res['documents'][0]['x'], trans_res['documents'][0]['y']

def get_distance(addr1, addr2):
    # 두 지점의 WTM 좌표 가져오기
    p1 = get_coords_and_trans(addr1)
    p2 = get_coords_and_trans(addr2)
    
    if p1 and p2:
        # 피타고라스 거리 계산 (결과는 m 단위)
        dist = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        return dist / 1000  # km로 변환
    return None

def to_float(x):
    if isinstance(x, float) or isinstance(x, int):
        return float(x)
    x = str(x).replace(",", "").replace("원", "").strip()
    try:
        return float(x)
    except:
        return 0.0
    
def calculate_costs(km, prices, eff):
    round_trip_km = km * 2
    
    gas_daily = int((round_trip_km / eff['ice']) * to_float(prices['gas']))
    diesel_daily = int((round_trip_km / eff['ice']) * to_float(prices['diesel']))
    ev_daily = int((round_trip_km / eff['ev']) * to_float(prices['ev']))
    
    results = [
        {"유종": "⛽ 보통휘발유", "단가": f"{prices['gas']}원/L", "오늘의 왕복 비용": f"{gas_daily:,}원"},
        {"유종": "⛽ 자동차용경유", "단가": f"{prices['diesel']}원/L", "오늘의 왕복 비용": f"{diesel_daily:,}원"},
        {"유종": "⚡ 전기차(EV)", "단가": f"{prices['ev']}원/kWh", "오늘의 왕복 비용": f"{ev_daily:,}원 (절약! ✅)"}
    ]
    
    savings = gas_daily - ev_daily
    return round_trip_km, results, savings