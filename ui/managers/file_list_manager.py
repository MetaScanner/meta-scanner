from tkinter import messagebox

class FileListManager:
    def __init__(self, app, frame):
        self.app = app
        self.frame = frame
        
    # =========================
    # 파일 목록 로드 (app으로부터 파일 리스트 전달받아 UI 업데이트)
    # =========================
    def load_files(self, files: list):
        self.frame.clear_list_view()
        if not files:
            self.frame.show_empty_label(True)
            messagebox.showinfo("알림", "선택한 폴더에 파일이 없습니다.")
            return
        self.frame.update_list_view(files)
 
    # =========================
    # 파일 크기 포맷
    # =========================
    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size / 1024 ** 2:.1f} MB"
        else:
            return f"{size / 1024 ** 3:.1f} GB"
        
    # =========================
    # 파일 선택 시 메타데이터 로드 요청 (app으로 전달)
    # =========================
    def file_selected(self, file_path: str):
        self.app.load_metadata(file_path)