# ui/styles.py

ANIMATION_CSS = """
<style>
.fade-in {
    animation: ls-fade-in 0.4s ease-out;
}

.slide-up {
    animation: ls-slide-up 0.35s ease-out;
}

@keyframes ls-fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes ls-slide-up {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
"""
