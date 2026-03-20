import json
import csv
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox

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
        
        
    def save_metadata(self):
        if not self.current_file_path or self.current_file_path not in self.metadata_cache:
            messagebox.showwarning("알림", "저장할 메타데이터가 없습니다.")
            return
        
        metadata = self.metadata_cache[self.current_file_path]
        save_format = self.frame.format_var.get()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{save_format}",
            filetypes=[(save_format.upper(), f"*.{save_format}")],
            initialfile=f"metadata.{save_format}"
        )
        
        if not file_path:
            return
        
        if save_format == "json":
            self._save_as_json(metadata, file_path)
        elif save_format == "csv":
            self._save_as_csv(metadata, file_path)
        elif save_format == "xml":
            self._save_as_xml(metadata, file_path)
        
        messagebox.showinfo("완료", f"저장되었습니다.\n{file_path}")
        
    def _save_as_json(self, metadata, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
                
    def _save_as_csv(self, metadata, file_path):
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["항목", "값"])
            for key, value in metadata.items():
                writer.writerow([key, value])
                    
    def _save_as_xml(self, metadata, file_path):
        root = ET.Element("Metadata")
        for key, value in metadata.items():
            item = ET.SubElement(root, "Item", name=key)
            item.text = str(value)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(file_path, encoding='utf-8', xml_declaration=True)


    def has_metadata_cache(self, file_path: str) -> bool:
        return file_path in self.metadata_cache