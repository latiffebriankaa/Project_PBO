"""Entry point aplikasi GUI BeresFile."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path
from collections import Counter

import config
from rules.rule_ekstensi import RuleEkstensi
from rules.rule_ai import RuleAI
from services.file_organizer import FileOrganizer
from utils.logger import save_log, save_json_log


class BeresFileApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BeresFile - Smart File Organizer")
        self.root.geometry("950x620")
        self.root.minsize(850, 520)
        self.root.configure(bg="#f8fafc")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure TNotebook (Tabs)
        self.style.configure("TNotebook", background="#ffffff", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#f1f5f9", foreground="#64748b", padding=(14, 6), font=("Segoe UI", 9, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab", background=[("selected", "#ffffff"), ("active", "#e2e8f0")], foreground=[("selected", "#0f172a"), ("active", "#0f172a")])
        
        # Configure Treeview (Table)
        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=26, background="#ffffff", fieldbackground="#ffffff", foreground="#0f172a", borderwidth=0)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#f1f5f9", foreground="#0f172a", borderwidth=0)
        self.style.map("Treeview", background=[("selected", "#3b82f6")], foreground=[("selected", "#ffffff")])
        self.style.map("Treeview.Heading", background=[("active", "#e2e8f0")], foreground=[("active", "#0f172a")])

        # State variables
        self.scan_dir_var = tk.StringVar(value=config.SCAN_DIR)
        self.dry_run_var = tk.BooleanVar(value=config.DRY_RUN)
        self.use_ai_var = tk.BooleanVar(value=config.ENABLE_AI)
        self.status_var = tk.StringVar(value="Siap")
        self.stats_var = tk.StringVar(value="Total: 0 | Berhasil: 0 | Error: 0")
        self.mode_var = tk.StringVar(value="Dry-Run")
        self.folder_var = tk.StringVar(value=self.scan_dir_var.get())
        self.total_var = tk.StringVar(value="0")
        self.processed_var = tk.StringVar(value="0")
        self.duplicate_var = tk.StringVar(value="0")
        self.error_var = tk.StringVar(value="0")

        self._build_ui()

    def _build_ui(self):
        # Root layout container
        root_container = tk.Frame(self.root, bg="#f8fafc")
        root_container.pack(fill="both", expand=True)

        # 1. Left Sidebar
        self.sidebar = tk.Frame(root_container, bg="#ffffff", width=260, padx=16, pady=16, highlightbackground="#e2e8f0", highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar Header / Logo
        logo_frame = tk.Frame(self.sidebar, bg="#ffffff")
        logo_frame.pack(fill="x", pady=(0, 16))
        
        logo_lbl = tk.Label(logo_frame, text="⚡ BeresFile", fg="#3b82f6", bg="#ffffff", font=("Segoe UI", 16, "bold"))
        logo_lbl.pack(anchor="w")
        
        sub_logo_lbl = tk.Label(logo_frame, text="Smart File Organizer & Renamer", fg="#64748b", bg="#ffffff", font=("Segoe UI", 8))
        sub_logo_lbl.pack(anchor="w", pady=(1, 0))

        sep = tk.Frame(self.sidebar, bg="#e2e8f0", height=1)
        sep.pack(fill="x", pady=(0, 16))

        # Folder Target Section
        lbl_folder = tk.Label(self.sidebar, text="📁 FOLDER TARGET", fg="#64748b", bg="#ffffff", font=("Segoe UI", 8, "bold"))
        lbl_folder.pack(anchor="w")

        folder_entry_frame = tk.Frame(self.sidebar, bg="#cbd5e1", padx=1, pady=1)
        folder_entry_frame.pack(fill="x", pady=(6, 10))

        self.entry_folder = tk.Entry(
            folder_entry_frame,
            textvariable=self.scan_dir_var,
            bg="#f8fafc",
            fg="#0f172a",
            insertbackground="#0f172a",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
            highlightthickness=0
        )
        self.entry_folder.pack(fill="x", ipady=6, padx=6)

        btn_choose = self._create_flat_button(
            self.sidebar,
            text="Pilih Folder...",
            bg="#f1f5f9",
            fg="#0f172a",
            hover_bg="#e2e8f0",
            command=self._choose_folder
        )
        btn_choose.pack(fill="x", pady=(0, 16))

        # Options Section
        lbl_options = tk.Label(self.sidebar, text="⚙️ OPSI PEMROSESAN", fg="#64748b", bg="#ffffff", font=("Segoe UI", 8, "bold"))
        lbl_options.pack(anchor="w", pady=(0, 4))

        self._make_toggle(self.sidebar, "Dry-Run / Mode Simulasi", self.dry_run_var)
        self._make_toggle(self.sidebar, "Aktifkan AI Vision", self.use_ai_var)

        sep2 = tk.Frame(self.sidebar, bg="#e2e8f0", height=1)
        sep2.pack(fill="x", pady=16)

        # Actions Section (Sidebar Buttons)
        btn_run = self._create_flat_button(
            self.sidebar,
            text="🚀 Jalankan Proses",
            bg="#10b981",
            fg="#ffffff",
            hover_bg="#059669",
            command=self._run_process
        )
        btn_run.pack(fill="x", pady=4)

        btn_undo = self._create_flat_button(
            self.sidebar,
            text="🔄 Undo Terakhir",
            bg="#f1f5f9",
            fg="#0f172a",
            hover_bg="#e2e8f0",
            command=self._undo_last_run
        )
        btn_undo.pack(fill="x", pady=4)

        btn_clear = self._create_flat_button(
            self.sidebar,
            text="🧹 Bersihkan Log",
            bg="#f1f5f9",
            fg="#0f172a",
            hover_bg="#e2e8f0",
            command=self._clear_log
        )
        btn_clear.pack(fill="x", pady=4)

        # 2. Main Content
        self.main_content = tk.Frame(root_container, bg="#f8fafc", padx=16, pady=16)
        self.main_content.pack(side="right", fill="both", expand=True)

        # Status Bar (Bottom of Main Content)
        status_bar_frame = tk.Frame(self.main_content, bg="#ffffff", padx=12, pady=6, highlightbackground="#e2e8f0", highlightthickness=1)
        status_bar_frame.pack(side="bottom", fill="x", pady=(12, 0))

        lbl_status = tk.Label(status_bar_frame, textvariable=self.status_var, fg="#64748b", bg="#ffffff", font=("Segoe UI", 9))
        lbl_status.pack(side="left")

        # Folder Status Banner
        folder_status_frame = tk.Frame(self.main_content, bg="#ffffff", padx=12, pady=8, highlightbackground="#e2e8f0", highlightthickness=1)
        folder_status_frame.pack(side="top", fill="x", pady=(0, 12))

        lbl_folder_title = tk.Label(folder_status_frame, text="FOLDER AKTIF SAAT INI", fg="#64748b", bg="#ffffff", font=("Segoe UI", 8, "bold"))
        lbl_folder_title.pack(anchor="w")

        lbl_folder_path = tk.Label(folder_status_frame, textvariable=self.folder_var, fg="#0f172a", bg="#ffffff", font=("Segoe UI", 10, "bold"))
        lbl_folder_path.pack(anchor="w", pady=(2, 0))

        # Stats Cards Grid
        status_strip = tk.Frame(self.main_content, bg="#f8fafc")
        status_strip.pack(side="top", fill="x", pady=(0, 12))
        status_strip.columnconfigure((0, 1, 2, 3, 4), weight=1)

        self._stat_chip(status_strip, 0, "Mode", self.mode_var, "#3b82f6")
        self._stat_chip(status_strip, 1, "Total File", self.total_var, "#0f172a")
        self._stat_chip(status_strip, 2, "Diproses", self.processed_var, "#10b981")
        self._stat_chip(status_strip, 3, "Duplikat", self.duplicate_var, "#b45309")
        self._stat_chip(status_strip, 4, "Error", self.error_var, "#ef4444")

        # Tabs Container
        notebook_container = tk.Frame(self.main_content, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
        notebook_container.pack(side="top", fill="both", expand=True)

        notebook = ttk.Notebook(notebook_container)
        notebook.pack(fill="both", expand=True, padx=2, pady=2)

        summary_tab = tk.Frame(notebook, bg="#ffffff", padx=8, pady=8)
        log_tab = tk.Frame(notebook, bg="#ffffff", padx=8, pady=8)

        notebook.add(summary_tab, text="📊 Ringkasan Kategori")
        notebook.add(log_tab, text="📝 Log Aktivitas")

        # Tab 1: Ringkasan content
        summary_body = tk.Frame(summary_tab, bg="#ffffff")
        summary_body.pack(fill="both", expand=True)
        summary_body.columnconfigure(0, weight=1)
        summary_body.rowconfigure(0, weight=1)

        self.category_tree = ttk.Treeview(summary_body, columns=("kategori", "jumlah"), show="headings", height=10)
        self.category_tree.heading("kategori", text="Kategori Berkas")
        self.category_tree.heading("jumlah", text="Jumlah Berkas")
        self.category_tree.column("kategori", width=300, anchor="w")
        self.category_tree.column("jumlah", width=120, anchor="center")
        self.category_tree.grid(row=0, column=0, sticky="nsew")

        category_scroll = ttk.Scrollbar(summary_body, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=category_scroll.set)
        category_scroll.grid(row=0, column=1, sticky="ns")

        # Tab 2: Log content
        self.log_text = scrolledtext.ScrolledText(
            log_tab,
            wrap="word",
            font=("Consolas", 10),
            bg="#f1f5f9",
            fg="#1e293b",
            insertbackground="#0f172a",
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.log_text.pack(fill="both", expand=True)

        # Configure color tags for Terminal Log (Premium Light Theme)
        self.log_text.tag_configure("normal", foreground="#334155")
        self.log_text.tag_configure("dry_run", foreground="#2563eb")
        self.log_text.tag_configure("ok", foreground="#059669")
        self.log_text.tag_configure("error", foreground="#dc2626")
        self.log_text.tag_configure("warning", foreground="#d97706")
        self.log_text.tag_configure("info", foreground="#7c3aed")

        # Lock log text to read-only by default
        self.log_text.configure(state="disabled")

        # Initial state setup
        self.folder_var.set(self.scan_dir_var.get())
        self._write_log("BeresFile siap digunakan. Pilih folder lalu klik Jalankan.")
        self._refresh_category_summary([])

    def _create_flat_button(self, parent, text, bg, fg, hover_bg, command):
        btn = tk.Button(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            command=command,
            cursor="hand2",
            padx=10,
            pady=8
        )
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn

    def _make_toggle(self, parent, text, variable):
        chk = tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            bg="#ffffff",
            fg="#0f172a",
            activebackground="#ffffff",
            activeforeground="#0f172a",
            selectcolor="#ffffff",
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        chk.pack(anchor="w", pady=4)

    def _stat_chip(self, parent, column, label, variable, text_color):
        chip = tk.Frame(parent, bg="#ffffff", padx=12, pady=8, highlightbackground="#e2e8f0", highlightthickness=1)
        chip.grid(row=0, column=column, sticky="nsew", padx=3)
        parent.columnconfigure(column, weight=1)
        
        lbl = tk.Label(chip, text=label.upper(), bg="#ffffff", fg="#64748b", font=("Segoe UI", 8, "bold"))
        lbl.pack(anchor="w")
        
        val = tk.Label(chip, textvariable=variable, bg="#ffffff", fg=text_color, font=("Segoe UI", 13, "bold"))
        val.pack(anchor="w", pady=(2, 0))

    def _choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.scan_dir_var.get() or str(Path.home()))
        if folder:
            self.scan_dir_var.set(folder)
            self.folder_var.set(folder)

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
        self.status_var.set("Log dibersihkan")
        self.stats_var.set("Total: 0 | Berhasil: 0 | Error: 0")
        self.total_var.set("0")
        self.processed_var.set("0")
        self.duplicate_var.set("0")
        self.error_var.set("0")
        self._refresh_category_summary([])

    def _write_log(self, text: str):
        self.log_text.configure(state="normal")
        tag = "normal"
        if text.startswith("[DRY-RUN]"):
            tag = "dry_run"
        elif text.startswith("[OK]") or text.startswith("[UNDO]"):
            tag = "ok"
        elif text.startswith("[ERROR]"):
            tag = "error"
        elif text.startswith("[DUPLICATE]") or text.startswith("[SKIP]"):
            tag = "warning"
        elif text.startswith("Mode:") or text.startswith("BeresFile siap"):
            tag = "info"
        
        self.log_text.insert(tk.END, text + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def _refresh_category_summary(self, actions):
        for row in self.category_tree.get_children():
            self.category_tree.delete(row)

        counts = Counter(action.get("category", "Lainnya") for action in actions)
        if not counts:
            self.category_tree.insert("", tk.END, values=("Belum ada data", 0))
            return

        for category, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            self.category_tree.insert("", tk.END, values=(category, count))

    def _run_process(self):
        scan_dir = self.scan_dir_var.get().strip()
        if not scan_dir:
            messagebox.showwarning("Peringatan", "Silakan pilih folder target terlebih dahulu.")
            return

        rules = [RuleEkstensi()]
        if self.use_ai_var.get() and config.GEMINI_API_KEY.strip():
            rules.insert(0, RuleAI(config.GEMINI_API_KEY, config.GEMINI_MODEL))

        organizer = FileOrganizer(
            rules=rules,
            dry_run=self.dry_run_var.get(),
            output_root_name=config.OUTPUT_ROOT_NAME,
        )

        try:
            result = organizer.process_directory(scan_dir)
            self._clear_log()
            for line in result.logs:
                self._write_log(line)

            log_path = save_log(result.logs, scan_dir)
            manifest_path = Path(result.manifest_path)
            mode = "Dry-Run" if self.dry_run_var.get() else "Eksekusi nyata"
            summary = (
                f"Mode: {mode} | Total: {result.total} | Berhasil: {result.processed} | "
                f"Duplikat: {result.duplicates} | Error: {result.errors} | Log: {log_path.name} | Manifest: {manifest_path.name}"
            )
            self.status_var.set(summary)
            self.stats_var.set(
                f"Total: {result.total} | Berhasil: {result.processed} | Duplikat: {result.duplicates} | Error: {result.errors}"
            )
            self.total_var.set(str(result.total))
            self.processed_var.set(str(result.processed))
            self.duplicate_var.set(str(result.duplicates))
            self.error_var.set(str(result.errors))
            self.mode_var.set("Dry-Run" if self.dry_run_var.get() else "Eksekusi")
            self.folder_var.set(scan_dir)
            self._refresh_category_summary(result.actions)
            self._write_log("-")
            self._write_log(summary)
            messagebox.showinfo("Selesai", summary)
        except Exception as exc:
            self.status_var.set(f"Gagal: {exc}")
            messagebox.showerror("Error", str(exc))

    def _undo_last_run(self):
        scan_dir = self.scan_dir_var.get().strip()
        if not scan_dir:
            messagebox.showwarning("Peringatan", "Folder target belum dipilih.")
            return

        organizer = FileOrganizer(
            rules=[RuleEkstensi()],
            dry_run=False,
            output_root_name=config.OUTPUT_ROOT_NAME,
        )

        try:
            undo_logs, manifest_path = organizer.undo_last_run(scan_dir)
            self._clear_log()
            self._write_log(f"Undo menggunakan manifest: {manifest_path.name}")
            for line in undo_logs:
                self._write_log(line)
            self.status_var.set("Undo selesai")
            self.stats_var.set(f"Undo dijalankan | Log: {manifest_path.name}")
            self.mode_var.set("Undo")
            messagebox.showinfo("Undo selesai", "Perubahan terakhir berhasil dibatalkan.")
        except Exception as exc:
            self.status_var.set(f"Undo gagal: {exc}")
            messagebox.showerror("Undo gagal", str(exc))


def main():
    root = tk.Tk()
    app = BeresFileApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
