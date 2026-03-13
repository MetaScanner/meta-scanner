from core.file_scanner import scan_folder

class FileListManager:
    def __init__(self, frame):
        self.frame = frame
        
    # =========================
    # 파일 목록 로드
    # app으로부터 폴더 경로를 받아 core에서 파일 목록을 가져온 뒤
    # frame의 treeview에 표시한다.
    # =========================
    def load_files(self, folder_path: str):
        files = scan_folder(folder_path)
 
        # treeview 초기화
        tree = self.frame.tree
        tree.delete(*tree.get_children())
 
        if not files:
            self.frame.empty_label.place(relx=0.5, rely=0.5, anchor="center")
            return
 
        # 파일이 있으면 안내 문구 숨기기
        self.frame.empty_label.place_forget()
 
        for file in files:
            size_str = self._format_size(file["size"])
            tree.insert("", "end", values=(
                file["name"],
                file["ext"],
                size_str,
                file["modified"],
            ))
 
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