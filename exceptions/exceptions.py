class LinkedArticleNotFound(RuntimeError):

    def __init__(self, slug):
        self.slug = slug
        super().__init__(slug)


class CollectionNotSetup(RuntimeError):
    def __init__(self, collection_name):
        self.collection_name = collection_name
        super().__init__(collection_name)
