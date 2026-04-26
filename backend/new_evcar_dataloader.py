from backend.db.db_connect import get_connection
import pandas as pd
 
df = pd.read_excel(r"backend\Dataset/연도별_전기차_신규등록_대수.xlsx", header=0)
df.columns = ['year', 'car', 'ev_car']
 
# car 컬럼 NaN 처리
df['car'] = df['car'].where(df['car'].notna(), None)
 
try:
    conn = get_connection()
    cursor = conn.cursor()
 
    for _, row in df.iterrows():
        car_val = None if pd.isna(row['car']) else int(row['car'])
        cursor.execute(
            "INSERT INTO ev_registration_by_year (year, car, ev_car) VALUES (%s, %s, %s)",
            (int(row['year']), car_val, int(row['ev_car'])))
 
    conn.commit()
 
except Exception as e:
    conn.rollback()
    print(f"오류 발생: {e}")
 
finally:
    cursor.close()
    conn.close()