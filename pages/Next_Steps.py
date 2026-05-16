import streamlit as st

st.header("🎁 Get Free Audit")
with st.form("audit"):
    email = st.text_input("Your email")
    goal = st.selectbox("Goal", ["Translation", "NLP Model", "Dataset"])
    file = st.file_uploader("Share a sample")
    submitted = st.form_submit_button("Receive Insights")
    if submitted:
        st.success("Audit request sent! You'll hear back in 24h.")