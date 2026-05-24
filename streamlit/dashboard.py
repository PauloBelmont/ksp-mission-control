import os
import time
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000/telemetry")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))
RETRY_INTERVAL = float(os.getenv("RETRY_INTERVAL", "5.0"))

st.set_page_config(page_title="KSP Mission Control", layout="wide")
st.title("🚀 KSP Mission Control")

# --- History preserved across reruns ---
if "history" not in st.session_state:
    st.session_state.history = {
        "altitude": [],
        "velocity": [],
    }

# --- Fetch telemetry ---
data = None
error = None

try:
    resp = requests.get(API_URL, timeout=2.0)
    if resp.status_code == 200:
        data = resp.json()
    else:
        error = f"kRPC unavailable (status {resp.status_code})"
except Exception:
    error = "Could not reach API"

# --- Connection error state ---
if error:
    st.error(error)
    st.info("Waiting for KSP and kRPC to be ready...")
    if st.button("🔄 Retry now"):
        st.rerun()
    time.sleep(RETRY_INTERVAL)
    st.rerun()

# --- Dashboard ---
st.success("Connected to KSP via kRPC")

metrics = st.columns(5)
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

st.line_chart({
    "Altitude": st.session_state.history["altitude"],
    "Velocity": st.session_state.history["velocity"],
})

time.sleep(POLL_INTERVAL)
st.rerun()
