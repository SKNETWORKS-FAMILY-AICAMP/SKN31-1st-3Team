import requests
import math

# REST API 키를 여기에 직접 넣거나 secrets에서 가져옵니다.
REST_API_KEY = "f2a6679c91baa35c72a45f2e4d1205c4"

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