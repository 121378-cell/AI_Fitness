import os
from datetime import datetime

import pandas as pd
import streamlit as st

from src.database import table_to_dataframe

st.set_page_config(page_title="AI Fitness Dashboard", layout="wide")

SAVE_PATH = os.getenv("SAVE_PATH", os.getcwd())
GARMIN_STATS_FILE = os.path.join(SAVE_PATH, "garmin_stats.csv")
GARMIN_ACTIVITIES_FILE = os.path.join(SAVE_PATH, "garmin_activities.csv")
GARMIN_RUNS_FILE = os.path.join(SAVE_PATH, "garmin_runs.csv")


def load_table_or_csv(table_name: str, csv_path: str) -> pd.DataFrame:
    try:
        df = table_to_dataframe(table_name)
        if df.empty and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
    except Exception:
        df = pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame()
    return df


def load_garmin_stats() -> pd.DataFrame:
    df = load_table_or_csv("garmin_stats", GARMIN_STATS_FILE)
    if df.empty:
        return df
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date")
    return df


def load_garmin_activities() -> pd.DataFrame:
    df = load_table_or_csv("garmin_activities", GARMIN_ACTIVITIES_FILE)
    if df.empty:
        return df
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date")
    return df


def load_garmin_runs() -> pd.DataFrame:
    df = load_table_or_csv("garmin_runs", GARMIN_RUNS_FILE)
    if df.empty:
        return df
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date")
    return df


st.title("AI Fitness Dashboard")
st.caption("Dashboard de salud y actividad basado en Garmin + SQLite/CSV fallback")

stats_df = load_garmin_stats()
act_df = load_garmin_activities()
runs_df = load_garmin_runs()

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Registros de salud", int(len(stats_df)))
with c2:
    st.metric("Actividades", int(len(act_df)))
with c3:
    st.metric("Carreras", int(len(runs_df)))

if not stats_df.empty:
    st.subheader("Tendencias de salud")
    numeric_cols = [c for c in ["Steps", "RHR", "Weight (lbs)", "Sleep Score"] if c in stats_df.columns]
    for col in numeric_cols:
        st.line_chart(stats_df.set_index("Date")[[col]])
else:
    st.warning("No hay datos de Garmin Health disponibles.")

if not act_df.empty:
    st.subheader("Actividades recientes")
    cols = [c for c in ["Date", "activityName", "sportType", "distance"] if c in act_df.columns]
    st.dataframe(act_df[cols].tail(100), use_container_width=True)

if not runs_df.empty:
    st.subheader("Carreras recientes")
    cols = [c for c in ["Date", "activityName", "distance", "averageSpeed", "averageHR"] if c in runs_df.columns]
    st.dataframe(runs_df[cols].tail(100), use_container_width=True)

st.divider()
st.caption(f"Última actualización dashboard: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
