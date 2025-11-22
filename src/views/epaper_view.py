# src/ui/epaper_view.py
```
"""View to render text to e-paper adapter."""
class EpaperView:
    def __init__(self, adapter):
        self.adapter = adapter

    def render_text(self, text: str):
        self.adapter.show_text(text)