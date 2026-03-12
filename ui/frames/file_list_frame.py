from ui.managers.file_list_manager import FileListManager

import tkinter as tk
from tkinter import ttk

class FileListFrame:
    def __init__(self, app, parent):
        self.app = app
        self.frame = ttk.LabelFrame(parent, style="Box.TFrame", padding=(6, 4))

        self.manager = FileListManager(self)
        self._build()

    def _build(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self._create_list_view()



    def _create_list_view(self):
        self.tree_container = ttk.Frame(self.frame)
        self.tree_container.pack(fill="both", expand=True)

        self.tree_container.columnconfigure(0, weight=1)
        self.tree_container.rowconfigure(0, weight=1)
        
        columns = ("name", "type", "size", "modified") 
        self.tree = ttk.Treeview(self.tree_container, columns=columns, show="headings", height=10)

        # 컬럼 정의
        self.tree.heading("name", text="파일명")
        self.tree.heading("type", text="형식")
        self.tree.heading("size", text="크기")
        self.tree.heading("modified", text="수정일")

        self.tree.column("name", anchor="w", width=300)
        self.tree.column("type", anchor="center", width=80)
        self.tree.column("size", anchor="e", width=100)
        self.tree.column("modified", anchor="center", width=150)

        vsb = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.empty_label = ttk.Label(
            self.tree_container,
            text="폴더를 선택하여 파일 목록을 불러오세요.",
            background="#ffffff",
            foreground="#888888",
            anchor="center",
            justify="center",
            font=self.app.font
        )

        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        # self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        
        
    # 전달받은 파일 목록을 Treeview 테이블에 표시
    def update_file_list(self, file_list):
        self.tree.delete(*self.tree.get_children())

        if not file_list:
            self.empty_label.config(text="선택한 폴더에 표시할 파일이 없습니다.")
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
            return

        self.empty_label.place_forget()

        for file_info in file_list:
            self.tree.insert(
                "",
                "end",
                values=(
                    file_info["name"],
                    file_info["type"],
                    file_info["size"],
                    file_info["modified"],
                )
            )