# Utility to generate unique keys
import streamlit as st
from ui.helpers import make_key
from i18n.translator import t


# Bilingual sample controls
def bilingual_sample_controls(tab: int, samples: dict, src_key: str, tgt_key: str, t=t):
    choice = st.selectbox(
        f"📚 {t('try_example')}",
        options=list(samples.keys()),
        key=make_key(tab, "sel", "align_samples")
    )

    cols = st.columns(2)
    with cols[0]:
        if st.button(t("load_example"), key=make_key(tab, "btn", "load_align_sample")):
            st.session_state[src_key] = samples[choice]["src"]
            st.session_state[tgt_key] = samples[choice]["tgt"]

    with cols[1]:
        if st.button(t("reset_txt"), key=make_key(tab, "btn", "reset_align")):
            st.session_state[src_key] = ""
            st.session_state[tgt_key] = ""

# Deduplication results display
def render_dedup_results(kept, removed, t=t):
    st.metric(t("kept_segments"), len(kept))
    st.metric(t("removed_segments"), len(removed))

    if kept:
        st.markdown(f"### ✅ {t('kept_segments')}")
        for i, seg in enumerate(kept, start=1):
            st.write(f"{i}. {seg}")

    if removed:
        st.markdown(f"### 🗑️ {t('removed_segments')}")
        for seg, ref, score in removed:
            st.warning(f"{t('similarity')} {score:.2f}")
            st.write(f"{t('removed')} {seg}")
            st.write(f"{t('matched_with')} {ref}")

# Jaccard similarity
def compute_jaccard_similarity(str1: str, str2: str) -> float:
    """
    Compute Jaccard similarity between two strings based on word sets.
    Jaccard similarity = (size of intersection) / (size of union)
    """
    set1 = set(str1.lower().split())
    set2 = set(str2.lower().split())
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    if not union:
        return 0.0
    return len(intersection) / len(union)
