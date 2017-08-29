class LinkedArticleNotFound(RuntimeError):

    def __init__(self, title, collection):
        self.title = title
        self.collection_name = collection.name
        super().__init__(title)


class ArticleDoesNotExist(RuntimeError):
    def __init__(self, title):
        self.title = title
        super().__init__(title)


class ArticleAlreadyExists(RuntimeError):
    def __init__(self, message):
        super().__init__(message)


class CollectionNotSetup(RuntimeError):
    def __init__(self, collection_name):
        self.collection_name = collection_name
        super().__init__(collection_name)


class DosidoNotInitialized(RuntimeError):

    def __init__(self):
        super().__init__("Dosido not setup")

