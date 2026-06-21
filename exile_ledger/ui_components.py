import tkinter as tk
from config import THEME_COLORS, FONT_FAMILY

class CollapsibleLogPanel(tk.Frame):
    """
    Custom composite Tkinter component that manages expanding and collapsing 
    real-time calculation log traces to keep UI clutter-free.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=THEME_COLORS["bg_panel"], **kwargs)
        self.is_expanded = False

        # Interactivity trigger label
        self.toggle_lbl = tk.Label(
            self, text="▶ 点击展开底层计算过程明细", 
            font=(FONT_FAMILY, 9, "underline"), 
            bg=THEME_COLORS["bg_panel"], fg=THEME_COLORS["accent_cyan"], 
            cursor="hand2"
        )
        self.toggle_lbl.pack(anchor="w", pady=5)
        self.toggle_lbl.bind("<Button-1>", self.toggle_state)

        # Logging textbox viewport
        self.txt_logs = tk.Text(
            self, bg=THEME_COLORS["bg_dark"], fg=THEME_COLORS["log_green"], 
            font=("Consolas", 9), bd=0, highlightthickness=0, height=8
        )

    def toggle_state(self, event=None):
        """Toggles layout packaging packing layouts depending on internal flag state"""
        if self.is_expanded:
            self.txt_logs.pack_forget()
            self.toggle_lbl.config(text="▶ 点击展开底层计算过程明细")
            self.is_expanded = False
        else:
            self.txt_logs.pack(fill="both", expand=True, pady=2)
            self.toggle_lbl.config(text="▼ 隐藏明细")
            self.is_expanded = True

    def update_logs(self, log_text):
        """Thread-safe pipeline updating text content dynamically"""
        self.txt_logs.config(state="normal")
        self.txt_logs.delete("1.0", "end")
        self.txt_logs.insert("1.0", log_text)
        self.txt_logs.config(state="disabled")