from pathlib import Path
import string

from markdown import markdown
from bs4 import BeautifulSoup


from exceptions import *

from .base import BaseObject
from .collection import Collection


class Article(BaseObject):

    def __init__(self, file_path, config):
        super().__init__(config)
        self.file_path = file_path

        base_name = Path(file_path).stem
        self.slug = self._path_to_slug(base_name)
        self.title = string.capwords(" ".join(base_name.split("_")))
        self.collection = Collection(self.config, self.collection_name_from_path(file_path))

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
        article_response = self.api_client.get_article_by_slug(self.slug, collection_id=self.collection.id)
        if not article_response:
            raise ArticleDoesNotExist(self.slug)
        return article_response["id"]
    
    @staticmethod
    def collection_name_from_path(file_path):
        return Path(file_path).parent.name

    @staticmethod
    def _path_to_slug(path_string):
        use_dashes = path_string.replace("_", "-")
        # for when an article links to another's specific paragraph like /heroes/squirrel_girl#origins
        ignore_paragraph_link = use_dashes.split("#")[0]
        return ignore_paragraph_link

    def _convert_text(self, skip_articles):
        file_text = open(self.file_path).read()
        rendered_html = markdown(file_text, extensions=["codehilite", "fenced_code", "admonition", "toc"])
        return self._update_references_for_helpscout(rendered_html, skip_articles)

    def _update_references_for_helpscout(self, html, skip_articles):
        """
        We want the author to continue writing md on github as normal. Which means relative links. So we convert 
        these to markdown friendly here.
        
        :param html: the starting html
        :param skip_articles: ool to skip looking for articles that aren't published so don't have a public url yet 
        :return: the converted htnl
        """
        soup = BeautifulSoup(html,  "html.parser")
        self.convert_reference_tags(soup, "img", "src", skip_articles)
        self.convert_reference_tags(soup, "a", "href", skip_articles)
        return str(soup)

    def convert_reference_tags(self, soup, tag_type, url_property, skip_articles=False):
        """
        General function for finding tags that link to internal items, images, articles, documents etc and making them
        helpscout friendly. General so we don't have to write a new fn for each kinda tag we want to convert.
        
        :param soup: a BeautifulSoup object of the md converted to html
        :param tag_type: type of ref tag, e.g. img, a 
        :param url_property: where the url in the tag is stored, e.g. href,  src
        :param skip_articles: whether to skip converting article links
        :return: None
        """
        tags = soup.find_all(tag_type)
        for tag in tags:
            target_url = tag[url_property]
            if self._is_media_link(target_url):
                tag[url_property] = self._build_asset_link(target_url)

            if self._is_article_link(target_url) and not skip_articles:
                tag[url_property] = Article(target_url, self.config)._public_url

    def _build_asset_link(self, target_url):
        return "{}/{}/{}".format(self.config.asset_host, self.collection.name, target_url)

    @staticmethod
    def _is_article_link(url):
        return Article._is_internal_link(url) and not Article._is_media_link(url)

    @staticmethod
    def _is_media_link(url):
        return Article._is_internal_link(url) and url.starts_with("media")

    @staticmethod
    def _is_internal_link(url):
        return "//" in url

    @property
    def _public_url(self):
        article_response = self.api_client.get_article_by_slug(self.slug)
        if not article_response:
            raise LinkedArticleNotFound(self.slug)
        return article_response["url"]

    def _convert_asset_link(self, tag_url):
        return "{}/{}/{}".format(self.config.asset_host, self.collection.name, tag_url)

