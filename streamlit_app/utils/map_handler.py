# streamlit_app/utils/ev_map.py
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_app.utils.db_handler import get_connection


"""_summary_
1. load_geojson()
>> geo 파일 읽고 반환 

2. merge_sidos_to_regions(geojson)
>> 17 to 8

3. filter_by_period(df, period="6month")
>> 사용자 선택 기간 필터링 (6개월 or 1년 가능)

4. aggregate_by_speed(df, speed="완속")
>> 충전 속도 기준으로 필터링 or 합산.

5. keep_complete_months_only(df)
>> 흰영역방지(모든 권역 데이터가 다 있는 시점만 남김)

6. add_growth_rate(df)
>> 처음 대비 누적 증가율(%) 컬럼 추가

7. prepare_map_data(df, period="6month", speed="완속", with_growth_rate=False)
>> db 데이터를 지도용으로 가공 

8. draw_choropleth
>> 시각화 그리는 코드 

   
"""

# =========================
# 상수
# =========================
GEOJSON_PATH = "backend/Dataset/skorea-provinces-2018-geo-simple.json"

SIDO_TO_REGION = {
    "서울특별시": "서울",
    "경기도": "경기",
    "인천광역시": "인천",
    "강원도": "강원",
    "충청북도": "충청",
    "충청남도": "충청",
    "대전광역시": "충청",
    "세종특별자치시": "충청",
    "전라북도": "전라",
    "전라남도": "전라",
    "광주광역시": "전라",
    "경상북도": "경상",
    "경상남도": "경상",
    "대구광역시": "경상",
    "울산광역시": "경상",
    "부산광역시": "경상",
    "제주특별자치도": "제주",
}


# =========================
# 캐싱 데이터 로드
# =========================
@st.cache_data
def get_charger_data_cached():
    """충전기 원본 데이터 로드"""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM ev_charger", conn)
    conn.close()
    return df


@st.cache_data
def get_map_geojson_cached():
    """GeoJSON 로드 + 권역 병합"""
    geojson = load_geojson()
    return merge_sidos_to_regions(geojson)


# =========================
# GeoJSON 처리
# =========================
def load_geojson():
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def merge_sidos_to_regions(geojson):
    """17개 시도 -> 8개 권역"""
    region_polygons = {}

    for feature in geojson["features"]:
        sido = feature["properties"]["name"]
        region = SIDO_TO_REGION.get(sido)

        if not region:
            continue

        region_polygons.setdefault(region, [])

        geom = feature["geometry"]

        if geom["type"] == "Polygon":
            region_polygons[region].append(geom["coordinates"])

        elif geom["type"] == "MultiPolygon":
            for coords in geom["coordinates"]:
                region_polygons[region].append(coords)

    features = []

    for region, polys in region_polygons.items():

        if len(polys) == 1:
            geometry = {
                "type": "Polygon",
                "coordinates": polys[0]
            }
        else:
            geometry = {
                "type": "MultiPolygon",
                "coordinates": polys
            }

        features.append({
            "type": "Feature",
            "properties": {"region": region},
            "geometry": geometry
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


# =========================
# 데이터 가공
# =========================
def filter_by_period(df, period="6month"):

    if period == "6month":
        return df[df["month"].str.endswith(("-06", "-12"))].copy()

    elif period == "year":
        return df[df["month"].str.endswith("-12")].copy()

    elif period == "all":
        return df.copy()

    raise ValueError("지원하지 않는 period")


def aggregate_by_speed(df, speed="완속"):

    if speed == "전체":
        return (
            df.groupby(["month", "region"], as_index=False)["count"]
            .sum()
        )

    return df[df["speed"] == speed][
        ["month", "region", "count"]
    ].copy()


def keep_complete_months_only(df):
    """모든 권역 데이터 존재하는 월만 유지"""
    monthly_region_count = df.groupby("month")["region"].nunique()
    expected = df["region"].nunique()

    complete_months = monthly_region_count[
        monthly_region_count == expected
    ].index

    return df[df["month"].isin(complete_months)].copy()


def add_growth_rate(df):
    """최초 시점 대비 누적 증가율"""
    df = df.copy()

    first_month = df["month"].min()

    base = (
        df[df["month"] == first_month]
        .set_index("region")["count"]
        .to_dict()
    )

    df["growth_rate"] = df.apply(
        lambda row:
        row["count"] / base[row["region"]] * 100
        if row["region"] in base else None,
        axis=1
    )

    return df.dropna(subset=["growth_rate"])


def prepare_map_data(
    df,
    period="6month",
    speed="완속",
    with_growth_rate=False
):
    df = filter_by_period(df, period)
    df = aggregate_by_speed(df, speed)
    df = keep_complete_months_only(df)

    df = (
        df.sort_values(["month", "region"])
        .reset_index(drop=True)
    )

    if with_growth_rate:
        df = add_growth_rate(df)

    return df


# =========================
# 시각화
# =========================
def draw_choropleth(
    df,
    geojson,
    animation_frame="month",
    color_column="count",
    color_scale="Blues",
    color_max=None,
    title=None
):

    hover_data = {
        "region": True,
        "count": ":,"
    }

    if "growth_rate" in df.columns:
        hover_data["growth_rate"] = ":.1f"

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="region",
        featureidkey="properties.region",
        color=color_column,
        animation_frame=animation_frame,
        range_color=[0, color_max],
        color_continuous_scale=color_scale,
        hover_data=hover_data,
        labels={
            "count": "충전기 수",
            "growth_rate": "증가율(%)",
            "region": "지역"
        },
        title=title
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        margin=dict(r=0, t=50, l=0, b=0),
        height=600
    )

    return fig


# =========================
# 외부 호출용 메인 함수
# =========================
def create_ev_map(speed, view_mode):

    df_raw = get_charger_data_cached()
    geojson = get_map_geojson_cached()

    is_growth = view_mode == "누적 증가율"

    df_map = prepare_map_data(
        df_raw,
        period="6month",
        speed=speed,
        with_growth_rate=is_growth
    )

    if is_growth:
        color_column = "growth_rate"
        color_max = df_map["growth_rate"].max()
        title = f"{speed} 충전기 누적 증가율"

    else:
        color_column = "count"
        color_max = df_map["count"].max()
        title = f"{speed} 충전기 보유 대수"

    return draw_choropleth(
        df_map,
        geojson,
        color_column=color_column,
        color_max=color_max,
        title=title
    )