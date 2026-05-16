# ui/motion.py
import streamlit as st
from contextlib import contextmanager

@contextmanager
def fade_block():
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown('</div>', unsafe_allow_html=True)

@contextmanager
def slide_up_block():
    st.markdown('<div class="slide-up">', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown('</div>', unsafe_allow_html=True)

def end():
    st.markdown("</div>", unsafe_allow_html=True)
