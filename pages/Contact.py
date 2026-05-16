# contact_py
from base_page import BasePage

class ContactPage(BasePage):

    # -------------------------------------------------
    # Main entry point
    # -------------------------------------------------
    def run(self):
        self.process_events()
        self.inject_tokens()
        self.inject_css(self.css())

        self.st.title(f"📬 {self.t("contact_title")}")


        self.st.caption(
            self.t("contact_caption")
        )

        # -------------------------
        # Privacy notice
        # -------------------------
        self.render_privacy_notice()

        # -------------------------
        # Contact form
        # -------------------------
        self.render_contact_form()

        # -------------------------
        # Public mode notice
        # -------------------------
        self.render_public_mode_notice()

    # -------------------------------------------------
    # Privacy notice
    # -------------------------------------------------
    def render_privacy_notice(self):    
        with self.card(f"🔏 {self.t("contact_privacy_notice")}", muted=True):
            with self.st.expander(self.t("contact_privacy_notice_expander")):
                self.st.markdown(f"{self.t("contact_privacy_notice_content")}")

    # -------------------------------------------------
    # Contact form
    # -------------------------------------------------
    def render_contact_form(self):
        with self.card(f"📬 {self.t("contact_form_title")}"):
            with self.st.form("contact_form", clear_on_submit=True):
                col1, col2 = self.st.columns(2)

                with col1:
                    name = self.st.text_input(self.t("contact_form_name"), max_chars=80)
                    email = self.st.text_input(self.t("contact_form_email"), max_chars=120)

                with col2:
                    company = self.st.text_input(self.t("contact_form_company"), max_chars=120)
                    topic = self.st.selectbox(
                        self.t("contact_form_topic"),
                        [
                            self.t("contact_form_topic_options_1"),
                            self.t("contact_form_topic_options_2"),
                            self.t("contact_form_topic_options_3"),
                            self.t("contact_form_topic_options_4"),
                            self.t("contact_form_topic_options_5"),
                        ],
                    )

                message = self.st.text_area(
                    self.t("contact_form_message"),
                    height=160,
                    max_chars=1000,
                    placeholder=self.t("contact_form_message_placeholder"),
                )

                submitted = self.st.form_submit_button(self.t("contact_form_submit"))

            if submitted:
                # -------------------------
                # Guardrails
                # -------------------------
                self.guarded_action(
                    key="contact_submit",
                    cooldown=20,
                    max_chars=1_000,
                    text=message,
                )

                if not email or "@" not in email:
                    self.st.error(self.t("contact_form_error_email"))
                    self.st.stop()

                if not message.strip():
                    self.st.error(self.t("contact_form_error_message"))
                    self.st.stop()

                # -------------------------
                # Telemetry (no content logged)
                # -------------------------
                try:
                    self.record_event("contact_form_submit")
                    # Placeholder for future integration:
                    # send_email(...)
                    self.st.success(
                        self.t("contact_form_success")
                    )
                except Exception:
                    self.record_error("contact_form_error")
                    self.st.error(self.t("contact_form_error"))

    # -------------------------------------------------
    # Public mode notice
    # -------------------------------------------------
    def render_public_mode_notice(self):
        if self.PUBLIC_MODE:
            self.st.info(self.t('contact_public_mode_notice'))
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
    ContactPage().run()


if __name__ == "__main__":
    main()