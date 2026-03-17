import os
import json
import zipfile
import hashlib
import mimetypes
import win32com.client
import pythoncom 

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
        root.title("AI Dataset Meta Collector v2 - Prototype")
        root.geometry("1300x750")

        self.meta_cache = {}
        self.file_paths = {}
        self.hash_index = {}

        self.conn = sqlite3.connect("meta_index.db", check_same_thread=False)
        self.create_db()

        # ---------------------------
        # 상단 버튼 영역 (요청하신 3개 버튼만 유지)
        # ---------------------------
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=5)

        self.folder_var = tk.StringVar()
        tk.Entry(top_frame, textvariable=self.folder_var, width=90).pack(side="left")

        # 1. 폴더 스캔 버튼
        tk.Button(top_frame, text="폴더 스캔", command=self.scan_folder).pack(side="left", padx=5)
        
        # 2. 선택 파일 메타 저장 (기존 download_single 연결)
        tk.Button(top_frame, text="선택 파일 메타 저장", command=self.download_single).pack(side="left", padx=5)
        
        # 3. 전체 메타데이터 저장 (기존 collect_all_meta 및 결과 저장을 위해 기능 유지)
        tk.Button(top_frame, text="전체 메타데이터 저장", command=self.save_all_meta_flow).pack(side="left", padx=5)

        # ---------------------------
        # 파일 목록 (Treeview) - 레이아웃 유지
        # ---------------------------
        columns = ("name", "type", "size", "modified")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True)

        for c in columns:
            self.tree.heading(c, text=c)

        self.tree.bind("<<TreeviewSelect>>", self.show_meta)

        # ---------------------------
        # 하단 버튼 영역 제거 (상단으로 통합됨에 따라 레이아웃 유지용 빈 프레임 또는 제거)
        # ---------------------------
        # 기존 하단 버튼들은 제거하였습니다.

        # ---------------------------
        # 메타 테이블 - 레이아웃 유지
        # ---------------------------
        meta_frame = tk.LabelFrame(root, text="Metadata")
        meta_frame.pack(fill="both", expand=True)

        self.meta_table = ttk.Treeview(meta_frame, columns=("key", "value"), show="headings")
        self.meta_table.heading("key", text="항목")
        self.meta_table.heading("value", text="값")
        self.meta_table.pack(fill="both", expand=True)

    # ------------------------------------------------
    # 핵심 로직 흐름 보조 (전체 저장용)
    # ------------------------------------------------
    def save_all_meta_flow(self):
        """모든 메타데이터를 수집한 후 바로 파일로 저장하는 흐름"""
        if not self.file_paths:
            messagebox.showinfo("알림", "스캔된 파일이 없습니다.")
            return
        
        self.collect_all_meta() # 모든 메타 데이터 수집
        self.download_csv()    # 혹은 download_all (ZIP) 등으로 변경 가능

    # ------------------------------------------------
    # 기존 기능 메서드 (구조 유지를 위해 보존)
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

    def file_hash(self, path):
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest()

    def get_windows_metadata(self, path):
        meta = {}
        pythoncom.CoInitialize() 
        try:
            abs_path = os.path.abspath(path)
            folder_path = os.path.dirname(abs_path)
            file_name = os.path.basename(abs_path)
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.Namespace(folder_path)
            if not folder: return meta
            item = folder.ParseName(file_name)
            if not item: return meta
            for i in range(320): 
                key = folder.GetDetailsOf(None, i)
                if not key: continue
                value = folder.GetDetailsOf(item, i)
                if value != "": meta[key] = value
        except: pass
        finally: pythoncom.CoUninitialize() 
        return meta

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
            "sha256": sha
        }
        
        # 중복 체크
        meta["duplicate"] = sha in self.hash_index
        if not meta["duplicate"]:
            self.hash_index[sha] = path

        # 윈도우 메타데이터 결합 (중복 키 제거)
        windows_meta = self.get_windows_metadata(path)
        duplicate_keys = ['이름', '폴더 경로', '크기', '항목 유형', '수정한 날짜', '만든 날짜', '액세스한 날짜']
        for k in duplicate_keys:
            if k in windows_meta: del windows_meta[k]
        meta.update(windows_meta)

        # 파일 타입별 분석
        ext = meta["extension"].lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(path)
                meta.update({"row_count": len(df), "col_count": len(df.columns)})
            elif ext in [".jpg", ".jpeg", ".png"]:
                img = Image.open(path)
                meta["resolution"] = f"{img.width}x{img.height}"
        except: pass

        self.save_db(meta)
        return meta

    def scan_folder(self):
        folder = filedialog.askdirectory()
        if not folder: return
        self.folder_var.set(folder)
        self.tree.delete(*self.tree.get_children())
        self.file_paths.clear()
        for root_dir, dirs, files in os.walk(folder):
            for file in files:
                path = os.path.join(root_dir, file)
                size = os.path.getsize(path)
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                ext = os.path.splitext(file)[1]
                iid = self.tree.insert("", "end", values=(file, ext, size, mtime))
                self.file_paths[iid] = path

    def show_meta(self, event):
        selected = self.tree.selection()
        if not selected: return
        path = self.file_paths[selected[0]]
        meta = self.collect_meta(path)
        self.meta_cache[path] = meta
        self.meta_table.delete(*self.meta_table.get_children())
        for k, v in meta.items():
            self.meta_table.insert("", "end", values=(k, str(v)))

    def collect_all_meta(self):
        paths = list(self.file_paths.values())
        def worker(path):
            self.meta_cache[path] = self.collect_meta(path)
        with ThreadPoolExecutor(max_workers=6) as exe:
            exe.map(worker, paths)

    def download_single(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "파일을 선택해주세요.")
            return
        path = self.file_paths[selected[0]]
        meta = self.collect_meta(path)
        save = filedialog.asksaveasfilename(defaultextension=".json", initialfile=f"{os.path.basename(path)}_meta.json")
        if save:
            with open(save, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=4, default=str, ensure_ascii=False)

    def download_csv(self):
        if not self.meta_cache: return
        save = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="total_metadata.csv")
        if save:
            df = pd.DataFrame(list(self.meta_cache.values()))
            df.to_csv(save, index=False, encoding="utf-8-sig")
            messagebox.showinfo("완료", "데이터 저장 완료")

    def save_db(self, meta):
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?)", 
                   (meta["file_path"], meta["file_name"], meta["extension"], 
                    meta["file_size"], meta["sha256"], str(meta["created_time"]), str(meta.get("modified_time", ""))))
        self.conn.commit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MetaCollectorApp(root)
    root.mainloop()