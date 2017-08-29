import string
from pathlib import Path

from bs4 import BeautifulSoup
from markdown import markdown

from dosido.exceptions import *
from .base import BaseObject
from .collection import Collection


class Article(BaseObject):

    def __init__(self, file_path, config):
        super().__init__(config)
        self.file_path = file_path
        self.slug = self._path_to_slug(file_path)
        self.title = ' '.join(Path(file_path).stem.split("_"))
        self.collection = Collection(self.config, self.collection_name_from_path(file_path))

    def create(self, skip_article_refs, publish):
        status = "published" if publish else "notpublished"
        if self._article_id:
            raise ArticleAlreadyExists(self.slug)
        return self.api_client.create_article(self.collection.id, self.title, self.convert_text(skip_article_refs), slug=self.slug, status=status)

    def update(self, is_draft, skip_article_refs, unpublish):
        if not self._article_id:
            raise ArticleDoesNotExist(self.slug)
        if is_draft:
            return self.api_client.save_draft(self._article_id, self.convert_text(skip_article_refs))
        status = "notpublished" if unpublish else None
        return self.api_client.update_article(self._article_id, text=self.convert_text(skip_article_refs),
                                              name=self.title, status=status)
    @property
    def _article_id(self):
        article_response = self.api_client.get_article_by_slug(self.slug, collection_id=self.collection.id)
        return None if not article_response else article_response["id"]

    @staticmethod
    def collection_name_from_path(file_path):
        return Path(file_path).parent.name

    @staticmethod
    def _path_to_slug(path_string):
        article_name = Path(path_string).stem
        use_dashes = article_name.replace("_", "-")
        # for when an article links to another's specific paragraph like /heroes/squirrel_girl#origins
        ignore_paragraph_link = use_dashes.split("#")[0]
        remove_punctuation = "".join(i for i in ignore_paragraph_link if i not in string.punctuation or i == "-")
        return remove_punctuation

    def _md_to_html(self):
        file_text = open(self.file_path).read()
        rendered_html = markdown(file_text, extensions=["codehilite", "fenced_code", "admonition", "toc"])
        return rendered_html

    def convert_text(self, skip_articles):
        soup = BeautifulSoup(self._md_to_html(), "html.parser")
        updated_references = self._update_references_for_helpscout(soup, skip_articles)
        return str(updated_references)

    def _update_references_for_helpscout(self, soup, skip_articles):
        """
        We want the author to continue writing md on github as normal. Which means relative links. So we convert 
        these to markdown friendly here.
        
        :param html: a beautiful soup obj
        :param skip_articles: ool to skip looking for articles that aren't published so don't have a public url yet 
        :return: the converted htnl
        """
        self.convert_reference_tags(soup, "img", "src", skip_articles)
        self.convert_reference_tags(soup, "a", "href", skip_articles)
        return soup

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
            target_url = tag.get(url_property)
            if not target_url:
                continue

            if self._is_media_link(target_url):
                tag[url_property] = self._build_asset_link(target_url)

            if self._is_article_link(target_url) and not skip_articles:
                tag[url_property] = self._get_public_url_from_path(target_url)

    def _build_asset_link(self, target_url):
        return "{}/{}/{}".format(self.config.asset_host, self.collection.name, target_url)

    @staticmethod
    def _is_article_link(url):
        return Article._is_internal_link(url) and not Article._is_media_link(url)

    @staticmethod
    def _is_media_link(url):
        return Article._is_internal_link(url) and url.startswith("media")

    @staticmethod
    def _is_internal_link(url):
        return all(i not in url for i in ["//", "mailto"]) and Article._path_to_slug(url)

    def _public_url(self):
        return self._get_public_url_from_path(self.file_path)

    def _get_public_url_from_path(self, article_path):
        linked_article = Article(article_path, self.config)
        article_response = self.api_client.get_article_by_slug(linked_article.slug)
        if not article_response:
            raise LinkedArticleNotFound(linked_article.slug, linked_article.collection)
        return article_response["url"]

    def _convert_asset_link(self, tag_url):
        return "{}/{}/{}".format(self.config.asset_host, self.collection.name, tag_url)

