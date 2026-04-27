import pandas as pd
from streamlit_app.utils.db_handler import get_connection

def run():
    df = pd.read_excel(r"backend\Dataset\합친_전기데이터.xlsx")

    df.columns = ["년월", "시도", "시군구", "용도", "고객수", "판매량", "판매수입"]

    df["년월"] = pd.to_datetime(df["년월"]).dt.to_period("M").dt.to_timestamp()

    df["판매량"] = pd.to_numeric(df["판매량"], errors="coerce")
    df["판매수입"] = pd.to_numeric(df["판매수입"], errors="coerce")

    df = df.dropna(subset=["판매량", "판매수입"])
    df = df[df["판매량"] > 0]

    df["price"] = df["판매수입"] / df["판매량"]
    df.loc[df["price"] <= 100, "price"] = 150

    result = df.groupby("년월")["price"].mean().reset_index()

    result = result.sort_values("년월")


    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO e_price (date, price)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
        price = VALUES(price)
        """
        
        data = [
            (
                row["년월"],
                float(row["price"])
            )
            for _, row in result.iterrows()
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

if __name__ == "__main__":
    run()