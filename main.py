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

import requests
import json
import os

from docopt import docopt
from distutils.util import strtobool
from api.client import ApiClient

def query_user(query, yes_no=False):
    if yes_no:
        return bool(strtobool(raw_input("{} (y/n)\n".format(query))))
    return raw_input("{}\n".format(query))


def initialize():
    config = {}
    api_key =  query_user("What is your api key?")
    config["api_key"] = api_key
    api_client = ApiClient(api_key)

    site_id = setup_site(api_client)
    config["site_id"] = site_id

    collections = setup_collections(site_id)
    config["collections"] = collections
    print config





def setup_site(api_client):
    has_site = query_user("Do you have already have a knowledge base site?", yes_no=True)

    if has_site:
        sub_domain = query_user("What is the sub domain?")
        site = api_client.get_site_by_sub_domain(sub_domain)
    else:
        sub_domain = query_user("Provide a sub domain for your site. Url will be subdomain.helpscoutdocs.com?")
        title = query_user("Provide a title for your site.")
        site = api_client.create_site(sub_domain, title)

    return site["id"]



def setup_collections(site_id):
    another = True
    collections = {}

    while another:
        name = query_user("Provide a name for the collection.")
        private = query_user("Should this collection be private? Default is public.", yes_no=True)
        collection = new_colletion(name, site_id, private)
        collections[name] = collection["id"]
        os.makedirs(name)
        another = query_user("Would you like to make another collection?", yes_no=True)
    return collections

def  new_colletion(name, site_id, private):
    return {"id": 3}

def article_create(file_pattern, publish):
    pass


def article_update(file_pattern, draft):
    pass


def main():
    args = docopt(__doc__)
    print args
    config = {"site_id": 3}

    if args["init"]:
        initialize()

    if args["article"]:
        file_pattern = args["<file-pattern>"]
        if args["new"]:
            article_create(file_pattern, args["--publish"])
        if args["update"]:
            article_update(file_pattern, args["--draft"])

    if args["collection"]:
        new_colletion(args["<name>"], config["site_id"], args["--private"])


if __name__ == '__main__':
    main()













