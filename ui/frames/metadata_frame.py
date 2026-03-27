import tkinter as tk
from tkinter import ttk

import ui.styles as styles

class MetadataFrame:
    def __init__(self, app, parent):
        self.app = app
        self.frame = ttk.LabelFrame(parent, text="Metadata", style="TLabelframe")

        self._build()

    def set_manager(self, manager):
        self.manager = manager

    def _build(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        #메타 데이터 저장 버튼 프레임
        self.meta_frame = tk.Frame(self.frame, bg=styles.BG_COLOR)
        self.meta_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.meta_frame.columnconfigure(0, weight=1)
        self.meta_frame.rowconfigure(1, weight=1)

        self.btn_frame = tk.Frame(self.meta_frame, bg=styles.BG_COLOR)
        self.btn_frame.grid(row=0, column=0, sticky="e", padx=5, pady=5)

        # 포맷 프레임
        self.format_frame = tk.Frame(self.btn_frame, bg=styles.BG_COLOR)
        self.format_frame.pack(side=tk.LEFT, padx=(10, 0))

        # 저장 프레임
        self.save_frame = tk.Frame(self.btn_frame, bg=styles.BG_COLOR)
        self.save_frame.pack(side=tk.LEFT)


        # 버튼 배치
        self.format_var = tk.StringVar(value="json")
        format = {"json": "#FAE7C0",  "csv":  "#D8F3DA",  "xml":  "#E5F1FB"}

        for fmt, color in format.items():
            rb = tk.Radiobutton(self.format_frame, text=fmt.upper(), value=fmt, variable=self.format_var,
                                             indicatoron=False, width=5, pady=2, selectcolor=color,  bg="#F0F0F0", activebackground=color, relief="raised")
            rb.pack(side=tk.LEFT, padx=2)
            
        self.single_file_download_btn = ttk.Button(
            self.save_frame, 
            text="메타데이터 저장", 
            command=self._save_metadata, 
            style="Primary.TButton")
        
        self.single_file_download_btn.pack(side=tk.LEFT, padx=10)

        self._create_metadata_view()

    def _create_metadata_view(self):
        # 스크롤바와 함께 트리뷰 프레임 생성
        self.tree_container = tk.Frame(self.meta_frame)
        self.tree_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.tree_container.columnconfigure(0, weight=1)
        self.tree_container.rowconfigure(0, weight=1)

        # 스크롤바 생성
        self.vsb = ttk.Scrollbar(self.tree_container, orient="vertical")
        self.hsb = ttk.Scrollbar(self.tree_container, orient="horizontal")

        # 트리뷰 생성
        self.tree_height = 15
        self.tree = ttk.Treeview(
                    self.tree_container, 
                    columns=("key", "value"), # 컬럼 정의
                    show="headings",
                    height=self.tree_height, 
                    yscrollcommand=self.vsb.set, 
                    xscrollcommand=self.hsb.set, 
                    style="Treeview"
                )
        
        # 헤더 및 너비 설정
        self.tree.heading("key", text="항목")
        self.tree.heading("value", text="값")
        self.tree.column("key", width=150, minwidth=100, anchor="w")
        self.tree.column("value", width=350, minwidth=200, anchor="w", stretch=True)

        # 스크롤바 설정
        self.vsb.config(command=self.tree.yview)
        self.hsb.config(command=self.tree.xview)
        
        # 그리드 레이아웃 배치
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.resize_bar = tk.Frame(self.tree_container, height=5, cursor="sb_v_double_arrow", bg="#cccccc")
        self.resize_bar.grid(row=2, column=0, sticky="ew")
        self.resize_bar.bind("<Button-1>", self._start_resize)
        self.resize_bar.bind("<B1-Motion>", self._on_resize)
        self.resize_bar.bind("<Enter>", self._on_hover)
        self.resize_bar.bind("<Leave>", self._on_leave)
        

    def update_metadata_view(self, metadata: dict):
        self.clear_metadata_view()

        if not metadata:
            return
        for key, value in metadata.items():
            self.tree.insert("", "end", values=(key, value))
        
    def _on_save_click(self):
        self.manager.save_metadata()

    def clear_metadata_view(self):
        self.tree.delete(*self.tree.get_children())

    # ===========================
    # 메타데이터 저장 이벤트 핸들러
    # ===========================
    def _save_metadata(self):
        save_format = self.format_var.get()
        self.manager.save_metadata(save_format)

    # ===========================
    # 트리뷰 크기 조절 이벤트 핸들러
    # ===========================
    def _start_resize(self, event):
        self.resize_bar.config(bg=styles.RESIZE_BAR_HOVER)
        self.start_y = event.y_root
        self.start_height = self.tree_height

    def _on_resize(self, event):
        delta = event.y_root - self.start_y

        row_delta = delta // 20

        new_height = max(3, self.start_height + row_delta)

        self.tree_height = new_height
        self.tree.config(height=self.tree_height)

        self.manager.request_ui_update()

    def _on_hover(self, event):
        self.resize_bar.config(bg=styles.RESIZE_BAR_HOVER)

    def _on_leave(self, event):
        self.resize_bar.config(bg=styles.RESIZE_BAR_NORMAL)

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
