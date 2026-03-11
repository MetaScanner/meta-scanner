import os
import json
import zipfile
import hashlib
import mimetypes
import win32com.client

import pandas as pd
import numpy as np

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from PIL import Image
from PyPDF2 import PdfReader

import sqlite3
import matplotlib.pyplot as plt
from flask import Flask, jsonify
import threading

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter import simpledialog


class MetaCollectorApp:

    def __init__(self, root):

        self.root = root
        root.title("AI Dataset Meta Collector v2")
        root.geometry("1300x750")

        self.meta_cache = {}
        self.file_paths = {}
        self.hash_index = {}

        self.conn = sqlite3.connect("meta_index.db", check_same_thread=False)
        self.create_db()


        # ---------------------------
        # 폴더 선택
        # ---------------------------

        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=5)

        self.folder_var = tk.StringVar()

        tk.Entry(top_frame, textvariable=self.folder_var, width=90).pack(side="left")

        tk.Button(top_frame, text="폴더 스캔",
                  command=self.scan_folder).pack(side="left", padx=5)

        tk.Button(top_frame, text="전체 메타 자동 수집",
                  command=self.collect_all_meta).pack(side="left", padx=5)

        tk.Button(top_frame, text="Dataset Summary 생성",
                  command=self.generate_dataset_summary).pack(side="left", padx=5)
        
        tk.Button(top_frame, text="메타 검색",
          command=self.search_meta).pack(side="left", padx=5)
        
        tk.Button(top_frame, text="Dataset 그래프",
          command=self.dataset_plot).pack(side="left", padx=5)
        
        tk.Button(top_frame, text="파일 미리보기",
          command=self.preview_file).pack(side="left", padx=5)
        
        tk.Button(top_frame, text="웹 대시보드",
          command=self.start_dashboard).pack(side="left", padx=5)

        # ---------------------------
        # 파일 목록
        # ---------------------------

        columns = ("name", "type", "size", "modified")

        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True)

        for c in columns:
            self.tree.heading(c, text=c)

        self.tree.bind("<<TreeviewSelect>>", self.show_meta)

        # ---------------------------
        # 버튼 영역
        # ---------------------------

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="선택 파일 메타 다운로드",
                  command=self.download_single).pack(side="left", padx=5)

        tk.Button(btn_frame, text="전체 메타 ZIP 다운로드",
                  command=self.download_all).pack(side="left", padx=5)

        tk.Button(btn_frame, text="메타 CSV 다운로드",
                  command=self.download_csv).pack(side="left", padx=5)

        # ---------------------------
        # 메타 테이블
        # ---------------------------

        meta_frame = tk.LabelFrame(root, text="Metadata")
        meta_frame.pack(fill="both", expand=True)

        self.meta_table = ttk.Treeview(meta_frame,
                                       columns=("key", "value"),
                                       show="headings")

        self.meta_table.heading("key", text="항목")
        self.meta_table.heading("value", text="값")

        self.meta_table.pack(fill="both", expand=True)

    # ------------------------------------------------
    # DB 생성
    # ------------------------------------------------

    def create_db(self):

        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS files(
            path TEXT PRIMARY KEY,
            name TEXT,
            ext TEXT,
            size INTEGER,
            sha256 TEXT,
            created TEXT,
            modified TEXT
        )
        """)

        self.conn.commit()

    # ------------------------------------------------
    # SHA256
    # ------------------------------------------------

    def file_hash(self, path):

        sha = hashlib.sha256()

        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)

        return sha.hexdigest()

    # ------------------------------------------------
    # Windows Explorer Metadata
    # ------------------------------------------------

    def get_windows_metadata(self, path):

        meta = {}

        try:

            shell = win32com.client.Dispatch("Shell.Application")

            folder = shell.Namespace(os.path.dirname(path))
            item = folder.ParseName(os.path.basename(path))

            for i in range(0, 200):

                key = folder.GetDetailsOf(None, i)

                if not key:
                    continue

                value = folder.GetDetailsOf(item, i)

                if value != "":
                    meta[key] = value

        except:
            pass

        return meta
    
    def search_meta(self):

        keyword = simpledialog.askstring("검색", "파일명 검색")

        if not keyword:
            return

        cur = self.conn.cursor()

        cur.execute("""
        SELECT path,name,ext,size,modified
        FROM files
        WHERE name LIKE ?
        """, (f"%{keyword}%",))

        rows = cur.fetchall()

        self.tree.delete(*self.tree.get_children())

        for r in rows:

            iid = self.tree.insert("", "end",
                values=(r[1], r[2], r[3], r[4]))

            self.file_paths[iid] = r[0]

    def preview_file(self):

        selected = self.tree.selection()

        if not selected:
            return

        path = self.file_paths[selected[0]]

        ext = os.path.splitext(path)[1].lower()

        win = tk.Toplevel(self.root)
        win.title("Preview")

        if ext in [".jpg",".jpeg",".png"]:

            from PIL import ImageTk

            img = Image.open(path)
            img = img.resize((500,400))

            photo = ImageTk.PhotoImage(img)

            label = tk.Label(win, image=photo)
            label.image = photo
            label.pack()

        elif ext in [".txt",".json",".csv"]:

            text = tk.Text(win)

            with open(path, encoding="utf-8", errors="ignore") as f:
                text.insert("1.0", f.read(5000))

            text.pack(fill="both", expand=True)

        else:

            tk.Label(win, text="Preview not supported").pack()

    def start_dashboard(self):

        def run():

            app = Flask(__name__)

            @app.route("/summary")
            def summary():

                total = len(self.meta_cache)

                types = {}

                for m in self.meta_cache.values():

                    ext = m.get("extension")

                    types[ext] = types.get(ext,0)+1

                return jsonify({
                    "total_files": total,
                    "file_types": types
                })

            app.run(port=5000)

        threading.Thread(target=run).start()

        messagebox.showinfo("Dashboard",
            "http://127.0.0.1:5000/summary")
        
    # ------------------------------------------------
    # Dataset 그래프
    # ------------------------------------------------

    def dataset_plot(self):

        if not self.meta_cache:

            messagebox.showinfo("알림", "먼저 메타데이터 수집 필요")
            return

        type_stats = {}

        for meta in self.meta_cache.values():

            ext = meta.get("extension", "unknown")

            type_stats[ext] = type_stats.get(ext, 0) + 1

        labels = list(type_stats.keys())
        values = list(type_stats.values())

        plt.figure(figsize=(8,5))

        plt.bar(labels, values)

        plt.title("File Type Distribution")
        plt.xlabel("File Type")
        plt.ylabel("Count")

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.show()

    # ------------------------------------------------
    # CSV 분석
    # ------------------------------------------------

    def analyze_dataframe(self, df):

        meta = {}

        meta["row_count"] = len(df)
        meta["column_count"] = len(df.columns)

        meta["columns"] = str(df.columns.tolist())
        meta["column_types"] = str(df.dtypes.astype(str).to_dict())

        meta["missing_total"] = int(df.isnull().sum().sum())
        meta["duplicate_rows"] = int(df.duplicated().sum())

        meta["unique_values"] = str(df.nunique().to_dict())

        try:
            meta["statistics"] = str(df.describe().to_dict())
        except:
            pass

        return meta

    # ------------------------------------------------
    # JSON depth
    # ------------------------------------------------

    def json_depth(self, obj):

        if isinstance(obj, dict):
            return 1 + max((self.json_depth(v) for v in obj.values()), default=0)

        if isinstance(obj, list):
            return 1 + max((self.json_depth(v) for v in obj), default=0)

        return 0

    # ------------------------------------------------
    # 메타 수집
    # ------------------------------------------------

    def collect_meta(self, path):

        stat = os.stat(path)

        sha = self.file_hash(path)

        meta = {

            "file_name": os.path.basename(path),
            "file_path": path,
            "extension": os.path.splitext(path)[1],
            "mime_type": mimetypes.guess_type(path)[0],
            "file_size": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime),
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
            "accessed_time": datetime.fromtimestamp(stat.st_atime),
            "sha256": sha
        }

        if sha in self.hash_index:
            meta["duplicate"] = True
        else:
            meta["duplicate"] = False
            self.hash_index[sha] = path

        meta["readonly"] = not os.access(path, os.W_OK)
        meta["hidden"] = os.path.basename(path).startswith(".")

        meta["windows_metadata"] = self.get_windows_metadata(path)

        ext = meta["extension"].lower()

        try:

            if ext == ".csv":

                df = pd.read_csv(path)

                meta.update(self.analyze_dataframe(df))

            elif ext in [".xlsx", ".xls"]:

                xl = pd.ExcelFile(path)
                meta["sheet_count"] = len(xl.sheet_names)

            elif ext == ".json":

                with open(path) as f:
                    data = json.load(f)

                meta["json_depth"] = self.json_depth(data)

            elif ext in [".jpg", ".jpeg", ".png"]:

                img = Image.open(path)

                meta["width"] = img.width
                meta["height"] = img.height
                meta["format"] = img.format

            elif ext == ".pdf":

                reader = PdfReader(path)

                meta["page_count"] = len(reader.pages)

                try:

                    info = reader.metadata

                    if info:
                        meta["pdf_author"] = str(info.author)
                        meta["pdf_title"] = str(info.title)

                except:
                    pass

        except Exception as e:

            meta["analysis_error"] = str(e)


        self.save_db(meta)
        return meta

    # ------------------------------------------------
    # 폴더 스캔
    # ------------------------------------------------

    def scan_folder(self):

        folder = filedialog.askdirectory()

        if not folder:
            return

        self.folder_var.set(folder)

        self.tree.delete(*self.tree.get_children())
        self.file_paths.clear()

        for root_dir, dirs, files in os.walk(folder):

            for file in files:

                path = os.path.join(root_dir, file)

                size = os.path.getsize(path)
                mtime = datetime.fromtimestamp(os.path.getmtime(path))

                ext = os.path.splitext(file)[1]

                iid = self.tree.insert("", "end",
                                       values=(file, ext, size, mtime))

                self.file_paths[iid] = path

    # ------------------------------------------------
    # 메타 표시
    # ------------------------------------------------

    def show_meta(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        path = self.file_paths[selected[0]]

        meta = self.collect_meta(path)

        self.meta_cache[path] = meta

        self.meta_table.delete(*self.meta_table.get_children())

        for k, v in meta.items():

            if isinstance(v, dict):

                for subk, subv in v.items():
                    self.meta_table.insert("", "end",
                        values=(f"{k}.{subk}", subv))

            else:

                self.meta_table.insert("", "end", values=(k, str(v)))

    # ------------------------------------------------
    # 전체 메타 수집
    # ------------------------------------------------

    def collect_all_meta(self):

        paths = list(self.file_paths.values())

        def worker(path):

            meta = self.collect_meta(path)

            self.meta_cache[path] = meta

        with ThreadPoolExecutor(max_workers=6) as exe:

            exe.map(worker, paths)

        messagebox.showinfo("완료", "모든 메타데이터 수집 완료")

    # ------------------------------------------------
    # Dataset Summary
    # ------------------------------------------------

    def generate_dataset_summary(self):

        if not self.meta_cache:

            messagebox.showinfo("알림", "먼저 메타데이터 수집 필요")
            return

        summary = {}

        total_files = len(self.meta_cache)
        total_size = 0

        type_stats = {}
        duplicate_files = []

        image_count = 0
        total_width = 0
        total_height = 0

        for path, meta in self.meta_cache.items():

            size = meta.get("file_size", 0)
            total_size += size

            ext = meta.get("extension", "").lower()

            type_stats[ext] = type_stats.get(ext, 0) + 1

            if meta.get("duplicate"):
                duplicate_files.append(path)

            if "width" in meta and "height" in meta:

                image_count += 1
                total_width += meta["width"]
                total_height += meta["height"]

        summary["total_files"] = total_files
        summary["total_size_bytes"] = total_size
        summary["total_size_gb"] = round(total_size / (1024**3), 2)

        summary["file_type_distribution"] = type_stats

        summary["duplicate_file_count"] = len(duplicate_files)
        summary["duplicate_files"] = duplicate_files

        if image_count > 0:

            summary["average_image_width"] = int(total_width / image_count)
            summary["average_image_height"] = int(total_height / image_count)

        save = filedialog.asksaveasfilename(defaultextension=".json")

        if not save:
            return

        with open(save, "w", encoding="utf-8") as f:

            json.dump(summary, f, indent=4, ensure_ascii=False)

        messagebox.showinfo("완료", "Dataset Summary 생성 완료")

    # ------------------------------------------------
    # 다운로드
    # ------------------------------------------------

    def download_single(self):

        selected = self.tree.selection()

        if not selected:
            return

        path = self.file_paths[selected[0]]

        meta = self.meta_cache.get(path)

        if not meta:
            messagebox.showinfo("알림", "먼저 메타데이터 수집 필요")
            return

        save = filedialog.asksaveasfilename(defaultextension=".json")

        if not save:
            return

        with open(save, "w", encoding="utf-8") as f:

            json.dump(meta, f, indent=4, default=str)

    def download_all(self):

        save = filedialog.asksaveasfilename(defaultextension=".zip")

        if not save:
            return

        with zipfile.ZipFile(save, "w") as z:

            for path, meta in self.meta_cache.items():

                name = os.path.basename(path) + ".json"

                z.writestr(name, json.dumps(meta, indent=4, default=str))

        messagebox.showinfo("완료", "ZIP 생성 완료")

    def download_csv(self):

        if not self.meta_cache:

            messagebox.showinfo("알림", "메타데이터 없음")
            return

        save = filedialog.asksaveasfilename(defaultextension=".csv")

        if not save:
            return

        df = pd.DataFrame(self.meta_cache.values())

        df.to_csv(save, index=False)

        messagebox.showinfo("완료", "CSV 저장 완료")

    def save_db(self, meta):

        cur = self.conn.cursor()

        cur.execute("""
        INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?)
        """, (
            meta["file_path"],
            meta["file_name"],
            meta["extension"],
            meta["file_size"],
            meta["sha256"],
            str(meta["created_time"]),
            str(meta["modified_time"])
        ))

        self.conn.commit()


root = tk.Tk()
app = MetaCollectorApp(root)
root.mainloop()