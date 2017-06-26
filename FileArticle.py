from pathlib import Path

import os

class FileArticle(object):

    def __init__(self, file_path, config, api_client):
        self.file_path = file_path
        self.image_host = config.get("site_details", "image_host")
        self.api_client = api_client
        self.config = config
        base_name = os.path.basename(file_path)
        self.slug = base_name
        self.title = string.capwords(" ".join(base_name.split("_")))

    @property
    def collection_id(self):
        collection_name = Path(self.file_path).parent.name
        collection_id = self.config.get("collections", collection_name)
        return collection_id

    def replace_image_links(self):
        pass

    def upload(self):
        pass

    def update(self):
        pass

    @property
    def temp_name(self):
        return "{}_tmp", self.name