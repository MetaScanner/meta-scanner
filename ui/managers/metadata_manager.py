

class MetadataManager:
    def __init__(self, app, frame):
        self.app = app
        self.frame = frame
        self.metadata_cache = {}

    def update_metadata(self, file_path: str):
        self.frame.clear_metadata_view()

        if not file_path in self.metadata_cache:
            metadata = self.app.request_collect_metadata(file_path)
            self.metadata_cache[file_path] = metadata

        self.frame.update_metadata_view(self.metadata_cache[file_path])

    def clear_metadata(self):
        self.frame.clear_metadata_view()
        self.metadata_cache = {}

    def has_metadata_cache(self, file_path: str) -> bool:
        return file_path in self.metadata_cache