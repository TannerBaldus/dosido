class LinkedArticleNotFound(RuntimeError):

    def __init__(self, slug, collection):
        self.slug = slug
        self.collection_name = collection.name
        super().__init__(slug)


class ArticleDoesNotExist(RuntimeError):
    def __init__(self, slug):
        self.slug = slug
        super().__init__(slug)


class CollectionNotSetup(RuntimeError):
    def __init__(self, collection_name):
        self.collection_name = collection_name
        super().__init__(collection_name)


class DosidoNotInitialized(RuntimeError):

    def __init__(self):
        super().__init__("Dosido not setup")

