from base_page import BasePage

class PrivacyPage(BasePage):

    # -------------------------------------------------
    # Main entry point
    # -------------------------------------------------
    def run(self):
        self.process_events()
        self.inject_tokens()
        self.inject_css(self.css())

        self.st.title(f"🔐 {self.t("privacy_title")}")
        self.content()

    def content(self):
        with self.card(self.t("privacy_summary"), muted=True):
            self.st.markdown(self.t("privacy_summary_text"))

        with self.card(self.t("privacy_not_collected")):
            self.st.markdown(self.t("privacy_not_collected_text"))

        with self.card(self.t("privacy_collected")):
            self.st.markdown(self.t("privacy_collected_text"))

        with self.card(self.t("privacy_contact")):
            self.st.markdown(self.t("privacy_contact_text"))

        with self.card(self.t("privacy_disclaimer"), muted=True):
            self.st.caption(self.t("privacy_disclaimer_text"))

    def css(self):
        return """
        .entity-highlight {
            padding: 2px 4px;
            border-radius: var(--radius-sm);
        }
        """

def main():
    PrivacyPage().run()


if __name__ == "__main__":
    main()
