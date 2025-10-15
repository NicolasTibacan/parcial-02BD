from Confing.Confing import get_engine, init_db
from Extract.Extract import extract_data
from Transform.Transform import transform_data
from load.Load import load_data
from Analist.Graficas import generate_all_plots


def run_pipeline(csv_path: str = "stock_senti_analysis.csv"):
    # Inicializar Engine (SQLAlchemy)
    engine = get_engine()
    init_db(engine)

    try:
        # Extract
        df = extract_data(csv_path)

        # Transform
        df_clean = transform_data(df)

        # Load (pasa el engine)
        load_data(engine, df_clean)

        # Analisis / Graficas
        generate_all_plots(df_clean)
    finally:
        # no hace falta cerrar Engine explícitamente; si usas get_sqlite_connection() sí habría que cerrarla
        pass

if __name__ == "__main__":
    run_pipeline()
