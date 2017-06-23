#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HS Docs.

Usage:
  dosido init
  dosido article new <file-pattern> [--publish]
  dosido article update <file-pattern> [--draft]
  dosido collection new <name> [--private]

Options:
  -h --help     Show this screen.
  --version     Show version.
  --draft       Make the update only a draft.
  --private     Make the collection private.
"""

from pathlib import Path
from ConfigParser import SafeConfigParser
from glob import glob
import os

from docopt import docopt
from distutils.util import strtobool
from api.client import ApiClient


def query_user(query, yes_no=False):
    if yes_no:
        answer = None
        while answer is None:
            try:
                answer = bool(strtobool(raw_input("{} (yes/no)\n".format(query))))
            except ValueError:
                answer = bool(strtobool(raw_input("Please answer yes, y, n or no.\n")))
        return answer
    return raw_input("{}\n".format(query))


class Dosido():

    def __init__(self):
        self.config_filename = "config.ini"
        self.config = SafeConfigParser()
        self.config.read(self.config_filename)
        self.api_key = (self.config.has_option("api_info", "api_key") and self.config.get("api_info", "api_key")) or None
        self.api_client = None if not self.api_key else ApiClient(self.api_key)

    def _get_md_files(self, file_pattern):
        file_paths = [i for i in glob(file_pattern) if i.endswith(".md")]
        if not file_paths:
            raise ValueError("No md files found")
        return file_paths

    def dispatch(self, cmd_args):
        if cmd_args["init"]:
            self.initialize()
            return

        if not self.api_client:
            print("Dosido has not been configured. Run: dosido init")
            return

        if cmd_args["article"]:
            file_pattern = cmd_args["<file-pattern>"]
            if cmd_args["new"]:
                self.article_create(file_pattern, cmd_args["--publish"])
            if cmd_args["update"]:
                self.article_update(file_pattern, cmd_args["--draft"])
            return

        if cmd_args["collection"]:
            self.new_collection(cmd_args["<name>"], self.config["site_id"], cmd_args["--private"])
            return

    def initialize(self):
        api_key = query_user("What is your api key?")
        self.config.set("api_info", "api_key",  api_key)
        self.api_client = ApiClient(api_key)

        site_id = self.setup_site()
        self.config.set("api_info", "site_id", str(site_id))
        collections = self.setup_collections(site_id)
        for name, collection_id in collections.iteritems():
            self.config.set("collections", name, collection_id)
        # collections = self.setup_collections(site_id)
        # self.config["collections"] = collections
        self.config.write(open(self.config_filename, "w"))

    def setup_site(self):
        has_site = query_user("Do you have already have a knowledge base site?", yes_no=True)
        if has_site:
            sub_domain = query_user("What is the sub domain?")
            site = self.api_client.get_site_by_sub_domain(sub_domain)
        else:
            sub_domain = query_user("Provide a sub domain for your site. Url will be subdomain.helpscoutdocs.com?")
            title = query_user("Provide a title for your site.")
            site = self.api_client.create_site(sub_domain, title)
        return site["id"]

    def setup_collections(self, site_id):
        another = True
        collections = {}

        while another:
            name = query_user("Provide a name for the collection.")
            private = query_user("Should this collection be private? Default is public.", yes_no=True)
            collection = self.new_collection(name, site_id, private)
            collections[name] = collection["id"]
            os.makedirs(name)
            another = query_user("Would you like to make another collection?", yes_no=True)
        return collections

    def new_collection(self, name, site_id, private):
        visibility = "private" if private else "public"
        return self.api_client.create_collection(site_id, name, visibility)["collection"]

    def article_create(self, file_pattern, publish):
        file_paths = self._get_md_files(file_pattern)
        for p in file_paths:
            self._create_article(p)

    def article_update(self, file_pattern, draft):
        pass

    def _create_article(self, file_path, temp=False):
        file_obj = open(file_path, "r")
        article_name = "{}_tmp".format(file_obj.name) if temp else None
        return self.api_client.upload_article(file_obj, self._get_collection_id_from_path(file_path), article_name)

    def _update_article(self, file_path):
        tmp_article = self._create_article(file_path)
        parsed_markdown = tmp_article["text"]


    def _get_collection_id_from_path(self, file_path):
        collection_name = Path(file_path).parent.name
        collection_id = self.config.get("collections", collection_name)
        return collection_id


def main():
    args = docopt(__doc__)
    d = Dosido()
    d.dispatch(args)

if __name__ == '__main__':
    main()













