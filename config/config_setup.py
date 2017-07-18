from pathlib import Path
from distutils.util import strtobool
import os

from .constants import *
from .dosido_config import DosidoConfig
from helpscout_orm import Collection, Site


def initialize():
    if not os.path.isdir(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)

    if not os.path.isfile(CONFIG_FILEPATH):
        Path(CONFIG_FILEPATH).touch()

    config = DosidoConfig()
    api_key = query_user("What is your api key?")
    config.api_key = api_key

    site_id = setup_site(config)
    config.site_id = site_id

    config.first_header_as_title = query_user(("Would you like to use the text of the first h1 tag as the title for your articles?\n"
                                               "The default is creating a title from underscore delimited file name from the article.\n "
                                               "e.g. example_article-1 becomes Example Article-1\n"
                                               ))

    collections = setup_collections(config)
    for name, collection_id in collections.items():
        config.add_collection(name, collection_id)

    config.asset_host = input(("What is the url that you are going to host your assets."
                               "\nUsually this will be your git repo's gh pages url.\n"))
    config.save()


def setup_site(config):
    has_site = query_user("Do you have already have a knowledge base site?", yes_no=True)
    if has_site:
        sub_domain = query_user("What is the sub domain?")
        site = Site(config, sub_domain).get()
    else:
        sub_domain = query_user("Provide a sub domain for your site. Url will be subdomain.helpscoutdocs.com?")
        title = query_user("Provide a title for your site.")
        site = Site(config, sub_domain).create(title)
    return site["id"]


def setup_collections(config):
    another = True
    collections = {}

    while another:
        name = query_user("Provide a name for the collection.")
        private = query_user("Should this collection be private? Default is public.", yes_no=True)
        collection = Collection(config, name).create(private)
        collections[name] = collection["id"]
        os.makedirs(name)
        another = query_user("Would you like to make another collection?", yes_no=True)
    return collections


def query_user(query, yes_no=False):
    if yes_no:
        answer = None
        while answer is None:
            try:
                answer = bool(strtobool(input("{} (yes/no)\n".format(query))))
            except ValueError:
                answer = bool(strtobool(input("Please answer yes, y, n or no.\n")))
        return answer
    return input("{}\n".format(query))

