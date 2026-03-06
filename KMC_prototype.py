import os
import json
import zipfile
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from PIL import Image
from PyPDF2 import PdfReader

import tkinter as tk
from tkinter import filedialog, ttk, messagebox


class MetaCollectorApp:

    def __init__(self, root):

        self.root = root
        root.title("AI Dataset Meta Collector")
        root.geometry("1300x750")

        self.meta_cache = {}
        self.file_paths = {}

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
    # 파일 SHA256
    # ------------------------------------------------

    def file_hash(self, path):

        sha = hashlib.sha256()

        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha.update(chunk)

        return sha.hexdigest()

    # ------------------------------------------------
    # CSV 안전 읽기
    # ------------------------------------------------

    def read_csv_safe(self, path):

        for enc in ["utf-8", "cp949", "euc-kr"]:

            try:
                return pd.read_csv(path, encoding=enc)
            except:
                continue

        raise Exception("encoding detection failed")

    # ------------------------------------------------
    # 폴더 스캔 (재귀)
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
    # JSON depth
    # ------------------------------------------------

    def json_depth(self, obj):

        if isinstance(obj, dict):
            return 1 + max((self.json_depth(v) for v in obj.values()), default=0)

        if isinstance(obj, list):
            return 1 + max((self.json_depth(v) for v in obj), default=0)

        return 0

    # ------------------------------------------------
    # DataFrame 분석
    # ------------------------------------------------

    def analyze_dataframe(self, df):

        meta = {}

        meta["row_count"] = len(df)
        meta["column_count"] = len(df.columns)

        meta["columns"] = str(df.columns.tolist())

        meta["column_types"] = str(df.dtypes.astype(str).to_dict())

        meta["missing_total"] = int(df.isnull().sum().sum())

        meta["missing_ratio"] = round(df.isnull().sum().sum() / df.size, 5)

        meta["duplicate_rows"] = int(df.duplicated().sum())

        meta["unique_values"] = str(df.nunique().to_dict())

        meta["numeric_columns"] = str(
            df.select_dtypes(include=np.number).columns.tolist())

        meta["categorical_columns"] = str(
            df.select_dtypes(exclude=np.number).columns.tolist())

        meta["sample_rows"] = df.head(5).to_dict()

        try:

            meta["statistics"] = str(df.describe().to_dict())

        except:

            pass

        return meta

    # ------------------------------------------------
    # 메타 수집
    # ------------------------------------------------

    def collect_meta(self, path):

        stat = os.stat(path)

        meta = {

            "file_path": path,
            "file_name": os.path.basename(path),
            "extension": os.path.splitext(path)[1],
            "file_size": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime),
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
            "accessed_time": datetime.fromtimestamp(stat.st_atime),
            "sha256": self.file_hash(path)
        }

        ext = meta["extension"].lower()

        try:

            if ext == ".csv":

                df = self.read_csv_safe(path)

                meta.update(self.analyze_dataframe(df))

            elif ext in [".xlsx", ".xls"]:

                xl = pd.ExcelFile(path)

                meta["sheet_count"] = len(xl.sheet_names)

                df = xl.parse(xl.sheet_names[0])

                meta.update(self.analyze_dataframe(df))

            elif ext == ".json":

                with open(path) as f:
                    data = json.load(f)

                meta["json_depth"] = self.json_depth(data)

                if isinstance(data, dict):
                    meta["key_count"] = len(data)

                if isinstance(data, list):
                    meta["list_length"] = len(data)

            elif ext in [".jpg", ".jpeg", ".png"]:

                img = Image.open(path)

                meta["width"] = img.width
                meta["height"] = img.height
                meta["channels"] = len(img.getbands())
                meta["format"] = img.format
                meta["aspect_ratio"] = round(img.width / img.height, 3)

            elif ext == ".pdf":

                reader = PdfReader(path)

                meta["page_count"] = len(reader.pages)

        except Exception as e:

            meta["analysis_error"] = str(e)

        return meta

    # ------------------------------------------------
    # 파일 선택 메타 표시
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

            self.meta_table.insert("", "end", values=(k, v))

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
    # 선택 메타 다운로드
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

    # ------------------------------------------------
    # 전체 ZIP
    # ------------------------------------------------

    def download_all(self):

        save = filedialog.asksaveasfilename(defaultextension=".zip")

        if not save:
            return

        with zipfile.ZipFile(save, "w") as z:

            for path, meta in self.meta_cache.items():

                name = os.path.basename(path) + ".json"

                z.writestr(name, json.dumps(meta, indent=4, default=str))

        messagebox.showinfo("완료", "ZIP 생성 완료")

    # ------------------------------------------------
    # CSV 다운로드
    # ------------------------------------------------

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


root = tk.Tk()

app = MetaCollectorApp(root)

root.mainloop()