from .base import BaseObject


class Collection(BaseObject):

    def __init__(self, config, name):
        super().__init__(config)
        self.site_id = config.site_id
        self.name = name

    def create(self, private):
        visibility = "private" if private else "public"
        collection = self.api_client.create_collection(self.site_id, self.name, visibility)["collection"]
        self.config.add_collection(self.name, collection["id"])
        return collection
