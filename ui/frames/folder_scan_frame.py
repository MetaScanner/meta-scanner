"""
폴더 스캔 UI 프레임을 정의하는 모듈
이 모듈은 폴더 스캔과 관련된 UI 요소를 포함하는 프레임을 정의한다.
"""
import tkinter as tk
from tkinter import ttk

class FolderScanFrame:
    def __init__(self, app, parent):
        self.app = app
        self.frame = ttk.Frame(parent)

        self._build()

    def set_manager(self, manager):
        self.manager = manager
        
    def _build(self):
        self.frame.columnconfigure(0, weight=1)

        # 폴더 경로 입력 필드
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(self.frame, textvariable=self.folder_var, state="readonly", font=self.app.large_font)
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # 폴더 선택 버튼
        self.select_button = ttk.Button(self.frame, text="폴더 선택", command=self._on_select_folder, style="Primary.TButton")
        self.select_button.grid(row=0, column=1, padx=5, pady=5)

    # =========================
    # 폴더 선택 이벤트 핸들러
    # =========================
    def _on_select_folder(self):
        folder = self.manager.select_folder()
        if folder:
            self.folder_var.set(folder)