"""
MetaCollector Application Controller

MetaCollector GUI 애플리케이션의 메인 컨트롤러 역할을 담당하는 클래스이다.
Tkinter 루트 윈도우를 초기화하고 애플리케이션의 기본 UI 환경을 설정한다.

이 모듈은 주로 다음 역할을 수행한다:
- 사용자 이벤트(UI 입력) 감지
- 사용자 요청에 따른 기능 실행
- core 모듈의 메타데이터 스캔 기능 호출
- 스캔 결과를 UI에 전달

실제 파일 탐색 및 메타데이터 수집 로직은 core 모듈에서 처리한다.
"""
from ui.main_layout import MainLayout
from core.file_processor import FileProcessor
from infra.window_adapter import WindowAdapter

import tkinter as tk

class MetaCollector:
    def __init__(self, root):
        self.root = root
        self.root.title("K-water Meta-Collector")
        self.root.geometry("1000x800")

        self.window_adapter = WindowAdapter()
        self.processor = FileProcessor()

        self.layout = MainLayout(self)

        self.folder_manager = self.layout.folder_scan_manager
        self.file_list_manager = self.layout.file_list_manager
        self.metadata_manager = self.layout.metadata_manager
    
    # =========================
    # 폴더 선택 이벤트 중재 (FolderScanManager → app → FileListManager)
    # =========================
    def on_folder_selected(self, folder_path: str):
        raw_files = self.window_adapter.get_all_files(folder_path)
        files = self.processor.process_files_data(raw_files)
        self.file_list_manager.load_files(files)
        self.metadata_manager.clear_metadata()

    def load_metadata(self, file_path: str):
        self.metadata_manager.update_metadata(file_path)
    
    def request_collect_metadata(self, file_path: str) -> dict:
        return self.window_adapter.get_file_metadata(file_path)