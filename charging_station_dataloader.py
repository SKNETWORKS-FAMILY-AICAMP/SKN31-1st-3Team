
from db.db_connect import get_connection
import pandas as pd

df = pd.read_excel(r"Dataset\202512년_지역별_전기차_충전기_구축현황(누적).xls", header = 4)

df.columns = [
    "month", "speed", "서울", "경기", "인천",
    "강원", "춘천", "전라", "경상", "제주", "total"
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