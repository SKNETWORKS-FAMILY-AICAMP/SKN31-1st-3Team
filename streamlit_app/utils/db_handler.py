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