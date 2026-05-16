# ui/inputs.py
import streamlit as st
from ui.helpers import make_key
from i18n.translator import t

def text_area_with_controls(
    tab: int,
    state_key: str,
    label: str = t("input_label"),
    height: int = 200,
    default_text: str = None,
    show_default: bool = True,
    samples: dict = None,
    show_samples: bool = True,
    show_reset: bool = True,
):
    choice = None
    if samples:
        choice = st.selectbox(
            f"📚 {t('try_example')}",
            options=list(samples.keys()),
            key=make_key(tab, "sel", f"{state_key}_samples")
        )

    cols = st.columns(2)
    with cols[0]:
        if show_default and default_text:
            if st.button(t("nlp_use_default"), key=make_key(tab, "btn", f"default_{state_key}")):
                st.session_state[state_key] = default_text
        elif show_samples and samples:
            if st.button(t("load_example"), key=make_key(tab, "btn", f"sample_{state_key}")):
                st.session_state[state_key] = samples[choice]

    with cols[1]:
        if show_reset:
            if st.button(t("reset_txt"), key=make_key(tab, "btn", f"reset_{state_key}")):
                st.session_state[state_key] = ""

    return st.text_area(label, height=height, key=state_key)
