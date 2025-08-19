
from pathlib import Path
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog

import dynamicdatab


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dynamic DB Manager")
        self.geometry("800x600")

        self.manager = dynamicdatab.DatabaseManager()

        self._build_widgets()
        self.refresh_db_listbox()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------
    def _build_widgets(self):
        # ----- Database frame -----
        db_frame = ttk.LabelFrame(self, text="Databases")
        db_frame.pack(fill="x", padx=10, pady=5)

        self.db_listbox = tk.Listbox(db_frame, height=4)
        self.db_listbox.pack(side="left", expand=True, fill="x", padx=(10, 0), pady=5)

        btn_frame = ttk.Frame(db_frame)
        btn_frame.pack(side="left", padx=10)

        ttk.Button(btn_frame, text="Connect", command=self.connect_to_selected_db).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Create DB", command=self.prompt_create_db).pack(fill="x", pady=2)

        self.selected_db_var = tk.StringVar(value="None")
        ttk.Label(db_frame, textvariable=self.selected_db_var, foreground="blue").pack(side="right", padx=10)
    
        # ----- Table creation frame -----
        tbl_frame = ttk.LabelFrame(self, text="Create Table")
        tbl_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(tbl_frame, text="Table name:").pack(side="left", padx=5)
        self.table_name_entry = ttk.Entry(tbl_frame, width=15)
        self.table_name_entry.pack(side="left", padx=5)

        ttk.Label(tbl_frame, text="Columns (name TYPE, ...):").pack(side="left", padx=5)
        self.columns_entry = ttk.Entry(tbl_frame, width=50)
        self.columns_entry.pack(side="left", padx=5, expand=True, fill="x")

        ttk.Button(tbl_frame, text="Create", command=self.create_table).pack(side="left", padx=5)

        # ----- SQL execution frame -----
        sql_frame = ttk.LabelFrame(self, text="Execute SQL")
        sql_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.sql_entry = scrolledtext.ScrolledText(sql_frame, height=5)
        self.sql_entry.pack(fill="x", padx=5, pady=5)

        ttk.Button(sql_frame, text="Run", command=self.run_sql).pack(pady=5)

        self.result_text = scrolledtext.ScrolledText(sql_frame, height=10, state="disabled")
        self.result_text.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    # ------------------------------------------------------------------
    # Database actions
    # ------------------------------------------------------------------
    def refresh_db_listbox(self):
        self.db_listbox.delete(0, tk.END)
        for name in sorted(self.manager.databases):
            self.db_listbox.insert(tk.END, name)

    def prompt_create_db(self):
        name = simpledialog.askstring("Create Database", "Enter new database name:")
        if not name:
            return
        self.manager.create_database(name)
        self.refresh_db_listbox()
        self.selected_db_var.set(f"Selected: {name}")

    def connect_to_selected_db(self):
        try:
            idx = self.db_listbox.curselection()[0]
        except IndexError:
            messagebox.showerror("Error", "Select a database from list.")
            return
        db_name = self.db_listbox.get(idx)
        self.manager.connect_to_database(db_name)
        self.selected_db_var.set(f"Selected: {db_name}")

    # ------------------------------------------------------------------
    # Table operations
    # ------------------------------------------------------------------
    def create_table(self):
        table_name = self.table_name_entry.get().strip()
        columns_raw = self.columns_entry.get().strip()
        if not table_name or not columns_raw:
            messagebox.showerror("Error", "Provide table name and columns definition.")
            return
        # Parse columns: split by comma, treat first space as delimiter between name and type
        columns = {}
        for col_chunk in columns_raw.split(","):
            if not col_chunk.strip():
                continue
            try:
                name, ctype = col_chunk.strip().split(None, 1)
            except ValueError:
                messagebox.showerror("Error", f"Invalid column definition: '{col_chunk}'. Use 'name TYPE'.")
                return
            columns[name] = ctype
        self.manager.create_table(table_name, columns)
        messagebox.showinfo("Success", f"Table '{table_name}' created (if it did not already exist).")

    # ------------------------------------------------------------------
    # SQL execution
    # ------------------------------------------------------------------
    def run_sql(self):
        if not self.manager.selected_db:
            messagebox.showerror("Error", "No database selected.")
            return
        sql = self.sql_entry.get("1.0", tk.END).strip()
        if not sql:
            return
        con = self.manager.databases[self.manager.selected_db]
        cursor = con.cursor()
        try:
            cursor.execute(sql)
            con.commit()
            if sql.lower().startswith("select"):
                rows = cursor.fetchall()
                self.display_results(rows)
            else:
                self.display_results([[f"Query executed. Rows affected: {cursor.rowcount}"]])
        except sqlite3.Error as e:
            messagebox.showerror("SQL Error", str(e))

    def display_results(self, rows):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        for row in rows:
            self.result_text.insert(tk.END, f"{row}\n")
        self.result_text.configure(state="disabled")


if __name__ == "__main__":
    App().mainloop()
