# Asset_Quality_Mgmt.py
from base_page import BasePage

class AssetQualityMgmtPage(BasePage):

    # -------------------------------------------------
    # Main entry point
    # -------------------------------------------------
    def run(self):
        self.process_events()
        self.inject_tokens()     # global design tokens
        self.inject_css(self.css())

        self.st.title(f"📚 {self.t("asset_title")}")

        self.content()


    def content(self):
        # TM & Glossary Engine
        self.header("asset_tm_glossary")
        self.st.markdown(f"{self.t("asset_tm_glossary_intro")}")

        # Interactive Glossary Search
        search_term = self.st.text_input(self.t("asset_tm_glossary_search"), "API")
        glossary_db = {
            "API": {"FR": "Interface de programmation", "ZH": "应用程序接口"},
            "Machine Learning": {"FR": "Apprentissage automatique", "ZH": "机器学习"},
        }
        if search_term:
            self.st.dataframe(glossary_db.get(search_term, {}), use_container_width=True)

        # Human-in-the-Loop Annotation
        self.st.header(f"🎯 {self.t("asset_annotation")}")
        self.st.markdown(f"{self.t("asset_annotation_intro")}")
        uploaded_file = self.st.file_uploader(self.t("asset_file_uploader"), type=['txt', 'json'])
        if uploaded_file:
            self.st.success(f"{self.t("asset_file_uploader_success")}: {uploaded_file.name}")
            self.st.button(self.t("asset_send_for_expert_review"), type="primary", key="asset_send_for_expert_review")

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


def main():
    AssetQualityMgmtPage().run()


if __name__ == "__main__":
    main()


# -------------------------------------------------
# END OF PAGE