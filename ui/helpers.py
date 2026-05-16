# ui/helpers.py
import streamlit as st
import time
import uuid
import bleach
from i18n.translator import t

def make_key(*parts):
    return "_".join(str(p) for p in parts)

def guarded_action(key: str, cooldown: int, max_chars: int, text: str):
    now = time.time()
    last = st.session_state.get(key, 0)
    if now - last < cooldown:
        st.warning(f"Please wait {int(cooldown - (now - last))} seconds before submitting again.")
        return False
    if len(text) > max_chars:
        st.error(f"Input exceeds maximum length of {max_chars} characters.")
        return False
    st.session_state[key] = now
    return True

def model_loading_notice(label: str):
    st.info(
        f"🔄 **{label}**",
        icon="⚡"
    )

def safe_html(text: str) -> str:
    """
    Sanitize user-provided text so it can be safely injected into HTML.
    Removes scripts, event handlers, dangerous tags, and inline JS.
    """
    if not isinstance(text, str):
        return ""

    return bleach.clean(
        text,
        tags=[],            # allow NO HTML tags from user
        attributes={},      # allow NO attributes
        strip=True          # remove disallowed tags entirely
    )

def tighten_bloc_container():
    st.markdown(
    """
    <style>
        header + section .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
        }

        .block-container > div:first-child {
            margin-top: -0.5rem;
        }

        .gradient-divider {
            margin: 0.5rem 0 0.75rem 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)