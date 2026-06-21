import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import config
import calc_engine
from ui_components import CollapsibleLogPanel

class ExileLedgerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ExileLedger - PoE2 智能推荐套利看板")
        self.root.geometry("1200x800")
        self.root.minimum_size = (1200, 800)
        self.root.configure(bg=config.THEME_COLORS["bg_dark"])

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.setup_styles()

        # 1. Initialize all reactive variables with hardcoded fallbacks first
        self.mode_var = tk.StringVar(value="E买D卖")
        self.d_to_e_var = tk.StringVar(value=config.DEFAULT_D_TO_E)
        self.gold_d_var = tk.StringVar(value=config.DEFAULT_GOLD_D)
        self.gold_e_var = tk.StringVar(value=config.DEFAULT_GOLD_E)
        self.cost_var = tk.StringVar(value=config.DEFAULT_COST)
        self.return_var = tk.StringVar(value=config.DEFAULT_RETURN)
        self.gold_item_var = tk.StringVar(value=config.DEFAULT_GOLD_ITEM)
        
        # Default snapshot row data
        self.target_list = [{"mode": "E买D卖", "cost": "330", "return": "1.55", "gold_item": 1200.0}]

        # 2. Safely load or generate the storage file
        self.load_or_create_storage()

        # 3. Assemble UI Layout
        self.build_ui()
        
        # Intercept app closure for auto-saving
        self.root.protocol("WM_DELETE_WINDOW", self.save_state_to_json)

        # 4. Attach reactive listeners for live calculations
        for var in [self.d_to_e_var, self.gold_d_var, self.gold_e_var, self.cost_var, self.return_var, self.gold_item_var]:
            var.trace_add("write", lambda *args: self.auto_calculate_current())
            
        self.auto_calculate_current()
        self.refresh_treeview()

    def setup_styles(self):
        c = config.THEME_COLORS
        f = config.FONT_FAMILY
        self.style.configure(".", background=c["bg_dark"], foreground=c["text_white"])
        self.style.configure("TLabelframe", background=c["bg_panel"], bordercolor=c["border"])
        self.style.configure("TLabelframe.Label", background=c["bg_panel"], foreground=c["accent_cyan"], font=(f, 10, "bold"))
        self.style.configure("TLabel", background=c["bg_panel"], foreground=c["text_gray"])
        self.style.configure("TEntry", fieldbackground=c["bg_input"], foreground=c["text_white"], bordercolor=c["border"])
        self.style.configure("TRadiobutton", background=c["bg_panel"], foreground=c["text_white"])
        self.style.configure("TButton", background=c["accent_blue"], foreground=c["text_white"], font=(f, 10, "bold"))
        self.style.map("TButton", background=[("active", "#0098ff")])
        self.style.configure("Treeview", background=c["bg_panel"], fieldbackground=c["bg_panel"], foreground=c["text_white"])
        self.style.configure("Treeview.Heading", background=c["bg_input"], foreground=c["accent_cyan"], relief="flat")

    def build_ui(self):
        # Left Workspace Panel Layout
        left_panel = ttk.Frame(self.root, style="TLabelframe", width=410, padding=12)
        left_panel.pack(side="left", fill="both", padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        # Section 1: Operation Mode Radios
        mode_frame = ttk.LabelFrame(left_panel, text=" 套利模式 ", padding=5)
        mode_frame.pack(fill="x", pady=4)
        for m in ["E买D卖", "D买E卖"]:
            r = ttk.Radiobutton(mode_frame, text=m, value=m, variable=self.mode_var, command=self.auto_calculate_current)
            r.pack(side="left", padx=20, pady=5)

        # Section 2: Core Market Indexes
        market_frame = ttk.LabelFrame(left_panel, text=" 市场基础价格与金币税 ", padding=10)
        market_frame.pack(fill="x", pady=4)
        ttk.Label(market_frame, text="1 D 换 E 数量:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(market_frame, textvariable=self.d_to_e_var, width=15).grid(row=0, column=1, padx=10, pady=4)
        ttk.Label(market_frame, text="1 D 交易金币:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(market_frame, textvariable=self.gold_d_var, width=15).grid(row=1, column=1, padx=10, pady=4)
        ttk.Label(market_frame, text="1 E 交易金币:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(market_frame, textvariable=self.gold_e_var, width=15).grid(row=2, column=1, padx=10, pady=4)

        # Section 3: Target Config Inputs
        item_frame = ttk.LabelFrame(left_panel, text=" 套利标的价格配置 ", padding=10)
        item_frame.pack(fill="x", pady=4)
        self.lbl_cost = ttk.Label(item_frame, text="买入价 (每个支付 E 或 比例):")
        self.lbl_cost.grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(item_frame, textvariable=self.cost_var, width=15).grid(row=0, column=1, padx=10, pady=4)
        self.lbl_return = ttk.Label(item_frame, text="卖出价 (每个换D 或 比例):")
        self.lbl_return.grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(item_frame, textvariable=self.return_var, width=15).grid(row=1, column=1, padx=10, pady=4)
        ttk.Label(item_frame, text="标的物自身金币税:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(item_frame, textvariable=self.gold_item_var, width=15).grid(row=2, column=1, padx=10, pady=4)

        tk.Button(left_panel, text="➕ 记录当前配置到快照盘", command=self.add_current_to_list,
                  bg=config.THEME_COLORS["accent_blue"], fg="white", font=(config.FONT_FAMILY, 10, "bold"), bd=0, height=2).pack(fill="x", pady=6)

        # Section 4: Live Output Terminal Framework
        res_frame = ttk.LabelFrame(left_panel, text=" 📊 实时监测与智能挂单推荐 ", padding=10)
        res_frame.pack(fill="both", expand=True, pady=4)

        self.lbl_roi = tk.Label(res_frame, text="ROI: --", font=(config.FONT_FAMILY, 14, "bold"), bg=config.THEME_COLORS["bg_panel"], fg="white")
        self.lbl_roi.pack(anchor="w", pady=2)
        self.lbl_gold_per_d = tk.Label(res_frame, text="消耗：-- / D", font=(config.FONT_FAMILY, 12, "bold"), bg=config.THEME_COLORS["bg_panel"], fg=config.THEME_COLORS["accent_green"])
        self.lbl_gold_per_d.pack(anchor="w", pady=2)
        self.lbl_quick_details = tk.Label(res_frame, text="智能挂单计算中...", font=(config.FONT_FAMILY, 9), bg=config.THEME_COLORS["bg_panel"], fg=config.THEME_COLORS["accent_orange"], justify="left", anchor="w")
        self.lbl_quick_details.pack(fill="x", pady=2)

        self.log_panel = CollapsibleLogPanel(res_frame)
        self.log_panel.pack(fill="both", expand=True, pady=2)

        # Right Dashboard Panel Layout
        right_panel = ttk.Frame(self.root, padding=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        tk.Label(right_panel, text="📋 历史追踪对比快照盘 (💡 单击任意行加载配置 | 双击移除)", 
                 font=(config.FONT_FAMILY, 11, "bold"), 
                 bg=config.THEME_COLORS["bg_dark"], fg="white", anchor="w").pack(fill="x", pady=5)

        columns = ("id", "mode", "cost", "return", "roi", "gold_cost")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="编号")
        self.tree.heading("mode", text="模式")
        self.tree.heading("cost", text="买入价")
        self.tree.heading("return", text="卖出价")
        self.tree.heading("roi", text="ROI")
        self.tree.heading("gold_cost", text="综合金币消耗 (/D)")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("mode", width=70, anchor="center")
        self.tree.column("cost", width=90, anchor="center")
        self.tree.column("return", width=90, anchor="center")
        self.tree.column("roi", width=80, anchor="center")
        self.tree.column("gold_cost", width=160, anchor="w")
        
        self.tree.pack(fill="both", expand=True)
        
        # Bindings: Single-click to IMPORT, Double-click to REMOVE
        self.tree.bind("<<TreeviewSelect>>", self.on_table_single_click)
        self.tree.bind("<Double-1>", self.on_table_double_click)

    def auto_calculate_current(self, *args):
        try:
            mode = self.mode_var.get()
            if mode == "E买D卖":
                self.lbl_cost.config(text="买入价 (每个支付 E 或 比例):")
                self.lbl_return.config(text="卖出价 (每个换D 或 比例):")
            else:
                self.lbl_cost.config(text="买入价 (每个支付 D 或 比例):")
                self.lbl_return.config(text="卖出价 (每个换E 或 比例):")

            d_to_e = float(self.d_to_e_var.get() or 0)
            gold_d = float(self.gold_d_var.get() or 0)
            gold_e = float(self.gold_e_var.get() or 0)
            
            cost = calc_engine.parse_ratio(self.cost_var.get() or "")
            return_val = calc_engine.parse_ratio(self.return_var.get() or "")
            gold_item = float(self.gold_item_var.get() or 0)
            
            res = calc_engine.run_arbitrage_calc(mode, d_to_e, gold_d, gold_e, cost, return_val, gold_item)
            
            if res is None:
                self.lbl_roi.config(text="ROI: 数据不全", fg="#aeaeae")
                return

            roi = res["roi"]
            self.lbl_roi.config(text=f"ROI 利润率: {roi:+.2f}%", fg=config.THEME_COLORS["accent_green"] if roi > 0 else config.THEME_COLORS["accent_red"])
            
            if res["gold"] == float('inf'):
                self.lbl_gold_per_d.config(text="消耗：亏损状态 / D", fg=config.THEME_COLORS["accent_red"])
            else:
                self.lbl_gold_per_d.config(text=f"消耗：{res['gold']/10000:.2f}万/D", fg=config.THEME_COLORS["accent_green"])
                
            self.lbl_quick_details.config(text=res["details"])
            self.log_panel.update_logs(res["logs"])
            
        except ValueError:
            self.lbl_roi.config(text="ROI: 等待合法数字...", fg=config.THEME_COLORS["text_dark_gray"])

    # --- 替换 main.py 中的 refresh_treeview 方法内循环部分 ---
    def refresh_treeview(self):
        for item in self.tree.get_children(): 
            self.tree.delete(item)
        try:
            d_to_e = float(self.d_to_e_var.get() or 0)
            gold_d = float(self.gold_d_var.get() or 0)
            gold_e = float(self.gold_e_var.get() or 0)
        except: 
            return

        # --- Replace the loop inside refresh_treeview ---
        for idx, item in enumerate(self.target_list):
            c_val = calc_engine.parse_ratio(str(item["cost"]))
            r_val = calc_engine.parse_ratio(str(item["return"]))
            res = calc_engine.run_arbitrage_calc(item["mode"], d_to_e, gold_d, gold_e, c_val, r_val, item["gold_item"])
            if res:
                roi_str = f"{res['roi']:+.2f}%"
                gold_str = f"亏损/D" if res["gold"] == float('inf') else f"{res['gold']/10000:.2f}万/D"
            else:
                roi_str, gold_str = "错误", "数据异常"
                
            # Maps exact parameters across all 6 tracking columns
            self.tree.insert("", "end", iid=str(idx), values=(
                f"方案 {idx+1}", 
                item["mode"], 
                item["cost"], 
                item["return"], 
                roi_str, 
                gold_str
            ))

    def add_current_to_list(self):
        try:
            self.target_list.append({
                "mode": self.mode_var.get(), 
                "cost": self.cost_var.get(), 
                "return": self.return_var.get(), 
                "gold_item": float(self.gold_item_var.get() or 0)
            })
            self.refresh_treeview()
        except Exception as e: 
            messagebox.showerror("错误", str(e))

    def on_table_double_click(self, event):
        item_id = self.tree.selection()
        if item_id:
            idx = int(item_id[0])
            if 0 <= idx < len(self.target_list):
                del self.target_list[idx]
                self.refresh_treeview()

    def on_table_single_click(self, event):
        """Imports a selected snapshot template configuration back into active UI components"""
        selection = self.tree.selection()
        if not selection:
            return
            
        idx = int(selection[0])
        if 0 <= idx < len(self.target_list):
            item = self.target_list[idx]
            
            # Temporarily unbind or block trace updates if needed, but standard 
            # tk.StringVar modifications handle downstream calculation loops gracefully
            self.mode_var.set(item["mode"])
            self.cost_var.set(str(item["cost"]))
            self.return_var.set(str(item["return"]))
            self.gold_item_var.set(str(int(item["gold_item"])))

    # --- Robust Storage Controller Pipeline ---
    def load_or_create_storage(self):
        """
        Handles storage verification safely. Creates a fresh file if it doesn't exist.
        Resets and warns the user if it detects corrupt JSON configurations.
        """
        # If file doesn't exist, generate a clean default one immediately
        if not os.path.exists(config.SAVE_FILE):
            self.execute_silent_save()
            return
        
        # If file exists, attempt parsing its contents
        try:
            with open(config.SAVE_FILE, "r", encoding="utf-8") as f:
                state_data = json.load(f)
                
            inputs = state_data.get("inputs", {})
            self.mode_var.set(inputs.get("mode", "E买D卖"))
            self.d_to_e_var.set(inputs.get("d_to_e", config.DEFAULT_D_TO_E))
            self.gold_d_var.set(inputs.get("gold_d", config.DEFAULT_GOLD_D))
            self.gold_e_var.set(inputs.get("gold_e", config.DEFAULT_GOLD_E))
            self.cost_var.set(inputs.get("cost", config.DEFAULT_COST))
            self.return_var.set(inputs.get("return", config.DEFAULT_RETURN))
            self.gold_item_var.set(inputs.get("gold_item", config.DEFAULT_GOLD_ITEM))
            
            self.target_list = state_data.get("history_snapshots", [])
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # File exists but is corrupt or invalid -> trigger alert, wipe out bad state, write clean setup
            print(f"[Storage Warning] Corrupted store profile wiped out. Resetting defaults. Info: {e}")
            self.execute_silent_save()

    def execute_silent_save(self):
        """Saves current memory structures out to the local JSON file path target."""
        state_data = {
            "inputs": {
                "mode": self.mode_var.get(),
                "d_to_e": self.d_to_e_var.get(),
                "gold_d": self.gold_d_var.get(),
                "gold_e": self.gold_e_var.get(),
                "cost": self.cost_var.get(),
                "return": self.return_var.get(),
                "gold_item": self.gold_item_var.get()
            },
            "history_snapshots": self.target_list
        }
        try:
            with open(config.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Failed handling file save execution trace: {e}")

    def save_state_to_json(self):
        """Standard window exit flush handler wrapping system destruction hooks."""
        self.execute_silent_save()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExileLedgerApp(root)
    root.mainloop()