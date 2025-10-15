import pandas as pd
from io import StringIO
from typing import List


def _combine_top_columns(df: pd.DataFrame) -> pd.Series:
    # Busca columnas tipo Top1, Top2, ... (case-insensitive) y concatena su contenido por fila
    top_cols = [c for c in df.columns if c.lower().startswith("top")]
    if not top_cols:
        return pd.Series([""] * len(df), index=df.index)
    parts = df[top_cols].astype(str).replace("nan", "").fillna("")
    combined = parts.apply(lambda row: " ".join([p.strip() for p in row if p and p.strip()]), axis=1)
    return combined


def extract_data(csv_path: str) -> pd.DataFrame:
    """
    Carga el CSV intentando varios encodings y estrategias de parsing.
    Devuelve un DataFrame con al menos: 'date' (si existe), 'label' (si existe) y 'text_original'.
    """
    encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=enc, low_memory=False)
            break
        except UnicodeDecodeError:
            continue
        except pd.errors.ParserError:
            try:
                df = pd.read_csv(csv_path, encoding=enc, engine="python", on_bad_lines="skip")
                break
            except Exception:
                continue
        except Exception:
            continue

    if df is None:
        # Último recurso: leer binario y decodificar reemplazando bytes inválidos
        with open(csv_path, "rb") as f:
            raw = f.read().decode("utf-8", errors="replace")
        df = pd.read_csv(StringIO(raw))

    # Normalizar nombres de columnas (mapa lower->original)
    cols_map = {c.lower(): c for c in df.columns}
    mapping = {}
    if "date" in cols_map:
        mapping[cols_map["date"]] = "date"
    elif "day" in cols_map:
        mapping[cols_map["day"]] = "date"

    if "text" in cols_map:
        mapping[cols_map["text"]] = "text"
    elif "sentence" in cols_map:
        mapping[cols_map["sentence"]] = "text"

    if "label" in cols_map:
        mapping[cols_map["label"]] = "label"
    if "sentiment_score" in cols_map:
        mapping[cols_map["sentiment_score"]] = "sentiment_score"
    elif "score" in cols_map:
        mapping[cols_map["score"]] = "sentiment_score"

    df = df.rename(columns=mapping)

    # Crear text_original: si ya existe 'text' usarla, sino combinar Top* o columnas restantes de texto
    if "text" in df.columns and df["text"].notna().any():
        df["text_original"] = df["text"].astype(str)
    else:
        df["text_original"] = _combine_top_columns(df)

    # Normalizar valores vacíos a NA
    df["text_original"] = df["text_original"].replace("", pd.NA)

    return df