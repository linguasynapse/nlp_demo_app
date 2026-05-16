# pages/Home.py
from base_page import BasePage

class HomePage(BasePage):
    def run(self):
        # Page setup
        self.process_events()
        self.inject_tokens()     # global design tokens
        # Inject page-specific CSS
        self.inject_css("""
            .metric-highlight {
                color: #0072ff;
                font-weight: bold;
            }
        """)

        # Hero section
        image_path = self.Path("ui/assets") / "linguasynapse_08.jpg"
        self.hero(
            title_key="home_title",
            subtitle_key="home_intro",
            image=image_path
        )

        # Section header
        self.section("home_metrics")

        # Page-level state example
        self.state["visits"] = self.state.get("visits", 0) + 1
        self.st.info(f"Page visits this session: {self.state['visits']}")

        # Metrics
        cols = self.st.columns(3)
        cols[0].metric(self.t("home_delivery_time"), self.t("home_hours"), self.t("home_50"))
        cols[1].metric(self.t("home_cost"), self.t("home_dollars"), self.t("home_50"))
        cols[2].metric(self.t("home_quality"), self.t("home_98"), self.t("home_qoq"))


def main():
    HomePage().run()


if __name__ == "__main__":
    main()
