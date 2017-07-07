from .base import BaseObject


class Site(BaseObject):

    def __init__(self, config, sub_domain):
        super().__init__(config)
        self.sub_domain = sub_domain

    def create(self, title):
        return self.api_client.create_site(self.sub_domain, title)

    def get(self):
        return self.api_client.get_site_by_sub_domain(self.sub_domain)