import streamlit as st
from ls_ui.cards import card
from ls_ui.grid import two_col
from ls_ui.env import PUBLIC_MODE
from ls_ui.telemetry import snapshot

if PUBLIC_MODE:
    st.warning("Usage dashboard is not available in public mode.")
    st.stop()

st.title("📊 Usage Dashboard")

data = snapshot()

# ---------------------------
# High-level KPIs
# ---------------------------

col1, col2 = two_col()

with col1:
    with card("Feature Usage", muted=True):
        if data["events"]:
            st.bar_chart(data["events"])
        else:
            st.info("No usage data yet.")

with col2:
    with card("Errors", muted=True):
        if data["errors"]:
            st.bar_chart(data["errors"])
        else:
            st.success("No errors recorded.")

# ---------------------------
# Performance
# ---------------------------

with card("Average Latency (seconds)", muted=True):
    if data["latency_avg"]:
        st.table(data["latency_avg"])
    else:
        st.info("No latency data yet.")
