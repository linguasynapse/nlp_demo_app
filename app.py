import os
import streamlit as st
from ui.theme import apply_theme
from ui.chrome import render_header, render_footer
from ui.env import PUBLIC_MODE
from ui.helpers import tighten_bloc_container
from i18n.translator import t, STRINGS
from debug_console import debug_console


st.set_page_config(
    page_title="AI-Powered Language Solutions",
    page_icon="assets/logo_dark.png",
    layout="wide",
    #initial_sidebar_state=None,
    menu_items={
        'Get Help': 'mailto:linguasynapse@yahoo.fr',
        'Report a bug': "mailto:linguasynapse@yahoo.fr",
        'About': "https://linguasynapse.wordpress.com/",
    }
)

# logo
st.logo("ui/assets/logo_dark.png", icon_image="ui/assets/icon_2.png", size="large")

# Apply theme and render header

tighten_bloc_container()
apply_theme()
render_header()

# auto register pages from the pages/ directory - automatic page update when new files are added
def auto_register_pages():
    pages = []
    for file in os.listdir("pages"):
        if file.endswith(".py") and not file.startswith("_"):
            name = file.replace(".py", "")
            key = f"nav_{name.lower()}"
            title = f"{t(key)}" if key in STRINGS["en"] else name
            pages.append(st.Page(f"pages/{file}", title=title))
    return pages


# Define pages - manually for more control
def get_pages():
    return [
        st.Page("pages/Home.py", title=f"🏠 {t('nav_home')}", default=True),
        st.Page("pages/NLP_Content_Intelligence.py", title=f"🧠 {t('nav_nlp')}"),
        st.Page("pages/Data_Engineering.py", title=f"🔧 {t('nav_data_engineering')}"),
        st.Page("pages/Asset_Quality_Mgmt.py", title=f"📚 {t('nav_asset_quality')}"),
        st.Page("pages/Contact.py", title=f"📬 {t('nav_contact')}"),
        st.Page("pages/Privacy.py", title=f"🔐 {t('nav_privacy')}"),
    ]

# pages = auto_register_pages()
pages = get_pages()
pg = st.navigation(pages, position="top")
pg.run()

render_footer()
