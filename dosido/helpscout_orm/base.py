from dosido.api import ApiClient


class BaseObject(object):

    def __init__(self, config):
        self.api_client = ApiClient(config.api_key)
        self.config = config
