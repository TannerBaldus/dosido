from pathlib import Path
from configparser import NoOptionError
import os
import string

from markdown import markdown
from exceptions import *
import panflute


class FileArticle(object):

    def __init__(self, file_path, config, api_client):
        self.file_path = file_path
        self.image_host = config.get("site_details", "image_host")
        self.api_client = api_client
        self.config = config
        base_name = os.path.basename(file_path)
        self.slug = base_name
        self.title = string.capwords(" ".join(base_name.split("_")))

    @property
    def collection_id(self):
        collection_name = Path(self.file_path).parent.name
        try:
            return self.config.get("collections", collection_name)
        except NoOptionError:
            raise CollectionNotSetup(collection_name)

    def _convert_text(self, skip_internals):
        file_text = open(self.file_path).read()
        text = markdown(file_text, extensions=["codehilite", "fenced_code", "admonition", "toc"])
        elements = panflute.convert_text(text, input_format="html", output_format="panflute")
        curried_replace_links = lambda elem, doc: self.replace_links(elem, doc, skip_internals=skip_internals)
        for node in elements:
            node.walk(curried_replace_links)
        return panflute.convert_text(elements, input_format="panflute", output_format="html")

    def replace_links(self, elem, doc, skip_internals):
        if type(elem) == panflute.Image:
            elem.url = "{}/{}".format(self.image_host, elem.url)

        if type(elem) == panflute.Link and self.is_internal_link(elem) and not skip_internals:
            linked_article = FileArticle(elem.url, self.config, self.api_client)
            elem.url = linked_article.public_url

    @property
    def public_url(self):
        article_response = self.api_client.get_article_by_slug(self.slug)
        if not article_response:
            raise LinkedArticleNotFound(self.slug)
        return article_response["url"]

    @staticmethod
    def is_internal_link(elem):
        return not elem.url.startswith("http")
