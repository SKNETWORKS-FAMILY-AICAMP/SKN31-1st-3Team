import sys
import os
import pandas as pd

# 프로젝트 루트 경로를 sys.path에 추가 (backend를 찾기 위함)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.db.db_connect import get_connection

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