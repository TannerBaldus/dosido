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


from glob import glob
import configparser
import os
import sys

from docopt import docopt
from distutils.util import strtobool
from api.client import ApiClient


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





class Dosido(object):

    def __init__(self):
        self.config_filename = "config.ini"
        self.config = configparser.ConfigParser()
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
            sys.exit()

        if cmd_args["article"]:
            file_pattern = cmd_args["<file-pattern>"]
            if cmd_args["new"]:
                self.article_create(file_pattern, cmd_args["--publish"])
            if cmd_args["update"]:
                self.article_update(file_pattern, cmd_args["--draft"])

        elif cmd_args["collection"]:
            self.new_collection(cmd_args["<name>"], self.config["site_id"], cmd_args["--private"])

        print("Done")

    def initialize(self):
        api_key = query_user("What is your api key?")
        self.config.set("api_info", "api_key",  api_key)
        self.api_client = ApiClient(api_key)

        site_id = self.setup_site()
        self.config.set("api_info", "site_id", str(site_id))
        collections = self.setup_collections(site_id)
        for name, collection_id in collections.items():
            self.config.set("collections", name, collection_id)
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
            self._create_article(FileArticle(p, self.config))

    def article_update(self, file_pattern, draft):
        file_paths = self._get_md_files(file_pattern)
        for p in file_paths:
            self._update_article(FileArticle(p, self.config, temp=True))
        pass

    def _create_article(self, file_article, temp=False):
        name = file_article.temp_name if temp else file_article.name
        return self.api_client.upload_article(file_article.file_obj, file_article.collection_id, name)

    def _update_article(self, file_article):
        tmp_article = self._create_article(file_article, temp=True)
        parsed_markdown = tmp_article["text"]
        article_id = self.api_client.get_article_by_slug(file_article.name, collection_id=file_article.collection_id)
        updated_article = self.api_client.update_article(article_id, text=parsed_markdown)
        self.api_client.delete(tmp_article['id'])
        return updated_article


def main():
    args = docopt(__doc__)
    d = Dosido()
    d.dispatch(args)

if __name__ == '__main__':
    main()













