import os
import time
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000/telemetry")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))
RETRY_INTERVAL = float(os.getenv("RETRY_INTERVAL", "5.0"))

st.set_page_config(page_title="KSP Mission Control", layout="wide")
st.title("🚀 KSP Mission Control")

# --- Session state initialization ---
if "connected" not in st.session_state:
    st.session_state.connected = False
if "history" not in st.session_state:
    st.session_state.history = {"altitude": [], "velocity": []}
if "prev" not in st.session_state:
    st.session_state.prev = {}
if "last_data" not in st.session_state:
    st.session_state.last_data = None
if "last_seen" not in st.session_state:
    st.session_state.last_seen = None

# --- Status bar ---
status_bar = st.empty()

# --- Connection controls ---
ctrl_col, _ = st.columns([1, 5])
if not st.session_state.connected:
    if ctrl_col.button("🔌 Connect", use_container_width=True):
        st.session_state.connected = True
        st.rerun()

# --- Fetch telemetry (only when connected) ---
data = None
fetch_error = None

if st.session_state.connected:
    try:
        resp = requests.get(API_URL, timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.last_data = data
            st.session_state.last_seen = time.time()
        else:
            fetch_error = f"kRPC unavailable (status {resp.status_code})"
    except Exception:
        fetch_error = "Could not reach API"

# --- Determine display state ---
# Use fresh data if available, fall back to last known values
display_data = data or st.session_state.last_data
is_stale = data is None and st.session_state.last_data is not None
is_reconnecting = st.session_state.connected and fetch_error is not None

# --- Status bar rendering ---
if not st.session_state.connected:
    status_bar.error("🔴 Disconnected — press Connect to start")
elif is_reconnecting:
    last_seen_ago = int(time.time() - st.session_state.last_seen) if st.session_state.last_seen else "?"
    status_bar.warning(f"🟡 Reconnecting... (last data {last_seen_ago}s ago)")
else:
    status_bar.success("🟢 Connected to KSP via kRPC")

# --- Helper: compute delta from previous cycle ---
def delta(key, current):
    prev_val = st.session_state.prev.get(key)
    return round(current - prev_val, 2) if prev_val is not None else None

# --- Helper: format value or placeholder ---
def fmt(value, format_spec="{:,.1f}"):
    if value is None:
        return "—"
    return format_spec.format(value)

# --- Flight Data ---
st.subheader("Flight Data")
f1, f2, f3, f4 = st.columns(4)

altitude        = display_data.get("altitude", None)        if display_data else None
vertical_speed  = display_data.get("vertical_speed", None)  if display_data else None
horizontal_speed= display_data.get("horizontal_speed", None)if display_data else None
heading         = display_data.get("heading", None)         if display_data else None

f1.metric("Altitude (m)",           fmt(altitude),          delta=delta("altitude", altitude) if altitude is not None else None)
f2.metric("Vertical Speed (m/s)",   fmt(vertical_speed),    delta=delta("vertical_speed", vertical_speed) if vertical_speed is not None else None)
f3.metric("Horizontal Speed (m/s)", fmt(horizontal_speed),  delta=delta("horizontal_speed", horizontal_speed) if horizontal_speed is not None else None)
f4.metric("Heading (°)",            fmt(heading))

# --- Orbital Data ---
st.subheader("Orbital Data")
o1, o2, o3, o4 = st.columns(4)

apoapsis  = display_data.get("apoapsis", None)  if display_data else None
periapsis = display_data.get("periapsis", None)  if display_data else None
fuel      = display_data.get("fuel", None)       if display_data else None
body      = display_data.get("body", "—")        if display_data else "—"

o1.metric("Apoapsis (m)",  fmt(apoapsis),  delta=delta("apoapsis", apoapsis)   if apoapsis is not None else None)
o2.metric("Periapsis (m)", fmt(periapsis), delta=delta("periapsis", periapsis) if periapsis is not None else None)
o3.metric("Fuel (u)",      fmt(fuel),      delta=delta("fuel", fuel)           if fuel is not None else None)
o4.metric("Body",          body)

# --- Update previous values for delta (only on fresh data) ---
if data:
    st.session_state.prev = {
        "altitude":         altitude,
        "vertical_speed":   vertical_speed,
        "horizontal_speed": horizontal_speed,
        "apoapsis":         apoapsis,
        "periapsis":        periapsis,
        "fuel":             fuel,
    }

# --- Historical chart ---
if display_data and altitude is not None:
    st.subheader("History")

    if data:  # only append on fresh data
        st.session_state.history["altitude"].append(altitude)
        st.session_state.history["velocity"].append(horizontal_speed or 0)

        max_len = 120
        for k in st.session_state.history:
            if len(st.session_state.history[k]) > max_len:
                st.session_state.history[k] = st.session_state.history[k][-max_len:]

    if st.session_state.history["altitude"]:
        st.line_chart({
            "Altitude (m)":          st.session_state.history["altitude"],
            "Horizontal Speed (m/s)": st.session_state.history["velocity"],
        })

# --- Polling loop ---
if st.session_state.connected:
    if fetch_error:
        time.sleep(RETRY_INTERVAL)
    else:
        time.sleep(POLL_INTERVAL)
    st.rerun()
