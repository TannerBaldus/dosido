# coding: utf-8
from api.client import ApiClient
api_key = "63bd9b2c7c4e8bf66130e7d64815cfb90affb780"
a = ApiClient(api_key)
f =  open("pill/foo.md")
r = a.upload_article(f, "5939de0904286305c68cf287", None)
