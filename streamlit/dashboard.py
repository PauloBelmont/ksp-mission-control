import os
import time
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000/telemetry")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))

st.set_page_config(page_title="KSP Mission Control", layout="wide")
st.title("🚀 KSP Mission Control")

# History is preserved across reruns via session_state
if "history" not in st.session_state:
    st.session_state.history = {
        "altitude": [],
        "velocity": [],
    }

status_placeholder = st.empty()
metrics = st.columns(5)
chart_placeholder = st.empty()

try:
    resp = requests.get(API_URL, timeout=2.0)
    if resp.status_code == 200:
        data = resp.json()
        status_placeholder.success("Connected to API")

        metrics[0].metric("Altitude (m)", f"{data.get('altitude', 0):.2f}")
        metrics[1].metric("Velocity (m/s)", f"{data.get('velocity', 0):.2f}")
        metrics[2].metric("Apoapsis (m)", f"{data.get('apoapsis', 0):.2f}")
        metrics[3].metric("Periapsis (m)", f"{data.get('periapsis', 0):.2f}")
        metrics[4].metric("Fuel", f"{data.get('fuel', 0):.2f}")

        st.session_state.history["altitude"].append(data.get("altitude", 0))
        st.session_state.history["velocity"].append(data.get("velocity", 0))

        # Keep only the last 120 data points
        max_len = 120
        for k in st.session_state.history:
            if len(st.session_state.history[k]) > max_len:
                st.session_state.history[k] = st.session_state.history[k][-max_len:]

        chart_placeholder.line_chart({
            "Altitude": st.session_state.history["altitude"],
            "Velocity": st.session_state.history["velocity"],
        })
    else:
        status_placeholder.error(f"API returned {resp.status_code}: {resp.text}")
except Exception as e:
    status_placeholder.error(f"Could not reach API: {e}")

time.sleep(POLL_INTERVAL)
st.rerun()
