import json
import pandas as pd
import plotly.express as px


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

#geojson 시도 파일 읽고 반환
def load_geojson():
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        return json.load(f)

# 17개 시도로 구성된 GeoJSON을 8개 권역 GeoJSON으로 합처줌
def merge_sidos_to_regions(geojson):
    region_polygons = {}
    
    for feature in geojson["features"]:
        sido_name = feature["properties"]["name"]
        region = SIDO_TO_REGION.get(sido_name)
        if region is None:
            continue
        
        if region not in region_polygons:
            region_polygons[region] = []
        
        geom = feature["geometry"]
        if geom["type"] == "Polygon":
            region_polygons[region].append(geom["coordinates"])
        elif geom["type"] == "MultiPolygon":
            for poly_coords in geom["coordinates"]:
                region_polygons[region].append(poly_coords)
    
    new_features = []
    for region, polys in region_polygons.items():
        if len(polys) == 1:
            geom = {"type": "Polygon", "coordinates": polys[0]}
        else:
            geom = {"type": "MultiPolygon", "coordinates": polys}
        
        new_features.append({
            "type": "Feature",
            "properties": {"region": region},
            "geometry": geom,
        })
    
    return {
        "type": "FeatureCollection",
        "features": new_features,
    }

# 데이터를 단위에 맞게 필터링
def filter_by_period(df, period="6month"):
    if period == "6month":
        return df[df["month"].str.endswith(("-06", "-12"))].copy()
    elif period == "year":
        return df[df["month"].str.endswith("-12")].copy()
    elif period == "all":
        return df.copy()
    else:
        raise ValueError(f"지원하지 않는 period: {period}")

# 충전 속도 기준으로 필터링 or 합산.
def aggregate_by_speed(df, speed="완속"):
    if speed == "전체":
        return df.groupby(["month", "region"], as_index=False)["count"].sum()
    else:
        return df[df["speed"] == speed][["month", "region", "count"]].copy()

# 흰영역방지(모든 권역 데이터가 다 있는 시점만 남김)
def keep_complete_months_only(df):
    region_counts_per_month = df.groupby("month")["region"].nunique()
    expected = df["region"].nunique()
    complete_months = region_counts_per_month[
        region_counts_per_month == expected
    ].index
    return df[df["month"].isin(complete_months)].copy()

# 처음 대비 누적 증가율(%) 컬럼 추가
def add_growth_rate(df):
    df = df.copy()
    
    first_month = df["month"].min()
    base = (
        df[df["month"] == first_month]
        .set_index("region")["count"]
        .to_dict()
    )
    
    df["growth_rate"] = df.apply(
        lambda row: row["count"] / base[row["region"]] * 100
        if row["region"] in base else None,
        axis=1,
    )
    
    df = df.dropna(subset=["growth_rate"])
    return df

# DB 원본 데이터를 지도용으로 가공한다.
def prepare_map_data(df, period="6month", speed="완속", with_growth_rate=False):
    df = filter_by_period(df, period)
    df = aggregate_by_speed(df, speed)
    df = keep_complete_months_only(df)
    df = df.sort_values(["month", "region"]).reset_index(drop=True)
    
    if with_growth_rate:
        df = add_growth_rate(df)
    
    return df


def draw_choropleth(
    df,
    geojson,
    animation_frame=None,
    color_max=None,
    title=None,
    color_column="count",
    color_scale="Blues",
):

    range_color = [0, color_max] if color_max is not None else None
    
    hover_data = {"region": True, "count": ":,"}
    if "growth_rate" in df.columns:
        hover_data["growth_rate"] = ":.1f"
    
    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="region",
        featureidkey="properties.region",
        color=color_column,
        animation_frame=animation_frame,
        range_color=range_color,
        color_continuous_scale=color_scale,
        hover_data=hover_data,
        labels={
            "count": "충전기 수",
            "growth_rate": "증가율(%)",
            "region": "지역",
        },
        title=title,
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        height=600,
    )
    
    return fig