# debug_console.py
import streamlit as st

def debug_console(page):
    """Display internal state, caches, and event bus info."""

    with st.expander("🛠 Debug Console", expanded=False):

        st.subheader("Page State")
        st.json(page.state)

        st.subheader("Page Cache")
        st.json(page.cache)

        st.subheader("Global Cache")
        st.json(page.global_cache)

        st.subheader("EventBus Listeners")
        st.json(page.bus._listeners)

        st.subheader("EventBus Queue")
        st.json(page.bus._queue)

        if st.button("Clear Page Cache"):
            page.cache_clear()
            st.success("Page cache cleared")

        if st.button("Clear Global Cache"):
            page.global_cache_clear()
            st.success("Global cache cleared")
