from tkinter import filedialog
import json
import csv
import xml.etree.ElementTree as ET

class Exporter:
    def __init__(self):
        pass

    def export_data(self, data:dict, format:str, file_name: str):    
        name = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name

        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(format.upper(), f"*.{format}")],
            initialfile=f"{name}_metadata.{format}"
        )
        
        if not file_path:
            return
        
        if format == "json":
            self._save_as_json(data, file_path)
        elif format == "csv":
            self._save_as_csv(data, file_path)
        elif format == "xml":
            self._save_as_xml(data, file_path)

        return file_path
    
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