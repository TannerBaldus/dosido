from pathlib import Path

import os

class FileArticle(object):

    def __init__(self, file_path, config, api_client,  temp=False):
        self.file_obj = open(file_path, 'r')
        self.collection_id = self._get_collection_id_from_path(file_path)
        self.config = config
        self.name = os.path.basename(self.file_obj.name)

    def _get_collection_id_from_path(self, file_path):
        collection_name = Path(file_path).parent.name
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