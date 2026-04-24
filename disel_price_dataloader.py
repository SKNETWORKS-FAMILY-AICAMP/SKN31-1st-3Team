from db.db_connect import get_connection
import pandas as pd
from datetime import datetime

# 엑셀 읽기
df = pd.read_excel(r"Dataset/경유_가격데이터.xlsx")

df.columns = ["date", "diesel_price"]

# 날짜 파싱
def parse_date(text):
    text = str(text).strip()
    text = text.replace("년", " ")
    text = text.replace("월", " ")
    text = text.replace("주", " ")
    l = text.split()
    return int(l[0]), int(l[1])   # year, month만 반환

# year, month 추출
df["year"], df["month"] = zip(*df["date"].apply(parse_date))

# date 생성 (YYYY-MM-01)
df["date"] = df.apply(
    lambda x: datetime(x["year"], x["month"], 1),
    axis=1
)

# 필요한 컬럼만
df = df[["date", "diesel_price"]]

# NaN 제거
df = df.dropna()

df = df.groupby("date").agg({
    "diesel_price": "mean",
}).reset_index()

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    INSERT INTO diesel_price (date, price)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
    price = VALUES(price)
    """
    
    data = [
        (
            row["date"],
            float(row["diesel_price"])
        )
        for _, row in df.iterrows()
    ]
    
    cursor.executemany(query, data)
    conn.commit()

except Exception as e:
    print(f"에러 발생: {e}")
    if conn:
        conn.rollback()

finally:
    if conn:
        cursor.close()
        conn.close()