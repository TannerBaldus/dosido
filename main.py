#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HS Docs.

Usage:
  dosido init
  dosido article new <file-pattern> [--publish --skip-internals]
  dosido article update <file-pattern> [--draft --skip-interals]
  dosido collection new <name> [--private --no-dir]

Options:
  -h --help                Show this screen.
  --version                Show version.
  -d --draft               Make the update only a draft.
  --private                Make the collection private.
  -s --skip-internals      don't try to link to other articles since they might not be in HelpScout yet
  -nd --no-dir             don't make a directory for the collection
"""


from glob import glob
import configparser
import os
import sys

from docopt import docopt
from distutils.util import strtobool

from api.client import ApiClient
from FileArticle import FileArticle
from exceptions import *



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
                self.article_create(file_pattern, cmd_args["--publish"], cmd_args["--skip-internals"])
            if cmd_args["update"]:
                self.article_update(file_pattern, cmd_args["--draft"], cmd_args["--skip-internals"])

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

    def new_collection(self, name, site_id, private, no_dir):
        visibility = "private" if private else "public"
        if not no_dir:
            os.makedirs(name)
        return self.api_client.create_collection(site_id, name, visibility)["collection"]

    def article_create(self, file_pattern, skip_internals, publish):
        for p in self._get_md_files(file_pattern):
            file_article = FileArticle(p, self.config, self.api_client)
            print("Creating HelpScout article from {}".format(file_article.file_path))
            file_article.create(skip_internals, publish)
            print("created")

    def article_update(self, file_pattern, is_draft, skip_internals):
        file_paths = self._get_md_files(file_pattern)
        for p in file_paths:
            file_article = FileArticle(p, self.config, self.api_client)
            print("Updating {}".format(file_article.file_path))
            file_article.update(is_draft, skip_internals)
            print("updated")
        pass

def main():
    args = docopt(__doc__)
    d = Dosido()

    try:
        d.dispatch(args)
    except ArticleDoesNotExist as e:
        print("Couldn't find article with slug {}. Did you call dosido article new first?".format(e.slug))
    except LinkedArticleNotFound as e:
        print(("There was no public url for the linked article with slug {0}.\n"
               "Try using --skip-internals then updating once {0} is uploaded to help scout").format(e.slug))
    except CollectionNotSetup as e:
        print("There is no collection {} in help scout. Run dosido collection new".format(e.collection_name))

if __name__ == '__main__':
    main()













