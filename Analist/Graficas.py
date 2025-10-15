# ...existing code...
import os
import re
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ...existing code...
PLOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Paleta y estilo agradable
plt.style.use("seaborn-v0_8-darkgrid")
PALETTE = {
    "positive": "#2ca02c",
    "neutral": "#7f7f7f",
    "negative": "#d62728",
    "other": "#1f77b4",
}

# ...existing code...
def _save_plot(fig, name: str):
    path = os.path.join(PLOTS_DIR, name)
    try:
        fig.tight_layout()
    except Exception:
        fig.subplots_adjust(left=0.12, right=0.95, top=0.94, bottom=0.08)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.06, dpi=150)
    plt.close(fig)

def _adjust_left_for_labels(fig, labels):
    if not labels:
        return
    max_len = max((len(str(l)) for l in labels))
    left = min(0.08 + max_len * 0.0065, 0.45)
    fig.subplots_adjust(left=left, right=0.95, top=0.95, bottom=0.08)

# ...existing code...
def plot_sentiment_over_time(df: pd.DataFrame):
    # ...existing code...
    pass

def plot_top_phrases(df: pd.DataFrame, top_n: int = 15):
    # ...existing code...
    pass

# ...existing code...
def plot_sentiment_pie(df: pd.DataFrame):
    # ...existing code...
    pass

def plot_score_distribution(df: pd.DataFrame):
    # ...existing code...
    pass

def plot_ticker_counts(df: pd.DataFrame, top_n: int = 12):
    # ...existing code...
    pass

# ---------- Nuevas gráficas añadidas ----------

def plot_sentiment_area(df: pd.DataFrame):
    """
    Área apilada de proporciones por sentimiento a lo largo del tiempo.
    Buena para ver cambios relativos y balance general.
    """
    if df is None or df.empty or "sentiment_label" not in df.columns or "date" not in df.columns:
        return

    tmp = df.copy()
    tmp["date_only"] = pd.to_datetime(tmp["date"], errors="coerce").dt.date
    tmp = tmp.dropna(subset=["date_only"])
    if tmp.empty:
        return

    counts = tmp.groupby(["date_only", "sentiment_label"]).size().unstack(fill_value=0)
    for c in ("positive", "neutral", "negative"):
        if c not in counts.columns:
            counts[c] = 0
    counts = counts[["positive", "neutral", "negative"]]
    props = counts.div(counts.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)

    dates = pd.to_datetime(props.index)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.stackplot(dates,
                 props["positive"].values,
                 props["neutral"].values,
                 props["negative"].values,
                 labels=["positive", "neutral", "negative"],
                 colors=[PALETTE["positive"], PALETTE["neutral"], PALETTE["negative"]],
                 alpha=0.85)
    ax.set_title("Area apilada: proporción diaria de sentimientos")
    ax.set_ylabel("Proporción")
    ax.set_xlabel("Fecha")
    ax.set_ylim(0, 1)
    ax.legend(loc="upper left", title="Sentimiento")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    fig.autofmt_xdate(rotation=30)
    _save_plot(fig, "sentiment_area.png")


def plot_sentiment_by_weekday(df: pd.DataFrame):
    """
    Heatmap (matriz) de proporciones de sentimiento por día de la semana.
    Muy útil para detectar patrones diarios (ej. más negativos los lunes).
    """
    if df is None or df.empty or "sentiment_label" not in df.columns or "date" not in df.columns:
        return

    tmp = df.copy()
    tmp["date_only"] = pd.to_datetime(tmp["date"], errors="coerce").dt.date
    tmp = tmp.dropna(subset=["date_only"])
    if tmp.empty:
        return

    tmp["weekday"] = pd.to_datetime(tmp["date_only"]).dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    counts = tmp.groupby(["weekday", "sentiment_label"]).size().unstack(fill_value=0)
    # asegurar columnas estándar
    for c in ("positive", "neutral", "negative"):
        if c not in counts.columns:
            counts[c] = 0
    counts = counts[["positive", "neutral", "negative"]]

    # convertir a proporciones por fila (weekday)
    props = counts.div(counts.sum(axis=1).replace(0, np.nan), axis=0).reindex(order).fillna(0)

    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(props.values, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    ax.set_yticks(range(len(props.index)))
    ax.set_yticklabels(props.index)
    ax.set_xticks(range(len(props.columns)))
    ax.set_xticklabels(props.columns)
    ax.set_title("Proporción de sentimientos por día de la semana")
    # mostrar valores en cada celda
    for i in range(props.shape[0]):
        for j in range(props.shape[1]):
            val = props.values[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8, color="black")
    cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.04)
    cbar.set_label("Proporción")
    _save_plot(fig, "sentiment_weekday_heatmap.png")

# ---------- Fin nuevas gráficas ----------

def generate_all_plots(df: pd.DataFrame):
    # mantener orden legible y añadir las dos nuevas
    plot_sentiment_over_time(df)
    plot_sentiment_area(df)                # nueva
    plot_sentiment_pie(df)
    plot_top_phrases(df)
    plot_top_phrases(df)                   # si quieres otra variante, cámbialo aquí
    plot_score_distribution(df)
    plot_ticker_counts(df)
    plot_sentiment_by_weekday(df)           # nueva
# ...existing code...