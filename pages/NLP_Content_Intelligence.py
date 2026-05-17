from base_page import BasePage
import re
import pandas as pd
import jieba
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import onnxruntime as ort
from transformers import AutoTokenizer
#from transformers.pipelines import pipeline
from langdetect import detect, detect_langs, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import langid
import os
DetectorFactory.seed = 0

class OnnxSentimentModel:
    def __init__(self, model_id):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.session = ort.InferenceSession(
            f"https://huggingface.co/{model_id}/resolve/main/model.onnx",
            providers=["CPUExecutionProvider"]
        )

    def __call__(self, text):
        inputs = self.tokenizer(text, return_tensors="np")
        outputs = self.session.run(None, dict(inputs))
        logits = outputs[0]

        # Softmax
        import numpy as np
        probs = np.exp(logits) / np.exp(logits).sum(-1, keepdims=True)
        label_id = probs.argmax(-1)[0]
        score = probs[0][label_id]

        labels = ["negative", "neutral", "positive"]
        return [{"label": labels[label_id], "score": float(score)}]

class NLPPage(BasePage):

    # -------------------------------------------------
    # Main entry point
    # -------------------------------------------------
    def run(self):
        self.process_events()
        self.inject_tokens()     # global design tokens
        self.inject_css(self.css())

        self.st.title(f"🧠 {self.t('nlp_title')}")

        tabs = self.st.tabs([
            self.t("nlp_sentiment"),
            self.t("nlp_keywords"),
            self.t("nlp_ner")
        ])

        with tabs[0]:
            self.render_sentiment_tab()

        with tabs[1]:
            self.render_keyword_tab()

        with tabs[2]:
            self.render_ner_tab()
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
    # Hybrid cached model loader
    # -------------------------------------------------
    def load_model(self):
        self.model_notice(self.t("nlp_loading_model"))
        return OnnxSentimentModel("onnx-community/xlm-roberta-base-sentiment")
        #return pipeline(
        #    "sentiment-analysis",
        #    model="finiteautomata/bertweet-base-sentiment-analysis", # Streamlit Cloud compatible
            #model="nlptown/bert-base-multilingual-uncased-sentiment",
        #    device=None, #disable torch on Steamlit Cloud
        #    framework="pt", #no automatic detection (no torch)
        #)

    def get_model(self):
        return self.hybrid_cache_get("sentiment_model", self.load_model)

    # -------------------------------------------------
    # TAB 1 — SENTIMENT ANALYSIS
    # -------------------------------------------------
    def render_sentiment_tab(self):
        left, right = self.dashboard()
    
        with left:
            with self.card(f"😍😞 {self.t("nlp_sentiment_tool")}", refreshable=False):
                samples = { 
                    self.t("nlp_sentiment_po"): self.t("nlp_sentiment_po_review"),
                    self.t("nlp_sentiment_ne"): self.t("nlp_sentiment_ne_review"),
                    self.t("nlp_sentiment_neu"): self.t("nlp_sentiment_neu_review")
                }
            
                raw_text = self.text_area(
                    tab=0,
                    state_key="sentiment_text",
                    samples=samples,
                    show_samples=True,
                    show_reset=True
                )
        
            run = self.st.button(self.t("nlp_btn_analyze"), key=self.key("sentiment", "btn"))
    
        with right:
            with self.card(self.t("nlp_sentiment_demo"), muted=True):
                if not self.st.session_state.get("sentiment_model_loaded", False):
                    self.model_notice(self.t("nlp_sentiment_model"))
            
                if run and raw_text.strip():                    
                    lang = self.detect_language(raw_text)
                    self.st.session_state["detected_lang"] = lang
                    detected_lang = self.st.session_state.get("detected_lang", "en")
                
                    # Analyze sentiment
                    
                    label, score = self.analyze_sentiment(raw_text)
                    self.st.session_state["sentiment_model_loaded"] = True
                
                    # Display confidence score
                    self.st.metric(self.t("nlp_confidence"), round(score, 3))
                
                    # Display detected language
                    self.st.caption(f"{self.t('nlp_detected_lang')}{lang}")
                
                    # Display sentiment result
                    self.normalize_sentiment(label)

                    # Apply font styling only for specific languages
                    if detected_lang in ["zh", "ja", "ko", "ar"]:
                        font_families = {
                            "zh": "Noto Sans SC",
                            "ja": "Noto Sans JP",
                            "ko": "Noto Sans KR",
                            "ar": "Noto Sans Arabic"
                        }
                        font_family = font_families.get(detected_lang, "sans-serif")
                    
                        # Inject font and CSS
                        font_html = f'<link href="https://fonts.googleapis.com/css2?family={font_family.replace(" ", "+")}:wght@400;500&display=swap" rel="stylesheet">'
                        css = f"""
                        <style>
                        .custom-sentiment {{
                            font-family: '{font_family}', sans-serif;
                            font-size: 24px;
                            font-weight: 500;
                            margin: 10px 0;
                            padding: 10px;
                            
                        }}
                        </style>
                        """
                        self.st.markdown(font_html + css, unsafe_allow_html=True)
                        self.st.markdown(f'<div class="custom-sentiment">{self.normalize_sentiment(label)}</div>', unsafe_allow_html=True)
                    else:
                        # For non-Asian languages, just display normally
                        self.st.markdown(f'<div style="font-size: 24px; margin: 10px 0; ">{self.normalize_sentiment(label)}</div>', unsafe_allow_html=True)
                
                else:
                    self.st.info(self.t("nlp_sentiment_run"))
                    with self.st.expander(f"ℹ️ {self.t('about_tool')}"):
                        self.st.caption(self.t("nlp_sentiment_tool_info"))
    
        # Word cloud section - SIMPLIFIED
        if run and raw_text.strip():
            if self.st.checkbox(self.t("nlp_show_wc"), value=True):
                with self.fade():
                    self.st.subheader(f"☁️ {self.t('nlp_wc')}")
                
                    # Simple test first
                    self.st.write(self.t("nlp_text_len"), len(raw_text))
                    self.st.write(self.t("nlp_detected_lang"), self.detect_language(raw_text))
                
                    # Try to generate word cloud
                    try:
                        fig = self.generate_wordcloud(raw_text)
                        if fig:
                            self.st.pyplot(fig)
                        else:
                            self.st.warning(self.t("nlp_no_wc"))
                    except Exception as e:
                        self.st.error(f"{self.t('nlp_error_wc')}: {str(e)}")

    def analyze_sentiment(self, text):
        model = self.get_model()
        result = model(text)[0]
        return result["label"], result["score"]

    def normalize_sentiment(self, label):
        stars = int(label.split()[0])
        if stars <= 2:
            return f'🙁 {self.t("nlp_sentiment_negative")}'
        elif stars == 3:
            return f'🤔 {self.t("nlp_sentiment_neutral")}'
        else:
            return f'🙂 {self.t("nlp_sentiment_positive")}'

    def generate_wordcloud(self, text):
        lang = self.detect_language(text)
    
        # For Chinese text, use jieba with proper segmentation
        if lang == "zh":
            try:
                jieba.initialize()
            except:
                pass
            text = " ".join(jieba.cut(text, cut_all=False))
        else:
            text = str(text) # For other languages, ensure it's a string
    
        # Create word cloud with Chinese font support
        try:
            # Try to use a Chinese font if available
            font_path = None
            if lang == "zh":
                # Common Chinese font paths
                chinese_fonts = [
                    "/System/Library/Fonts/PingFang.ttc",  # macOS
                    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
                    "C:/Windows/Fonts/msyh.ttc",  # Windows
                    "C:/Windows/Fonts/simhei.ttf",  # Windows
                ]
                for font in chinese_fonts:
                    if os.path.exists(font):
                        font_path = font
                        break
        
            wc = WordCloud(
                width=900,
                height=450,
                background_color="white",
                max_words=120,
                collocations=False,
                font_path=font_path,  # Add font path for Chinese
                stopwords=set()  # Clear default stopwords for Chinese
            ).generate(text)
        
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            return fig
        
        except Exception as e:
            self.st.error(f"Word cloud generation error: {str(e)}")
            # Fallback to simple display
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, self.t('nlp_no_wc'), 
                    ha='center', va='center', fontsize=12)
            ax.axis("off")
            return fig

    def detect_language(self, text):
        text = text.strip()
        lang, confidence = langid.classify(text) # Use langid for language detection
        return "zh" if lang == "zh" else lang

    def detect_language_with_optimization(self, text):
        try:
            results = detect_langs(text.strip()) # Improved language detection - returns probability distribution        
            for result in results:# Check all possibilities, prioritize Chinese
                lang = result.lang
                if lang.startswith("zh"):
                    return "zh"
            return results[0].lang # Return top result if no Chinese found
        except Exception:
            return "unknown"

    def detect_language_no_optimation(self, text):
        try:
            lang = detect(text.strip())# only returns the top guess. - issue with zht
            return "zh" if lang.startswith("zh") else lang
        except Exception:
            return "unknown"

    # -------------------------------------------------
    # TAB 2 — KEYWORD EXTRACTION
    # -------------------------------------------------
    def render_keyword_tab(self):
        left, right = self.dashboard()
        with left:
            with self.card(f"🔑 {self.t('nlp_keywords')}", refreshable=False):

                samples = { 
                    self.t("tech_news"): self.t("tech_txt"),
                    self.t("sports"): self.t("sports_txt"),
                    self.t("his"): self.t("his_txt")
                }

                raw_text = self.text_area(
                    tab=0,
                    state_key="kw_text",
                    samples=samples,
                    show_samples=True,
                    show_reset=True
                )

                run = self.st.button(self.t("nlp_btn_extract"), key=self.key("kw", "btn"))
                if run and raw_text.strip():                    
                    kws = self.extract_keywords(raw_text)
                    if kws:
                        self.st.success(f"✅ {self.t("nlp_extracted_keywords")}")
                        for word, freq in kws:
                            self.st.write(f"- **{word}** ({freq})")
                    else:
                        self.st.warning(self.t("nlp_no_kw"))

        with right:
            with self.card(self.t("nlp_keyword_demo"), muted=True):
                self.st.info(self.t("nlp_kw_run"))
                with self.st.expander(f"ℹ️ {self.t('about_tool')}"):
                    self.st.caption(self.t("nlp_kw_info"))

    def extract_keywords(self, text, top_n=5):
        words = re.findall(r"\b\w+\b", text.lower())
        stopwords = {"the", "and", "is", "in", "of", "to", "a", "was", "as"}
        filtered = [w for w in words if w not in stopwords and len(w) > 2]
        counts = Counter(filtered)
        return counts.most_common(top_n)

    # -------------------------------------------------
    # TAB 3 — SIMPLE NER
    # -------------------------------------------------
    def render_ner_tab(self):
        left, right = self.dashboard()
        with left:
            with self.card(f"🔎 {self.t('nlp_ner')}", refreshable=False):

                samples = { 
                    self.t("tech_news"): self.t("tech_txt"),
                    self.t("sports"): self.t("sports_txt"),
                    self.t("his"): self.t("his_txt")
                }

                raw_text = self.text_area(
                    tab=0,
                    state_key="ner_text",
                    samples=samples,
                    show_samples=True,
                    show_reset=True
                )

                run = self.st.button(self.t("nlp_btn_ner"), key=self.key("ner", "btn"))
                if run and raw_text.strip():                    
                    entities = self.simple_ner(raw_text)
                    if entities:
                        
                        # Legend
                        self.st.markdown(self.t("nlp_ner_legend"), unsafe_allow_html=True)
                        self.st.markdown(f"""
                        - <span style='background-color:#FFD700; padding:2px; border-radius:3px;'>Gold</span> → {self.t("nlp_proper_noun")}  
                        - <span style='background-color:#87CEEB; padding:2px; border-radius:3px;'>Blue</span> → {self.t("nlp_number")}  
                        - <span style='background-color:#90EE90; padding:2px; border-radius:3px;'>Green</span> → {self.t("nlp_year")}  
                        """, unsafe_allow_html=True)

                        highlighted = self.highlight_entities(raw_text, entities)
                        self.st.markdown(highlighted, unsafe_allow_html=True)

                        df = pd.DataFrame(entities, columns=[self.t("nlp_entity"), self.t("nlp_type")])
                        self.st.table(df)
                    else:
                        self.st.warning(self.t("nlp_no_entities"))

        with right:
            with self.card(self.t("nlp_ner_demo"), muted=True):
                self.st.info(self.t("nlp_ner_run"))
                with self.st.expander(f"ℹ️ {self.t('about_tool')}"):
                    self.st.caption(self.t("nlp_ner_info"))

    def simple_ner(self, text):
        entities = []
        for match in re.findall(r"\b[A-Z][a-z]+\b", text):
            entities.append((match, self.t("nlp_proper_noun")))
        for match in re.findall(r"\b\d+\b", text):
            entities.append((match, self.t("nlp_number")))
        for match in re.findall(r"\b\d{4}\b", text):
            entities.append((match, self.t("nlp_year")))
        return entities

    def highlight_entities(self, text, entities):
        """Wrap detected entities with colored spans."""
        highlighted = text
        for ent, label in entities:
            color = {
                self.t("nlp_proper_noun"): "#FFD700",  # gold
                self.t("nlp_number"): "#87CEEB",       # light blue
                self.t("nlp_year"): "#90EE90"          # light green
            }.get(label, "#FFB6C1")        # default pink

            highlighted = re.sub(
                fr"\b{ent}\b",
                f"<span style='background-color:{color}; padding:2px; border-radius:3px;'>{ent}</span>",
                highlighted
            )
        return highlighted

def main():
    NLPPage().run()


if __name__ == "__main__":
    main()
