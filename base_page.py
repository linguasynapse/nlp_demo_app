 # base_page.py
from pathlib import Path
import streamlit as st
from i18n.translator import t
from event_bus import get_event_bus
from utils import compute_jaccard_similarity
from ui.env import PUBLIC_MODE
from ui.inputs import text_area_with_controls
from ui.cards import card
from ui.layout import dashboard
from ui.motion import fade_block, end
from ui.tokens import TOKENS
from ui.styles import ANIMATION_CSS
from ui.helpers import (
    make_key, 
    guarded_action, 
    model_loading_notice, 
    safe_html, 
    tighten_bloc_container
)

class BasePage:
    """Base class for all pages to avoid repeated imports."""
    def __init__(self):
        self.st = st
        self.Path = Path
        self.t = t
        self.bus = get_event_bus()

        # expose UI components
        self.text_area = text_area_with_controls
        self.key = make_key
        self.guard = guarded_action
        self.card = card
        self.fade = fade_block
        self.end = end
        self.model_notice = model_loading_notice
        self.tighten_bloc_container = tighten_bloc_container
        self.compute_jaccard = compute_jaccard_similarity
        #self.st.markdown(ANIMATION_CSS, unsafe_allow_html=True) # inject core styles once
        self.safe_html = safe_html
        self.dashboard = dashboard
        self.PUBLIC_MODE = PUBLIC_MODE

        self._setup_ui() # Inject ANIMATION_CSS custom UI components

        # -------------------------
        # Page-level state
        # -------------------------
        if "page_state" not in st.session_state:
            st.session_state.page_state = {}

        page_name = self.__class__.__name__
        if page_name not in st.session_state.page_state:
            st.session_state.page_state[page_name] = {}

        self.state = st.session_state.page_state[page_name]

        # -------------------------
        # Page-level cache
        # -------------------------
        if "page_cache" not in st.session_state:
            st.session_state.page_cache = {}

        if page_name not in st.session_state.page_cache:
            st.session_state.page_cache[page_name] = {}

        self.cache = st.session_state.page_cache[page_name]

        # -------------------------
        # Global cache
        # -------------------------
        if "global_cache" not in st.session_state:
            st.session_state.global_cache = {}

        self.global_cache = st.session_state.global_cache

    # -------------------------
    # Page-level cache
    # -------------------------
    def cache_get(self, key, compute_fn):
        """Return cached value or compute and store it."""
        if key not in self.cache:
            self.cache[key] = compute_fn()
        return self.cache[key]
    def cache_set(self, key, value):
        self.cache[key] = value

    def cache_clear(self):
        self.cache.clear()

    # -------------------------
    # Global cache (shared across all pages)
    # -------------------------
    def global_cache_get(self, key, compute_fn):
        if key not in self.global_cache:
            self.global_cache[key] = compute_fn()
        return self.global_cache[key]

    # -------------------------
    # Hybrid cache: try page cache, then global cache, then compute
    # -------------------------
    def hybrid_cache_get(self, key, compute_fn):
        """Try page cache → global cache → compute."""
        if key in self.cache:
            return self.cache[key]
        if key in self.global_cache:
            self.cache[key] = self.global_cache[key]
            return self.cache[key]
        value = compute_fn()
        self.cache[key] = value
        self.global_cache[key] = value
        return value

    # -------------------------
    # EventBus processing
    # -------------------------
    def process_events(self):
        self.bus.process()

    # -------------------------
    # Override in child pages
    # -------------------------
    def run(self):
        raise NotImplementedError


    # -------------------------
    # Translation helpers
    # -------------------------
    def title(self, key):
        self.st.title(self.t(key))

    def header(self, key):
        self.st.header(self.t(key))

    def text(self, key):
        self.st.write(self.t(key))

    def markdown(self, key):
        self.st.markdown(self.t(key))

    # -------------------------
    # Custom UI Components
    # -------------------------
    def _setup_ui(self):
        self.st.markdown(ANIMATION_CSS, unsafe_allow_html=True)

    def hero(self, title_key, subtitle_key=None, image=None):
        """Full-width hero section."""
        if image:
            self.st.image(image, width="stretch")

        self.st.markdown(f"<h1 style='margin-bottom:0'>{self.t(title_key)}</h1>", unsafe_allow_html=True)

        if subtitle_key:
            self.st.markdown(
                f"<p style='font-size:1.2rem; opacity:0.8'>{self.t(subtitle_key)}</p>",
                unsafe_allow_html=True
            )

    def section(self, key):
        """Styled section header."""
        self.st.markdown(
            f"<h2 style='border-left: 4px solid #0072ff; padding-left: 0.5rem'>{self.t(key)}</h2>",
            unsafe_allow_html=True
        )

    # -------------------------
    # Design Tokens Injection
    # -------------------------
    def inject_tokens(self):
        css = ":root {\n"
        for key, value in TOKENS.items():
            css_var = key.replace(".", "-")
            css += f"  --{css_var}: {value};\n"
        css += "}"
        self.st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # -------------------------
    # Page-level CSS
    # -------------------------
    def inject_css(self, css: str):
        self.st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
