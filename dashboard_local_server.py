import os
import subprocess
import time
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from src.database import table_to_dataframe

load_dotenv()

SAVE_PATH = os.getenv("SAVE_PATH", os.getcwd())
PROJECT_DIR = os.getenv("PROJECT_DIR", os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.getenv("LOG_FILE", "/home/pi/cron_log.txt")

GARMIN_STATS_FILE = os.path.join(SAVE_PATH, "garmin_stats.csv")
GARMIN_ACTIVITIES_FILE = os.path.join(SAVE_PATH, "garmin_activities.csv")

TRACKED_FILES = {
    "Garmin Health": {
        "path": GARMIN_STATS_FILE,
        "command": f"cd {PROJECT_DIR} && /usr/bin/python3 daily_garmin_health.py >> {LOG_FILE} 2>&1",
    },
    "Garmin Activities": {
        "path": GARMIN_ACTIVITIES_FILE,
        "command": f"cd {PROJECT_DIR} && /usr/bin/python3 daily_garmin_activities.py >> {LOG_FILE} 2>&1",
    },
    "Garmin Yesterday": {
        "path": GARMIN_STATS_FILE,
        "command": f"cd {PROJECT_DIR} && /usr/bin/python3 update_yesterday_garmin.py >> {LOG_FILE} 2>&1",
    },
}


@st.cache_data(ttl=300)
def load_garmin_data():
    df = table_to_dataframe("garmin_stats")
    if df.empty and os.path.exists(GARMIN_STATS_FILE):
        df = pd.read_csv(GARMIN_STATS_FILE)
    if df.empty:
        return None
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", format="mixed")
    return df.dropna(subset=["Date"]).sort_values("Date")


@st.cache_data(ttl=300)
def load_activities_data():
    df = table_to_dataframe("garmin_activities")
    if df.empty and os.path.exists(GARMIN_ACTIVITIES_FILE):
        df = pd.read_csv(GARMIN_ACTIVITIES_FILE)
    if df.empty:
        return None
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", format="mixed")
    return df.dropna(subset=["Date"]).sort_values("Date")


def status_for(path: str):
    if os.path.exists(path):
        dt = datetime.fromtimestamp(os.path.getmtime(path))
        age = datetime.now() - dt
        if age < timedelta(hours=2):
            return f"✅ {dt:%Y-%m-%d %H:%M}", "ok"
        return f"⚠️ {dt:%Y-%m-%d %H:%M}", "stale"
    return "❌ missing", "missing"


st.set_page_config(page_title="AI Fitness Dashboard", layout="wide")
st.title("AI Fitness Dashboard (Garmin-only)")
st.caption("Dashboard operativo para datos Garmin y estado del sistema.")

start = st.sidebar.date_input("Start", datetime.now().date() - timedelta(days=30))
end = st.sidebar.date_input("End", datetime.now().date())

if start > end:
    st.error("Start date must be before end date")
    st.stop()

start_dt = pd.to_datetime(start)
end_dt = pd.to_datetime(end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

tab1, tab2, tab3 = st.tabs(["Recovery", "Activities", "System"])

with tab1:
    garmin = load_garmin_data()
    if garmin is None:
        st.warning("No Garmin health data available.")
    else:
        filtered = garmin[(garmin["Date"] >= start_dt) & (garmin["Date"] <= end_dt)].copy()
        if filtered.empty:
            st.info("No data for selected range.")
        else:
            cols = st.columns(3)
            cols[0].metric("Avg Steps", f"{filtered.get('Steps', pd.Series(dtype=float)).fillna(0).mean():,.0f}")
            cols[1].metric("Avg RHR", f"{filtered.get('RHR', pd.Series(dtype=float)).fillna(0).mean():.1f}")
            cols[2].metric("Avg Sleep", f"{filtered.get('Sleep Score', pd.Series(dtype=float)).fillna(0).mean():.1f}")

            if "Steps" in filtered.columns:
                fig = px.line(filtered, x="Date", y="Steps", title="Daily Steps")
                st.plotly_chart(fig, use_container_width=True)
            if "RHR" in filtered.columns:
                fig = px.line(filtered, x="Date", y="RHR", title="Resting Heart Rate")
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    acts = load_activities_data()
    if acts is None:
        st.warning("No Garmin activities data available.")
    else:
        filtered = acts[(acts["Date"] >= start_dt) & (acts["Date"] <= end_dt)].copy()
        if filtered.empty:
            st.info("No activities for selected range.")
        else:
            if "sportType" in filtered.columns:
                sport_counts = filtered["sportType"].fillna("Unknown").value_counts().reset_index()
                sport_counts.columns = ["sportType", "count"]
                fig = px.bar(sport_counts, x="sportType", y="count", title="Activities by Sport")
                st.plotly_chart(fig, use_container_width=True)
            if "distance" in filtered.columns:
                filtered["distance"] = pd.to_numeric(filtered["distance"], errors="coerce").fillna(0)
                daily = filtered.groupby(filtered["Date"].dt.date)["distance"].sum().reset_index()
                fig = px.line(daily, x="Date", y="distance", title="Daily Distance")
                st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Mission Status")
    for name, cfg in TRACKED_FILES.items():
        last, _ = status_for(cfg["path"])
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.write(name)
        c2.write(last)
        if c3.button("Run", key=f"run_{name}"):
            subprocess.Popen(cfg["command"], shell=True)
            st.toast(f"Started: {name}")
            time.sleep(0.2)
            st.rerun()

    st.markdown("---")
    st.subheader("History Import")
    history_start = st.date_input("History start", value=datetime.now().date() - timedelta(days=365), key="history_start")
    force = st.checkbox("Force Refresh", value=False)
    force_flag = " --force" if force else ""
    d = history_start.isoformat()

    c1, c2, c3 = st.columns(3)
    if c1.button("Import Garmin Health"):
        subprocess.Popen(f"cd {PROJECT_DIR} && /usr/bin/python3 history_garmin_import.py {d}{force_flag} >> {LOG_FILE} 2>&1", shell=True)
        st.success("Garmin Health import started")
    if c2.button("Import Garmin Activities"):
        subprocess.Popen(f"cd {PROJECT_DIR} && /usr/bin/python3 history_garmin_activities.py {d}{force_flag} >> {LOG_FILE} 2>&1", shell=True)
        st.success("Garmin Activities import started")
    if c3.button("Run All Imports"):
        subprocess.Popen(f"cd {PROJECT_DIR} && /usr/bin/python3 history_garmin_import.py {d}{force_flag} >> {LOG_FILE} 2>&1", shell=True)
        subprocess.Popen(f"cd {PROJECT_DIR} && /usr/bin/python3 history_garmin_activities.py {d}{force_flag} >> {LOG_FILE} 2>&1", shell=True)
        st.success("All imports started")
