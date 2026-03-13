"""
File Scanner Core

파일 시스템에서 파일 목록을 수집하는 순수 로직 모듈이다.
파일 정보를 딕셔너리 리스트로 반환한다.
"""

import os
from datetime import datetime


def scan_folder(folder_path: str) -> list[dict]:
    """
    폴더를 재귀적으로 탐색하여 파일 정보 목록을 반환한다.

    Parameters
    ----------
    folder_path : str
        탐색할 폴더 경로

    Returns
    -------
    list[dict]
        파일 정보 딕셔너리 리스트
        각 딕셔너리는 name, ext, size, modified, path 키를 가진다.
    """
    files = []

    for root_dir, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            path = os.path.join(root_dir, filename)

            try:
                stat = os.stat(path)
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            except Exception:
                size = 0
                modified = ""

            ext = os.path.splitext(filename)[1] or "(없음)"

            files.append({
                "name": filename,
                "ext": ext,
                "size": size,
                "modified": modified,
                "path": path,
            })

    return files