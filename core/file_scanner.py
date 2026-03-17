"""
File Scanner Core

파일 시스템에서 파일 목록을 수집하는 순수 로직 모듈이다.
파일 정보를 딕셔너리 리스트로 반환한다.
"""

import os
from datetime import datetime
import win32com.client
import pythoncom 

class FileScanner:
    def __init__(self):
        self.hash_index = {}  # 중복 체크를 위한 해시 인덱스

    def scan_folder(self, folder_path: str) -> list[dict]:
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
    

    def scan_file_metadata(self, file_path: str) -> dict:
        """
        단일 파일의 메타데이터를 수집하여 딕셔너리로 반환한다.

        Parameters
        ----------
        file_path : str
            메타데이터를 수집할 파일 경로

        Returns
        -------
        dict
            파일 메타데이터 딕셔너리
            name, ext, size, modified, path 키를 가진다.
        """
        stat = os.stat(file_path)

        metadata = self.get_windows_metadata(file_path)

        return metadata

    def get_windows_metadata(self, path):
        meta = {}
        pythoncom.CoInitialize() 
        try:
            abs_path = os.path.abspath(path)
            folder_path = os.path.dirname(abs_path)
            file_name = os.path.basename(abs_path)
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.Namespace(folder_path)
            if not folder: return meta
            item = folder.ParseName(file_name)
            if not item: return meta
            for i in range(320): 
                key = folder.GetDetailsOf(None, i)
                if not key: continue
                value = folder.GetDetailsOf(item, i)
                if value != "": meta[key] = value
        except: pass
        finally: pythoncom.CoUninitialize() 
        return meta