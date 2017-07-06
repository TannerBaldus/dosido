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
from config import DosidoConfig, config_setup
from helpscout_orm import Article, Collection
from exceptions import *


class Dosido(object):
    
    @classmethod
    def _get_md_files(cls, file_pattern):
        file_paths = [i for i in glob(file_pattern) if i.endswith(".md")]
        if not file_paths:
            raise ValueError("No md files found")
        return file_paths

    @classmethod
    def dispatch(cls, cmd_args):
        if cmd_args["init"]:
            cls.initialize()
            return

        if not cls.api_client:
            print("Dosido has not been configured. Run: dosido init")
            sys.exit()

        if cmd_args["article"]:
            file_pattern = cmd_args["<file-pattern>"]
            if cmd_args["new"]:
                cls.article_create(file_pattern, cmd_args["--publish"], cmd_args["--skip-internals"])
            if cmd_args["update"]:
                cls.article_update(file_pattern, cmd_args["--draft"], cmd_args["--skip-internals"])

        elif cmd_args["collection"]:
            cls.new_collection(cmd_args["<name>"], cmd_args["--private"], cmd_args["--no-dir"])

        print("Done")

    @classmethod
    def initialize(cls):
        config_setup.initialize()


    def new_collection(cls, name, private, no_dir):
        if not no_dir:
            os.makedirs(name)
        return Collection(DosidoConfig(), name).create(private)

    def article_create(cls, file_pattern, skip_internals, publish):
        for p in cls._get_md_files(file_pattern):
            file_article = Article(p, DosidoConfig())
            print("Creating HelpScout article from {}".format(file_article.file_path))
            file_article.create(skip_internals, publish)
            print("created")

    def article_update(cls, file_pattern, is_draft, skip_internals):
        file_paths = cls._get_md_files(file_pattern)
        for p in file_paths:
            file_article = Article(p, DosidoConfig())
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













