"""
ScrollContainer

Tkinter에서 세로 스크롤이 가능한 콘텐츠 영역을 제공하는 UI 컨테이너이다.
Canvas와 Scrollbar를 조합하여 스크롤 가능한 레이아웃을 구성하고,
실제 UI 위젯은 내부의 page_frame에 배치한다.

이 클래스는 다음을 담당한다:
- Canvas 기반 스크롤 컨테이너 생성
- Scrollbar 연결
- 콘텐츠 크기에 따른 scrollregion 자동 갱신
- Canvas와 내부 프레임(page_frame)의 가로폭 동기화
"""

import tkinter as tk
from tkinter import ttk

class ScrollContainer:
    def __init__(self, root):
        self.root = root
        self._build()

    def _build(self):
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.page_frame = ttk.Frame(self.canvas)
        self.page_frame.columnconfigure(0, weight=1)

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.page_frame, anchor="nw"
        )

        # scrollregion 자동 갱신
        def _update_scrollregion(event=None):

            self.canvas.update_idletasks()

            width = self.page_frame.winfo_width()
            height = self.page_frame.winfo_height()

            canvas_h = self.canvas.winfo_height()

            # canvas보다 작으면 scroll 필요 없음
            if height <= canvas_h:
                self.canvas.configure(scrollregion=(0, 0, width, canvas_h))
            else:
                self.canvas.configure(scrollregion=(0, 0, width, height))

        self.page_frame.bind("<Configure>", _update_scrollregion)

        # 가로폭 동기화
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(
                self.canvas_window, width=e.width
            )
        )
