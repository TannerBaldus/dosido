from .base import BaseObject
import os


class Collection(BaseObject):

    def __init__(self, config, name):
        super().__init__(config)
        self.site_id = config.site_id
        self.name = name

    def create(self, private, no_dir=False):
        visibility = "private" if private else "public"
        collection = self.api_client.create_collection(self.site_id, self.name, visibility)["collection"]
        self.config.add_collection(self.name, collection["id"])
        if not no_dir:
            self._create_directory()
        return collection

    def _create_directory(self):
        if not os.path.isdir("name/media"):
            os.makedirs("{}/{media}".format(self.name))
