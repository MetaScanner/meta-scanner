"""
Folder Scan Manager

폴더 스캔 UI에서 발생하는 사용자 이벤트를 처리하는 매니저 모듈이다.
폴더 선택 다이얼로그를 호출하고 선택된 경로를 UI 프레임에 전달하는 역할을 한다.

이 모듈은 다음 기능을 담당한다:
- 폴더 선택 다이얼로그 실행
- 선택된 폴더 경로를 UI 상태 변수에 반영
"""

from tkinter import filedialog

class FolderScanManager:
    def __init__(self, frame):
        self.frame = frame

    # =========================
    # 폴더 선택 다이얼로그
    # =========================
    def select_folder(self):
        folder = filedialog.askdirectory()
        
        if folder:
            self.frame.app.on_folder_selected(folder)
 
        return folder