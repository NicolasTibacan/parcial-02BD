# ...existing code...
import sqlite3
import pandas as pd
from sqlite3 import Connection
# ...existing code...

def load_data(conn: Connection, df: pd.DataFrame, table_name: str = "sentiments") -> None:
    """
    Guarda el DataFrame en la tabla SQLite (if_exists='append').
    Convierte la columna 'date' a ISO string si existe.
    """
    df_to_store = df.copy()

    if "date" in df_to_store.columns:
        # Normaliza a datetime y convierte a ISO; los valores inválidos quedan como None
        df_to_store["date"] = pd.to_datetime(df_to_store["date"], errors="coerce").apply(
            lambda x: x.isoformat() if not pd.isna(x) else None
        )

    try:
        df_to_store.to_sql(table_name, conn, if_exists="append", index=False)
    except Exception as e:
        # Re-levanta el error para que el llamador lo maneje (o cambiar por logging según convenga)
        raise
# ...existing code...