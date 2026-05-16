import streamlit as st
from i18n.strings import STRINGS

def t(key: str) -> str:
    """Translate a given key based on the current language setting."""
    lang = st.session_state.get("lang_code", "en")
    value = STRINGS.get(lang, STRINGS["en"]).get(key)

    if value is None:
        st.warning(f"⚠ Missing translation: `{key}`", icon="⚠")
        return f"[{key}]"

    return value