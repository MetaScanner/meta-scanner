import os
from datetime import datetime


class FileListManager:
    def __init__(self, frame):
        self.frame = frame

    # 선택한 폴더의 파일 목록을 읽어와 리스트로 반환
    def get_files_in_folder(self, folder_path):
        file_list = []

        if not folder_path:
            return file_list

        try:
            for file_name in os.listdir(folder_path):
                full_path = os.path.join(folder_path, file_name)

                if os.path.isfile(full_path):
                    ext = os.path.splitext(file_name)[1]
                    size = os.path.getsize(full_path)
                    modified = datetime.fromtimestamp(
                        os.path.getmtime(full_path)
                    ).strftime("%Y-%m-%d %H:%M:%S")

                    file_list.append(
                        {
                            "name": file_name,
                            "type": ext if ext else "-",
                            "size": f"{size:,}",
                            "modified": modified,
                        }
                    )

        except Exception as e:
            print(f"파일 목록 불러오기 오류: {e}")

        return file_list