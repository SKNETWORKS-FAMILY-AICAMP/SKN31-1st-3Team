
from backend.db.db_connect import get_connection
import pandas as pd
def run():
    df = pd.read_excel(r"backend\Dataset\202512년_지역별_전기차_충전기_구축현황(누적).xls", header = 3)

    df.columns = [
        "month", "speed", "서울", "경기", "인천",
        "강원", "충청", "전라", "경상", "제주", "total"
    ]
    # 3. 합계 제거
    df = df.drop(columns=["total"])

    df_long = df.melt(
        id_vars=["month", "speed"],
        var_name="region",
        value_name="count"
    )

    #print(df_long)

    # NaN 제거 
    df_long = df_long.dropna()
    conn = None

    # DB 연결
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO ev_charger (month, speed, region, count)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        count = VALUES(count)
        """
        
        for _, row in df_long.iterrows():
            cursor.execute(query, (
            str(row["month"]),
            row["speed"],
            row["region"],
            int(row["count"])
        ))
        conn.commit()
            

    except Exception as e:
        print(f"에러 발생: {e}")
        if conn:
            conn.rollback() 
            
    finally:
        if conn:
            cursor.close() 
            conn.close() 


    df_long = df_long.dropna()

    # # ↓ 임시 디버그
    # print(f"변환 후 총 행 수: {len(df_long)}")
    # print("\n2025-12 데이터:")
    # print(df_long[df_long["month"] == "2025-12"])
    # print("\n2025-12 행 수:", len(df_long[df_long["month"] == "2025-12"]))

    # print("\nmonth 컬럼 타입:", df_long["month"].dtype)
    # print("month 샘플:", df_long["month"].head())

if __name__ == "__main__":
    run()