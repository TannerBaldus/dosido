from configparser import ConfigParser
from pathlib import Path
from glob import glob
import os


class DosidoConfig(ConfigParser):
    settings_path = ".dosido/config.ini"

    def __init__(self):
        super(DosidoConfig).__init__()
        self.read(self.config_filepath)
        if not self.sections():
            self._initialize_sections()

    def _initialize_sections(self):
        self.add_section("api_info")
        self.add_section("collections")
        self.add_section("site_details")

    @property
    def config_filepath(self):
        config_path = glob(self.settings_path)
        for dir_path in Path(os.getcwd()).parents:
            if config_path:
                return config_path[0]
            config_path = glob(os.path.join(dir_path, self.settings_path))
        raise ValueError("no path")

    def get_collection(self, collection_name):
        return self.get("collections", collection_name)

    def add_collection(self, collection_name, collection_id):
        self.set("collections", collection_name, collection_id)

    @property
    def api_key(self):
        return self.get("api_info", "api_key")

    @api_key.setter
    def api_key(self, api_key_str):
        self.set("api_info", "api_key", api_key_str)

    @property
    def site_id(self):
        return self.get("site_details", "site_id")

    @site_id.setter
    def site_id(self, site_id):
        self.set("site_details", "site_id", site_id)

    @property
    def image_host(self):
        return self.get("site_details", "image_host")

    @image_host.setter
    def image_host(self, image_host_url):
        self.set("site_details", "image_host", image_host_url)


