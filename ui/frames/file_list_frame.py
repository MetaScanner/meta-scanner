from ui.managers.file_list_manager import FileListManager

import tkinter as tk
from tkinter import ttk

class FileListFrame:
    def __init__(self, app, parent):
        self.app = app
        self.frame = ttk.LabelFrame(parent, style="BOX.TFrame", padding=(6, 4))

        self._build()
    
    def set_manager(self, manager):
        self.manager = manager

    def _build(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self._create_list_view()

    def _create_list_view(self):
        self.tree_container = ttk.Frame(self.frame)
        self.tree_container.pack(fill="both", expand=True)

        self.tree_container.columnconfigure(0, weight=1)
        self.tree_container.rowconfigure(0, weight=1)
        
        columns = ("name", "type", "size", "modified", "path") 
        self.tree = ttk.Treeview(self.tree_container, columns=columns, show="headings", height=10)

        self.tree["displaycolumns"] = ("name", "type", "size", "modified", "path")
        
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

        self.show_empty_label(True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def update_list_view(self, files: list):    
        self.show_empty_label(False)
        for file in files:
            size_str = self.manager._format_size(file["size"])
            self.tree.insert("", "end", values=(
                file["name"],
                file["ext"],
                size_str,
                file["modified"],
                file["path"]
            ))

    def clear_list_view(self):
        self.tree.delete(*self.tree.get_children())
        self.show_empty_label(True)

    def show_empty_label(self, show=True):
        if show:
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.empty_label.place_forget()

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            path = item["values"][4]
            name = item["values"][0]
            self.manager.file_selected(path, name)

    # ===========================
    # ScrollManager 인터페이스
    # ===========================
    def is_inside(self, widget):
        return self._is_child_of(widget, self.tree_container)

    def scroll(self, event):
        delta = int(-1 * (event.delta / 120))
        self.tree.yview_scroll(delta, "units")

    def _is_child_of(self, widget, parent):
        while widget is not None:
            if widget == parent:
                return True
            widget = widget.master
        return False