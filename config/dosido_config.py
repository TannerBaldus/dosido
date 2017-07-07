from configparser import ConfigParser
from pathlib import Path
from glob import glob
import os

from .constants import CONFIG_FILEPATH
from exceptions import DosidoNotInitialized


class DosidoConfig():
    settings_path = CONFIG_FILEPATH

    def __init__(self):
        self.config_parser = ConfigParser()
        self.config_parser.read(self.config_filepath)
        if not self.config_parser.sections():
            self._initialize_sections()

    def _initialize_sections(self):
        self.config_parser.add_section("api_info")
        self.config_parser.add_section("collections")
        self.config_parser.add_section("site_details")

    @property
    def config_filepath(self):
        config_path = glob(self.settings_path)
        for dir_path in Path(os.getcwd()).parents:
            if config_path:
                return config_path[0]
            config_path = glob(os.path.join(dir_path, self.config_parser.settings_path))
        raise DosidoNotInitialized()

    def get_collection(self, collection_name):
        return self.config_parser.get("collections", collection_name)

    def add_collection(self, collection_name, collection_id):
        self.config_parser.set("collections", collection_name, collection_id)

    @property
    def api_key(self):
        return self.config_parser.get("api_info", "api_key")

    @api_key.setter
    def api_key(self, api_key_str):
        self.config_parser.set("api_info", "api_key", api_key_str)

    @property
    def site_id(self):
        return self.config_parser.get("site_details", "site_id")

    @site_id.setter
    def site_id(self, site_id):
        self.config_parser.set("site_details", "site_id", site_id)

    @property
    def asset_host(self):
        return self.config_parser.get("site_details", "image_host")

    @asset_host.setter
    def asset_host(self, image_host_url):
        self.config_parser.set("site_details", "image_host", image_host_url)

    def save(self):
        with open(self.config_filepath, 'w') as configfile:
            self.config_parser.write(configfile)


