#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HS Docs.

Usage:
  dosido init
  dosido article new <file-pattern> [--publish --skip-article-refs --ignore-existing]
  dosido article update <file-pattern> [--draft --skip-article-refs]
  dosido collection new <name> [--private --no-dir]

Options:
  --help -h                       Show this screen.
  --version                       Show version.
  --draft -d                      Make the update only a draft.
  --publish -pb                   publish the article immediately.
  --private -pr                   Make the collection private.
  --skip-article-refs -s          don't try to link to other articles since they might not be published in HelpScout yet
  --no-dir -nd                    don't make a directory for the collection
  --ignore-existing -i            skip article already exists errors on article creation
"""


from glob import glob

from .config import DosidoConfig, config_setup
from docopt import docopt
from .exceptions import *
from .helpscout_orm import Article, Collection


class Dosido(object):
    
    @staticmethod
    def _get_md_files(file_pattern):
        file_paths = [i for i in glob(file_pattern) if i.endswith(".md")]
        if not file_paths:
            raise ValueError("No md files found")
        return file_paths

    @classmethod
    def dispatch(cls, cmd_args):
        if cmd_args["init"]:
            cls.initialize()

        elif cmd_args["article"]:
            file_pattern = cmd_args["<file-pattern>"]
            if cmd_args["new"]:
                cls.article_create(file_pattern, cmd_args["--skip-article-refs"], cmd_args["--publish"], cmd_args["--ignore-existing"])
            if cmd_args["update"]:
                cls.article_update(file_pattern, cmd_args["--draft"], cmd_args["--skip-article-refs"])

        elif cmd_args["collection"]:
            cls.new_collection(cmd_args["<name>"], cmd_args["--private"], cmd_args["--no-dir"])

        print("Done")

    @staticmethod
    def initialize():
        config_setup.initialize()

    @staticmethod
    def new_collection(name, private, no_dir):
        return Collection(DosidoConfig(), name).create(private, no_dir)

    @staticmethod
    def article_create(file_pattern, skip_internals, publish, ignore_existing):
        for p in Dosido._get_md_files(file_pattern):
            file_article = Article(p, DosidoConfig())
            print("Creating HelpScout article from {}".format(file_article.file_path))
            try:
                file_article.create(skip_internals, publish)
            except ArticleAlreadyExists:
                if not ignore_existing:
                    raise
                print("Article already exists")
                continue
            print("created")

    @staticmethod
    def article_update(file_pattern, is_draft, skip_internals):
        file_paths = Dosido._get_md_files(file_pattern)
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
        print(("There was no public url for the linked article with slug {0} in the collection {1}.\n"
               "Try using --skip-article-refs then updating once {0} is uploaded to help scout").format(e.slug, e.collection_name))
    except CollectionNotSetup as e:
        print("There is no collection {} in help scout. Run dosido collection new".format(e.collection_name))

    except DosidoNotInitialized:
        print("Not a dosido repository (or any of the parent directories): .dosido\nDid you run dosido init?")

    except ArticleAlreadyExists as e:
        print(e)

if __name__ == '__main__':
    main()













