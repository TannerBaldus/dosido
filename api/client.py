import requests

class ApiClient(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://docsapi.helpscout.net/v1"
        self.session = requests.Session()
        self.session.auth = (api_key, "X")
        self.session.headers.update({"Content-Type": "application/json"})

    @staticmethod
    def _remove_empty_params(params):
        import json
        return json.dumps({k: v for k, v in params.iteritems() if v is not None})

    def _http_action(self, url, action_name, **kwargs):
        url = "{}/{}".format(self.base_url, url)

        if action_name == "GET":
            response = self.session.get(url, **kwargs)

        if action_name == "PUT":
            response = self.session.put(url, **kwargs)

        if action_name == "POST":
            response = self.session.post(url, **kwargs)

        if action_name == "DELETE":
            response = self.session.delete(url, **kwargs)

        print response.json()
        if not response.ok:
            raise RuntimeError("API raised code {} with message {}".format(response.status_code, response.text))
        return response.json()

    def post(self, url, post_data, **kwargs):
        return self._http_action(url, "POST", data=self._remove_empty_params(post_data), **kwargs)

    def get(self, url, query_params={}, **kwargs):
        return self._http_action(url, "GET", params=self._remove_empty_params(query_params), **kwargs)

    def delete(self, url, **kwargs):
        return self._http_action(url, "DELETE" **kwargs)

    def put(self, url, put_data, **kwargs):
        return self._http_action(url, "PUT", data=self._remove_empty_params(put_data), **kwargs)

    def get_site_by_sub_domain(self, sub_domain):
        for site in self.get("sites")["items"]:
            if site["subDomain"] == sub_domain:
                return site

    def create_site(self, sub_domain, title):
        return {"id": 4}

    def create_collection(self, site_id, name, visibility):
        post_data = {"name": name, "site_id": site_id, "visibility": visibility, "reload": True}
        return self.post("collections", post_data)

    def get_collection_by_slug(self, collection_slug):
        collections = self.get("collections")["items"]
        for collection in collections:
            if collection["slug"] == collection_slug:
                return collection
        return None

    def upload_article(self, file_obj, collection_id, name):
        article_file = {"file": file_obj}
        post_data = {"key": self.api_key, "collectionId": collection_id, "reload": True,
                     "name": name}
        return self.post("articles/upload", post_data, files=article_file)["article"]

    def search_articles(self, query, collection_id=None, status=None, visibility=None):
        query_params = {"query": query, "collectionId": collection_id, "status": status,
                        "visibility	": visibility}
        return self.get("search/articles", query_params)

    def get_article_by_slug(self, slug, collection_id=None):
        articles = self.search_articles(slug, collection_id)["articles"]["items"]
        for article in articles:
            if  article["slug"] == slug:
                return article

    def delete_article(self, article_id):
        return self.delete("articles/{}".format(article_id))

    def update_article(self, article_id, text=None, status=None, slug=None, categories=None, related=None):
        post_data = {"text": text, "status": status, "slug": slug, "categories": categories,
                     "related": related, "reload": True}
        return self.post("articles/{}".format(article_id), post_data)



