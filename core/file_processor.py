"""
File Processor

app으로부터 받은 파일 목록을 가공하는 순수 로직 모듈이다.
파일 정보를 딕셔너리 리스트로 반환한다.
"""

import os
from datetime import datetime 

class FileProcessor:
    def __init__(self):
        pass

    def process_files_data(self, raw_files: list[dict]) -> list[dict]:
            """데이터를 앱의 형식에 맞게 변환 (비즈니스 로직)"""
            processed_files = []
            for raw in raw_files:
                ext = os.path.splitext(raw["name"])[1] or "(없음)"
                modified = datetime.fromtimestamp(raw["mtime"]).strftime("%Y-%m-%d %H:%M")
                
                processed_files.append({
                    "name": raw["name"],
                    "ext": ext,
                    "size": raw["size"],
                    "modified": modified,
                    "path": raw["path"],
                })
            return processed_files