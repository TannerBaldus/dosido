from api import ApiClient

class BaseObject():

    def __init__(self, config):
        self.api_client = ApiClient(config.api_key)
        self.config = config