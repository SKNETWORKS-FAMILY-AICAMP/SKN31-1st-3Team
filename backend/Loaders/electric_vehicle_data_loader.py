from streamlit_app.utils.db_handler import get_connection
import pandas as pd

def run():
    df = pd.read_excel(r"backend\Dataset\201504_202604_전기차등록현황.xls", header=3)
    df = df.drop(columns=['합계'])

    df_long = df.melt(
        id_vars=['년월'],
        var_name='region',
        value_name='count'
    )

    df_long.columns = ['year', 'region', 'count']

    #  year 분리
    df_long[['year', 'month']] = df_long['year'].str.split('-', expand=True)
    df_long['year'] = df_long['year'].astype(int)
    df_long['month'] = df_long['month'].astype(int)

    #  count 정리
    df_long['count'] = pd.to_numeric(df_long['count'], errors='coerce')
    df_long = df_long.dropna(subset=['count'])
    df_long['count'] = df_long['count'].astype(int)

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        data = list(df_long[['year', 'month', 'region', 'count']].itertuples(index=False, name=None))
        
        sql = """
        INSERT INTO electric_vehicle_count (year, month, region, count)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        count = VALUES(count);
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

if __name__ == "__main__":
    run()