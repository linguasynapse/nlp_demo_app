import streamlit as st

def card(title, body, icon=None):
    st.markdown(
        f"""
        <div style="
            border: 1px solid #e0e0e0;
            padding: 1rem;
            border-radius: 10px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        ">
            <h4 style="margin-bottom:0.5rem">{icon or ''} {title}</h4>
            <p style="opacity:0.85">{body}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def alert(message, type="info"):
    colors = {
        "info": "#0072ff",
        "success": "#2ecc71",
        "warning": "#f1c40f",
        "error": "#e74c3c"
    }
    st.markdown(
        f"""
        <div style="
            padding: 0.75rem 1rem;
            border-left: 5px solid {colors[type]};
            background: #f9f9f9;
            border-radius: 6px;
            margin-bottom: 1rem;
        ">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )

def badge(text, color="#0072ff"):
    st.markdown(
        f"""
        <span style="
            background:{color}22;
            color:{color};
            padding:0.25rem 0.5rem;
            border-radius:6px;
            font-size:0.85rem;
            margin-right:0.25rem;
        ">{text}</span>
        """,
        unsafe_allow_html=True
    )

def timeline(items):
    st.markdown("<div style='border-left:2px solid #0072ff; padding-left:1rem'>", unsafe_allow_html=True)
    for title, desc in items:
        st.markdown(
            f"""
            <div style="margin-bottom:1rem">
                <h4 style="margin-bottom:0.25rem">{title}</h4>
                <p style="opacity:0.8">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
