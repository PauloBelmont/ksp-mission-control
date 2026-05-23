import os
import time
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000/telemetry")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))

st.set_page_config(page_title="KSP Dashboard", layout="wide")
st.title("🚀 KSP Streamlit Dashboard")

status_placeholder = st.empty()
metrics = st.columns(5)
chart_placeholder = st.empty()

history = {
    "time": [],
    "altitude": [],
    "velocity": [],
}

while True:
    try:
        resp = requests.get(API_URL, timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            status_placeholder.success("Conectado ao API")

            metrics[0].metric("Altitude (m)", f"{data.get('altitude', 0):.2f}")
            metrics[1].metric("Velocity (m/s)", f"{data.get('velocity', 0):.2f}")
            metrics[2].metric("Apoapsis (m)", f"{data.get('apoapsis', 0):.2f}")
            metrics[3].metric("Periapsis (m)", f"{data.get('periapsis', 0):.2f}")
            metrics[4].metric("Fuel", f"{data.get('fuel', 0):.2f}")

            history["time"].append(time.time())
            history["altitude"].append(data.get("altitude", 0))
            history["velocity"].append(data.get("velocity", 0))

            max_len = 120
            for k in history:
                if len(history[k]) > max_len:
                    history[k] = history[k][-max_len:]

            chart_placeholder.line_chart({
                "Altitude": history["altitude"],
                "Velocity": history["velocity"],
            })
        else:
            status_placeholder.error(f"API returned {resp.status_code}: {resp.text}")
    except Exception as e:
        status_placeholder.error(f"Erro ao acessar API: {e}")

    time.sleep(POLL_INTERVAL)
