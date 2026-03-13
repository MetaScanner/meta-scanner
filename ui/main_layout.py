"""
Main Layout

MetaScanner 애플리케이션의 메인 UI 레이아웃을 구성하는 모듈이다.
Tkinter 루트 윈도우 아래에서 전체 화면 구조를 정의하고
각 프레임(frame)과 UI 컴포넌트를 배치하는 역할을 한다.

이 모듈은 다음을 담당한다:
- 메인 화면 레이아웃 구성
- 프레임(frame) 및 UI 컴포넌트 배치
- 스크롤 컨테이너 및 UI 매니저 초기화

실제 기능 로직은 managers 또는 core 모듈에서 처리된다.
"""

from ui.components.scroll_container import ScrollContainer
from ui.managers.scroll_manager import ScrollManager
from ui.frames.folder_scan_frame import FolderScanFrame
from ui.frames.file_list_frame import FileListFrame
from ui import styles

class MainLayout:
    def __init__(self, app):
        self.app = app
        self.root = app.root

        styles.setup_styles(app)

        self._build_scroll_container()
        self._build_frames()
        self._build_scroll_manager()

    # =========================
    # 전체 화면 스크롤 설정
    # =========================
    def _build_scroll_container(self):
        self.scroll_container = ScrollContainer(self.root)
        self.page_frame = self.scroll_container.page_frame
        self.canvas = self.scroll_container.canvas

        self.page_frame.columnconfigure(0, weight=1)

    # =========================
    # Content 영역 생성
    # =========================
    def _build_frames(self):
        self.folder_scan = FolderScanFrame(self.app, self.page_frame)
        self.folder_scan.frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.file_list = FileListFrame(self.app, self.page_frame)
        self.file_list.frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    
    # =========================
    # 내부 스크롤 영역 등록
    # =========================
    def _build_scroll_manager(self):
        self.scroll_manager = ScrollManager(self.root, self.canvas)