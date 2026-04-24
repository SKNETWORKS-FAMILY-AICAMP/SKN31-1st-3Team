from backend.db.db_connect import get_connection
import pandas as pd

df = pd.read_csv(r"backend\Dataset\자동차등록대수현황_2015~2025.csv", encoding='cp949', header=45)
#print(df)

df.columns = ['type', 'year', 'total', 'official', 'private', 'business']

df_total = df[['year', 'total']]
#print(df_total)

df_total['total'] = pd.to_numeric(df_total['total'], errors='coerce')
df_total = df_total.dropna()

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    data = list(df_total.itertuples(index=False, name=None))
    
    sql = """
    INSERT INTO car_total (year, total)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
    total = VALUES(total)
    """
    cursor.executemany(sql, data)
    conn.commit()
except Exception as e:
    print(f"에러 발생: {e}")
    if conn:
        conn.rollback() 
        
finally:
    if conn:
        cursor.close() 
        conn.close() 