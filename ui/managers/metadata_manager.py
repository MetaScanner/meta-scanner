from tkinter import messagebox

class MetadataManager:
    def __init__(self, app, frame):
        self.app = app
        self.frame = frame
        self.metadata_cache = {}
        self.current_file_path = None

    def update_metadata(self, file_path: str):
        self.frame.clear_metadata_view()
        self.current_file_path = file_path

        if not file_path in self.metadata_cache:
            metadata = self.app.request_collect_metadata(file_path)
            self.metadata_cache[file_path] = metadata

        self.frame.update_metadata_view(self.metadata_cache[file_path])

    def clear_metadata(self):
        self.frame.clear_metadata_view()
        self.metadata_cache = {}
        self.current_file_path = None
        
    def save_metadata(self, save_format: str):
        if not self.current_file_path or self.current_file_path not in self.metadata_cache:
            messagebox.showwarning("알림", "저장할 메타데이터가 없습니다.")
            return
        
        metadata = self.metadata_cache[self.current_file_path]

        file_path = self.app.export_metadata(metadata, save_format)
        
        messagebox.showinfo("완료", f"저장되었습니다.\n{file_path}")
        
    def has_metadata_cache(self, file_path: str) -> bool:
        return file_path in self.metadata_cache