# Data_Engineering.py
import re
import pandas as pd
import jieba
import json
import string
from base_page import BasePage
from utils import bilingual_sample_controls, render_dedup_results


class DataEngineeringPage(BasePage):

    # -------------------------------------------------
    # Main entry point
    # -------------------------------------------------
    def run(self):
        self.process_events()
        self.inject_tokens()     # global design tokens
        self.inject_css(self.css())

        self.title("data_engineering_title")

        tabs = self.st.tabs([
            self.t("data_align"),
            self.t("data_cleaning"),
            self.t("data_dedup")
        ])

        with tabs[0]:
            self.render_align_tab()

        with tabs[1]:
            self.render_cleaning_tab()

        with tabs[2]:
            self.render_dedup_tab()

        # debug_console(self)

    # -------------------------------------------------
    # CSS
    # -------------------------------------------------
    def css(self):
        return """
        .entity-highlight {
            padding: 2px 4px;
            border-radius: var(--radius-sm);
        }
        """
    # -------------------------------------------------
    # TAB 1 — ALIGNMENT
    # -------------------------------------------------
    def render_align_tab(self):
        left, right = self.dashboard()
        with left:
            with self.card(f"↔️ {self.t("data_align_tool")}", refreshable=False):
                # --- Sample data for alignment ---
                ALIGN_SAMPLES = {
                    "FR → EN (Salutation/Greeting)": {
                    "src": "Bonjour. Comment ça va?",
                    "tgt": "Hello. How are you?"
                    },
                    "ZH → EN (产品/Product)": {
                    "src": "这是测试。我们正在对齐句子。",
                    "tgt": "This is a test. We are aligning sentences."
                    },
                    "FR → EN (Affaires/Business)": {
                    "src": "Le contrat a été signé hier. La livraison est prévue demain.",
                    "tgt": "The contract was signed yesterday. Delivery is scheduled for tomorrow."
                    }
                }              

                bilingual_sample_controls(
                    tab=0,
                    samples=ALIGN_SAMPLES,
                    src_key="align_src",
                    tgt_key="align_tgt",
                    t=self.t
                )

                src_text = self.st.text_area(
                    self.t("data_align_src_text"),
                    height=180,
                    key="align_src"
                )

                tgt_text = self.st.text_area(
                    self.t("data_align_tgt_text"),
                    height=180,
                    key="align_tgt"
                )
            
            # Initialize in session state if not exists
            if 'aligned_pairs' not in self.st.session_state:
                self.st.session_state.aligned_pairs = None
            
            if self.st.button(self.t("data_align_btn"), key=self.key("btn", "align")):
                aligned_pairs, src_sents, tgt_sents = self.simple_align(src_text, tgt_text)

                # Update session state
                self.st.session_state.aligned_pairs = aligned_pairs
                self.st.session_state.src_sents = src_sents
                self.st.session_state.tgt_sents = tgt_sents

                if aligned_pairs is None:
                    self.st.error(
                    f"❌ {self.t('data_align_mismatch')} — "
                    f"{self.t('data_align_src')}: {len(src_sents)}, {self.t('data_align_tgt')}: {len(tgt_sents)}"
                    )
                    self.st.info(f"💡 {self.t('data_align_check_counts')}")
                else:
                    self.st.success(f"✅ {self.t('data_align_completed')} {len(aligned_pairs)} {self.t('data_align_pairs')}")
                    self.render_alignment_results(aligned_pairs)

                    # ---- Export section ----
                    self.st.markdown(f"### 📦 {self.t('data_align_export')}")

                    tmx_content = self.build_tmx_lite(aligned_pairs, src_lang="fr", tgt_lang="en")
                    jsonl_content = self.build_jsonl(aligned_pairs, src_lang="fr", tgt_lang="en")

                    cols = self.st.columns(2)

                    with cols[0]:
                        self.st.download_button(
                            f"📥 {self.t('data_align_tmx')}",
                            tmx_content,
                            file_name="aligned.tmx",
                            mime="application/xml"
                        )
                    with cols[1]:
                        self.st.download_button(
                            f"📥 {self.t('data_align_jsonl')}",
                            jsonl_content,
                            file_name="aligned.jsonl",
                            mime="application/json"
                    )   
            
            # Check if there are previous results to show
            elif self.st.session_state.aligned_pairs is not None:
                aligned_pairs = self.st.session_state.aligned_pairs
                self.st.success(f"✅ {self.t('data_align_completed')} {len(aligned_pairs)} {self.t('data_align_pairs')}")
                self.render_alignment_results(aligned_pairs)

                # ---- Export section (show again)
                self.st.markdown(f"### 📦 {self.t('data_align_export')}")
                tmx_content = self.build_tmx_lite(aligned_pairs, src_lang="fr", tgt_lang="en")
                jsonl_content = self.build_jsonl(aligned_pairs, src_lang="fr", tgt_lang="en")
                cols = self.st.columns(2)

                with cols[0]:
                    self.st.download_button(
                        f"📥 {self.t('data_align_tmx')}",
                        tmx_content,
                        file_name="aligned.tmx",
                        mime="application/xml"
                    )
                with cols[1]:
                    self.st.download_button(
                        f"📥 {self.t('data_align_jsonl')}",
                        jsonl_content,
                        file_name="aligned.jsonl",
                        mime="application/json"
                    )   

        with right:
            with self.card(self.t("data_align_tool"), muted=True):
                self.st.info(self.t("data_align_info"))
                with self.st.expander(f"ℹ️ {self.t('about_tool')}"):
                    self.st.caption(self.t("data_align_tool_info"))

    # --- Align helper function ---
    def simple_align(self, src_text: str, tgt_text: str):
        """Align sentences by index from source and target texts, with mismatch check."""
        delimiters = [".", "。", "！", "？"]
        def split_sentences(text):
            for d in delimiters:
                text = text.replace(d, ".")  # normalize to "."
            return [s.strip() for s in text.split(".") if s.strip()]

        src_sentences = split_sentences(src_text)
        tgt_sentences = split_sentences(tgt_text)

        # Check mismatch
        if len(src_sentences) != len(tgt_sentences):
            return None, src_sentences, tgt_sentences

        # Align by index
        pairs = [(src, tgt) for src, tgt in zip(src_sentences, tgt_sentences)]
        return pairs, src_sentences, tgt_sentences

    def render_alignment_results(self, pairs):
        for i, (src, tgt) in enumerate(pairs, start=1):
            cols = self.st.columns([0.06, 0.47, 0.47])
            cols[0].markdown(f"**{i}.**")
            cols[1].write(src)
            cols[2].write(tgt)



    # --- TMX Builder ---
    def build_tmx_lite(self, pairs, src_lang="src", tgt_lang="tgt"):
        tus = []
        for i, (src, tgt) in enumerate(pairs, start=1):
            tus.append(
                f"""
                <tu tuid="{i}">
                <tuv xml:lang="{src_lang}"><seg>{src}</seg></tuv>
                <tuv xml:lang="{tgt_lang}"><seg>{tgt}</seg></tuv>
                </tu>
                """.strip()
            )

        return f"""<?xml version="1.0" encoding="UTF-8"?>
                <tmx version="1.4">
                    <body>
                        {"".join(tus)}
                    </body>
                </tmx>
                """
    
    # --- JSONL Builder ---
    def build_jsonl(self, pairs, src_lang="src", tgt_lang="tgt"):
        lines = []
        for src, tgt in pairs:
            lines.append(json.dumps({
                "source": src,
                "target": tgt,
                "src_lang": src_lang,
                "tgt_lang": tgt_lang
            }, ensure_ascii=False))
        return "\n".join(lines)
    
    
    # -------------------------------------------------
    # TAB 2 — CLEANING
    # -------------------------------------------------
    def render_cleaning_tab(self):
        left, right = self.dashboard()
        with left:
            with self.card(f"🧹 {self.t("data_cleaning_title")}", refreshable=False):              
                default_text = "<p>Hello <b>World</b>! This is <i>sample</i> text.</p>"
            
                # Initialize page-level state 
                if "clean_raw_text" not in self.st.session_state:
                    self.st.session_state.clean_raw_text = ""

                cols = self.st.columns(2)
                with cols[0]:
                    if self.st.button(self.t("data_cleaning_default"), key=self.key("btn", "default_clean")):
                        self.st.session_state.clean_raw_text = default_text
                with cols[1]:
                    if self.st.button(self.t("reset_txt"), key=self.key("btn", "reset_clean")):
                        self.st.session_state.clean_raw_text = ""

                raw_text = self.st.session_state.clean_raw_text
                raw_text = self.st.text_area(
                    "Raw Text",
                    height=200,
                    key="clean_raw_text"
                )

                self.st.markdown(f"**{self.t("data_cleaning_options")}**")
                apply_tags = self.st.checkbox(self.t("data_cleaning_tags"), value=True)
                apply_lower = self.st.checkbox(self.t("data_cleaning_lower"), value=True)
                apply_punct = self.st.checkbox(self.t("data_cleaning_punct"), value=False)

            if self.st.button(self.t("data_cleaning_run"), key=self.key("btn", "run_clean")):
                steps = []
                current = raw_text

                if apply_tags:
                    cleaned = self.safe_html(current)
                    cleaned = self.clean_tags(cleaned)
                    steps.append((self.t("data_cleaning_tags"), current, cleaned))
                    current = cleaned

                if apply_lower:
                    cleaned = self.safe_html(current)
                    cleaned = self.to_lower(cleaned)
                    steps.append((self.t("data_cleaning_lower"), current, cleaned))
                    current = cleaned

                if apply_punct:
                    cleaned = self.safe_html(current)
                    cleaned = self.strip_punct(cleaned)
                    steps.append((self.t("data_cleaning_punct"), current, cleaned))
                    current = cleaned

                if steps:
                    self.st.success(f"✅ {self.t('data_cleaning_completed')}")
                    self.render_cleaning_steps(steps)
                else:
                    self.st.warning(self.t("data_cleaning_no_options"))

        with right:
            with self.card(self.t("data_cleaning_title"), muted=True):
                self.st.info(self.t("data_cleaning_run_info"))
                with self.st.expander(f"ℹ️ {self.t('about_tool')}"):
                    self.st.caption(self.t("data_cleaning_tool_info"))


    # --- Cleaning helpers ---
    def clean_tags(self, text: str) -> str:
        """Remove HTML/XML tags but keep inner content."""
        return re.sub(r"</?[^>]+>", "", text)   # removes <tag> and </tag>, keeps content

    def to_lower(self, text: str) -> str:
        return text.lower()

    def strip_punct(self, text: str) -> str:
        return text.translate(str.maketrans("", "", string.punctuation))
    def render_cleaning_steps(self, steps):
        """
        steps: list of (step_name, before, after)
        """
        for i, (name, before, after) in enumerate(steps, start=1):
            self.st.markdown(f"**{i}. {name}**")
            cols = self.st.columns(2)
            cols[0].text_area(self.t("data_cleaning_before"), before, height=120, disabled=True, key=f"clean_before_{i}")
            cols[1].text_area(self.t("data_cleaning_after"), after, height=120, disabled=True, key=f"clean_after_{i}")

    # -------------------------------------------------
    # TAB 3 — DATASET DEDUPLICATION
    # -------------------------------------------------
    def render_dedup_tab(self):
        left, right = self.dashboard()
        with left:
            with self.card(f"🧪 {self.t("data_dedup_title")}", refreshable=False):              
            
                # Initialize page-level state 
                self.state.setdefault("clean_raw_text", "")

                default_text = """
                    Hello world
                    Hello world!
                    This is a sample sentence
                    This is a sample sentence with extra words
                    Another sentence
                    completely different line
                    Another sentence."""
                # Initialize page-level state 
                self.state.setdefault("dedup_text", "")
                cols = self.st.columns(2)
                with cols[0]:
                    if self.st.button(self.t("data_dedup_default"), key=self.key("btn", "default_dedup")):
                        self.st.session_state.dedup_text = default_text
                with cols[1]:
                    if self.st.button(self.t("reset_txt"), key=self.key("btn", "reset_dedup")):
                        self.st.session_state.dedup_text = ""

                raw_text = self.st.text_area(
                    self.t("data_dedup_input"),
                    help=self.t("data_dedup_input_help"),
                    height=220,
                    key="dedup_text"
                )

                similarity_threshold = self.st.slider(
                    self.t("data_dedup_threshold"),
                    help=self.t("data_dedup_threshold_help"),
                    min_value=0.5,
                    max_value=1.0,
                    value=0.8,
                    step=0.05
                )
        if self.st.button(self.t("data_dedup_run"), key=self.key("btn", "run_dedup")):
            segments = [s.strip() for s in raw_text.splitlines() if s.strip()]

            if len(segments) < 2:
                self.st.warning(self.t("data_dedup_min_segments"))
                #self.st.info(self.t("data_dedup_min_segments_info"))
            else:
                kept, removed = self.deduplicate_segments(
                    segments,
                    similarity_threshold=similarity_threshold
                )

                self.st.success(f"✅ {self.t("data_dedup_completed")}")
                render_dedup_results(kept, removed, t=self.t)

        with right:
            with self.card(self.t("data_dedup_demo"), muted=True):
                self.st.info(self.t("data_dedup_info"))
                with self.st.expander(f"ℹ️ {self.t('about_tool')}"):
                    self.st.caption(self.t("data_dedup_tool_info"))

    # --- Deduplication helpers ---
    def normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s]", "", text)
        return text.strip()

    def token_overlap(self, a: str, b: str) -> float:
        a_tokens = set(a.split())
        b_tokens = set(b.split())
        if not a_tokens or not b_tokens:
            return 0.0
        return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)

    def deduplicate_segments(self, segments, similarity_threshold=0.8):
        kept = []
        removed = []

        for seg in segments:
            norm = self.normalize_text(seg)
            is_duplicate = False

            for kept_seg in kept:
                kept_norm = self.normalize_text(kept_seg)
                # Exact match
                if norm == kept_norm:
                    removed.append((seg, kept_seg, 1.0))
                    is_duplicate = True
                    break
                # Similarity match
                sim = self.token_overlap(norm, kept_norm)
                if sim >= similarity_threshold:
                    removed.append((seg, kept_seg, sim))
                    is_duplicate = True
                    break

            if not is_duplicate:
                kept.append(seg)

        return kept, removed


def main():
    DataEngineeringPage().run()


if __name__ == "__main__":
    main()