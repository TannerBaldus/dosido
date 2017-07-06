from pathlib import Path
from configparser import NoOptionError
import string

from markdown import markdown
from bs4 import BeautifulSoup


from exceptions import *
from .base import BaseObject


class Article(BaseObject):

    def __init__(self, file_path, config):
        super().__init__(config)
        self.file_path = file_path

        base_name = Path(file_path).stem
        self.slug = self._path_to_slug(base_name)
        self.title = string.capwords(" ".join(base_name.split("_")))

    def create(self, skip_internals, publish):
        status = "published" if publish else "notpublished"
        return self.api_client.create_article(self.collection_id, self.title, self._convert_text(skip_internals),
                                       slug=self.slug, status=status)

    def update(self, is_draft, skip_internals):
        if is_draft:
            return self.api_client.save_draft(self._article_id, self._convert_text(skip_internals))
        return self.api_client.update_article(self._article_id, text=self._convert_text(skip_internals))

    @property
    def _article_id(self):
        article_response = self.api_client.get_article_by_slug(self.slug, collection_id=self.collection_id)
        if not article_response:
            raise ArticleDoesNotExist(self.slug)
        return article_response["id"]

    @property
    def collection_id(self):
        collection_name = Path(self.file_path).parent.name
        try:
            return self.config.get("collections", collection_name)
        except NoOptionError:
            raise CollectionNotSetup(collection_name)

    @staticmethod
    def _path_to_slug(path_string):
        use_dashes = path_string.replace("_", "-")
        # for when an article links to another's specific paragraph like /heroes/squirrel_girl#origins
        ignore_paragraph_link = use_dashes.split("#")[0]
        return ignore_paragraph_link

    def _convert_text(self, skip_internals):
        file_text = open(self.file_path).read()
        rendered_html = markdown(file_text, extensions=["codehilite", "fenced_code", "admonition", "toc"])
        return self._update_references_for_helpscout(rendered_html, skip_internals)

    def _update_references_for_helpscout(self, html, skip_internals):
        soup = BeautifulSoup(html,  "html.parser")
        if not skip_internals:
            self._convert_internal_links(soup)
        self._convert_image_links(soup)
        return str(soup)

    def _convert_image_links(self, soup):
        img_tags = soup.find_all("img")
        for tag in img_tags:
            if self._is_internal_link(tag):
                tag["src"] = "{}/{}".format(self.config.image_host, tag["src"])

    def _convert_internal_links(self, soup):
        anchor_tags = soup.find_all("a")
        for tag in anchor_tags:
            if self._is_internal_link(tag):
                tag["href"] = FileArticle(tag["href"], self.config, self.api_client)._public_url

    @property
    def _public_url(self):
        article_response = self.api_client.get_article_by_slug(self.slug)
        if not article_response:
            raise LinkedArticleNotFound(self.slug)
        return article_response["url"]

    @staticmethod
    def _is_internal_link(anchor_tag):
        return not anchor_tag["href"].startswith("http")
