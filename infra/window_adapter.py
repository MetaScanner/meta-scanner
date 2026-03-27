import os
import win32com.client
import pythoncom

class WindowAdapter:
    def __init__(self):
        pass

    def get_all_files(self, folder_path: str):
        """
        폴더 내 모든 파일의 기본 정보를 수집한다.
        """
        raw_files = []
        for root_dir, _, filenames in os.walk(folder_path):
            for filename in filenames:
                path = os.path.join(root_dir, filename)
                try:
                    stat = os.stat(path)
                    raw_files.append({
                        "name": filename,
                        "path": path,
                        "size": stat.st_size,
                        "mtime": stat.st_mtime
                    })
                except Exception:
                    continue
        return raw_files

    def get_file_metadata(self, file_path: str) -> dict:
        """
        Windows Shell을 사용하여 파일의 메타데이터를 수집한다.

        Parameters
        ----------
        file_path : str
            메타데이터를 수집할 파일의 경로

        Returns
        -------
        dict
            수집된 메타데이터 딕셔너리
            키는 메타데이터 이름, 값은 해당 메타데이터 값이다.
        """
        metadata = {}
        pythoncom.CoInitialize()
        try:
            abs_path = os.path.abspath(file_path)
            folder_path = os.path.dirname(abs_path)
            file_name = os.path.basename(abs_path)
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.Namespace(folder_path)

            if not folder:
                return metadata
            
            item = folder.ParseName(str(file_name))

            if not item:
                return metadata
            
            for i in range(320): 
                key = folder.GetDetailsOf(None, i)
                if not key: continue
                value = folder.GetDetailsOf(item, i)
                if value != "": metadata[key] = value

        except Exception as e:
            print("WindowAdapter error:", e)
        finally:
            pythoncom.CoUninitialize()

        return metadata