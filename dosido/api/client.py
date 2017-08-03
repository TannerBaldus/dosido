import json

import requests

from dosido.exceptions import *


class ApiClient(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://docsapi.helpscout.net/v1"
        self.session = requests.Session()
        self.session.auth = (api_key, "X")

    @staticmethod
    def _remove_empty_params(params, to_json=True):
        filtered_data = {k: v for k, v in params.items() if v is not None}
        if to_json:
            return json.dumps(filtered_data)
        return filtered_data

    def _http_action(self, url, action_name, is_content_json=True, is_response_json=True, **kwargs):

        if is_content_json:
            headers = {"Content-Type": "application/json"}
            kwargs["headers"] = headers

        url = "{}/{}".format(self.base_url, url)

        if action_name == "GET":
            response = self.session.get(url,  **kwargs)

        if action_name == "PUT":
            response = self.session.put(url, **kwargs)

        if action_name == "POST":
            response = self.session.post(url, **kwargs)

        if action_name == "DELETE":
            response = self.session.delete(url, **kwargs)

        if not response.ok:
            self._handle_errors(response)

        if is_response_json:
            return response.json()
        return response.text

    @staticmethod
    def _handle_errors(response):
        response_body = response.json()
        if "Article name is already in use" in response_body.get("name", [""])[0]:
            raise ArticleAlreadyExists(response_body.get("name")[0])
        raise RuntimeError("API raised code {} with message {}".format(response.status_code, response.text))


    def post(self, url, post_data, **kwargs):
        return self._http_action(url, "POST", data=self._remove_empty_params(post_data,),
                                 **kwargs)

    def get(self, url, query_params={}, **kwargs):
        return self._http_action(url, "GET", params=self._remove_empty_params(query_params, to_json=False), **kwargs)

    def delete(self, url, **kwargs):
        return self._http_action(url, "DELETE" **kwargs)

    def put(self, url, put_data, **kwargs):
        return self._http_action(url, "PUT", data=self._remove_empty_params(put_data), **kwargs)

    def get_site_by_sub_domain(self, sub_domain):
        for site in self.get("sites")["sites"]["items"]:
            if site["subDomain"] == sub_domain:
                return site

    def create_site(self, sub_domain, title):
        post_data = {"subDomain": sub_domain, "title": title, "reload": True}
        return self.post("sites", post_data)

    def create_collection(self, site_id, name, visibility):
        post_data = {"name": name, "site_id": site_id, "visibility": visibility, "reload": True}
        return self.post("collections", post_data)

    def get_collection_by_slug(self, collection_slug):
        collections = self.get("collections")["collections"]["items"]
        for collection in collections:
            if collection["slug"] == collection_slug:
                return collection
        return None

    def create_article(self, collection_id, name, text,
                       status=None, slug=None, categories=None, related=None):
        post_data = {"text": text, "collectionId": collection_id, "status": status, "name":name,
                     "slug": slug, "categories": categories, "related": related, "reload": True}
        return self.post("articles", post_data)["article"]

    def search_articles(self, query, collection_id=None, status=None, visibility=None):
        query_params = {"query": query, "collectionId": collection_id, "status": status,
                        "visibility	": visibility}
        return self.get("search/articles", query_params)

    def get_article_by_slug(self, slug, collection_id=None):
        articles = self.search_articles(slug, collection_id)["articles"]["items"]
        for article in articles:
            if article["slug"] == slug:
                return article

    def delete_article(self, article_id):
        return self.delete("articles/{}".format(article_id))

    def update_article(self, article_id, text=None, name=None, status=None, slug=None, categories=None, related=None):
        post_data = {"text": text, "status": status, "slug": slug, "categories": categories,
                     "related": related, "reload": True, "name": name}
        return self.put("articles/{}".format(article_id), post_data)["article"]

    def save_draft(self, article_id, text):
        post_data = {"text": text}
        return self.post(url="articles/{}/drafts".format(article_id), post_data=post_data, is_response_json=False)
