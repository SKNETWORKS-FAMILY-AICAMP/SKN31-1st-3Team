import sys
import os
import pandas as pd
import pymysql
from dotenv import load_dotenv
import os



load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        charset='utf8mb4',
        use_unicode=True
    )



def get_data_from_db(query):
    conn = None
    try:
        conn = get_connection()
        # pandas의 read_sql을 사용하면 쿼리 결과가 바로 데이터프레임이 됩니다.
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"❌ DB 호출 중 오류 발생: {e}")
        return pd.DataFrame() # 에러 발생 시 빈 데이터프레임 반환
    finally:
        if conn:
            conn.close()

def get_share_data_processed():
    """점유율 관련 데이터 로드 및 전처리"""
    # 데이터 로드
    rdf = pd.DataFrame(get_data_from_db("select * from ev_registration_by_year"))
    car = pd.DataFrame(get_data_from_db("select * from car_total"))
    evcar = pd.DataFrame(get_data_from_db("select * from electric_vehicle_count"))

    # 1. 연도 라벨링 (2026 -> 2026.03)
    rdf['year_label'] = rdf['year'].astype(str).str.replace('2026', '2026.03', regex=False)

    # 2. 누적 비중 계산 로직
    ev_last = evcar.loc[evcar.groupby('year')['month'].idxmax()]
    ev_yearly = ev_last.groupby('year')['count'].sum().reset_index()
    ev_yearly.columns = ['year', 'ev_total']

    car_yearly = car[['year', 'total']].copy()
    car_yearly.columns = ['year', 'car_total']
    car_yearly['year'] = car_yearly['year'].astype(int)

    df_ratio = pd.merge(ev_yearly, car_yearly, on='year')
    df_ratio['ev_ratio'] = (df_ratio['ev_total'] / df_ratio['car_total'] * 100).round(2)

    return rdf, df_ratio            
            
def get_fuel_data_processed():

    TANK_GAS = 50
    TANK_DIESEL = 55
    BATTERY = 60

    query = """
    SELECT
        f.date,
        f.regular_price,
        f.premium_price,
        d.price AS diesel_price,
        e.price AS electric_price
    FROM fuel_price f
    LEFT JOIN diesel_price d
        ON f.date = d.date
    JOIN e_price e
        ON f.date = e.date
    ORDER BY f.date;
    """

    df = get_data_from_db(query)

    if df.empty:
        return df, df

    df_calc = df.copy()
    df_calc["regular_gas_full"] = df_calc["regular_price"] * TANK_GAS
    df_calc["premium_gas_full"] = df_calc["premium_price"] * TANK_GAS
    df_calc["diesel_full"] = df_calc["diesel_price"] * TANK_DIESEL
    df_calc["electric_full"] = df_calc["electric_price"] * BATTERY

    return df, df_calc