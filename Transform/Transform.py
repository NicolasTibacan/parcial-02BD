import pandas as pd
import re
from typing import Optional

def clean_text(s: Optional[object]) -> str:
    """Limpia una cadena: elimina URLs, menciones, puntuación extra y espacios repetidos."""
    if pd.isna(s):
        return ""
    s = str(s)
    s = re.sub(r"http\S+", "", s)
    s = re.sub(r"@\w+", "", s)
    s = re.sub(r"[^\w\s\'\"]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def infer_label_from_score(score) -> str:
    """Inferir etiqueta a partir de un score numérico; valores no numéricos → 'neutral'."""
    try:
        if pd.isna(score):
            return "neutral"
        sc = float(score)
    except Exception:
        return "neutral"
    if sc > 0.2:
        return "positive"
    if sc < -0.2:
        return "negative"
    return "neutral"

def map_label_value(label) -> str:
    """Mapea label binario o textual a etiquetas estándar."""
    if pd.isna(label):
        return "neutral"
    try:
        # si es 1/0 numérico o string convertible
        n = float(label)
        if n == 1:
            return "positive"
        if n == 0:
            return "negative"
    except Exception:
        pass
    # si es texto ya descriptivo
    txt = str(label).strip().lower()
    if txt in ("positive", "pos", "positivo", "positiva"):
        return "positive"
    if txt in ("negative", "neg", "negativo", "negativa"):
        return "negative"
    return "neutral"

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma el DataFrame y devuelve columnas:
    ['date','ticker','text_original','cleaned_text','sentiment_label','sentiment_score']
    """
    df = df.copy()

    # date -> datetime coercion
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # text_original: usarla si existe, sino intentar 'text' o 'sentence'
    if "text_original" in df.columns:
        df["text_original"] = df["text_original"].astype(str)
    elif "text" in df.columns:
        df["text_original"] = df["text"].astype(str)
    elif "sentence" in df.columns:
        df["text_original"] = df["sentence"].astype(str)
    else:
        df["text_original"] = ""

    # ticker: si no existe, crear nulos
    if "ticker" not in df.columns:
        df["ticker"] = None

    # cleaned_text
    df["cleaned_text"] = df["text_original"].apply(clean_text)

    # sentiment_score / sentiment_label
    if "sentiment_score" in df.columns:
        df["sentiment_score"] = pd.to_numeric(df["sentiment_score"], errors="coerce")
        df["sentiment_label"] = df["sentiment_score"].apply(infer_label_from_score)
    else:
        if "label" in df.columns:
            df["sentiment_label"] = df["label"].apply(map_label_value)
            df["sentiment_score"] = pd.NA
        else:
            df["sentiment_label"] = "neutral"
            df["sentiment_score"] = pd.NA

    # Seleccionar columnas que espera la BD
    needed = ["date", "ticker", "text_original", "cleaned_text", "sentiment_label", "sentiment_score"]
    out = df.reindex(columns=[c for c in needed if c in df.columns])

    # Eliminar duplicados basados en text_original y filas con cleaned_text vacío
    if "text_original" in out.columns:
        out = out.drop_duplicates(subset=["text_original"]).copy()
    else:
        out = out.drop_duplicates().copy()

    if "cleaned_text" in out.columns:
        out = out[out["cleaned_text"].str.len() > 0]

    out = out.reset_index(drop=True)
    return out
# ...existing code...