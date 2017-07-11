import pytest

from config import DosidoConfig
from helpscout_orm import Article


@pytest.fixture
def mock_config(mocker):
    mock_config = mocker.patch('config.DosidoConfig')
    mock_config.asset_host = "http://test.com"
    mock_config.get_collection.return_value = 1
    return mock_config


@pytest.fixture
def mock_api_client(mocker):
    client = mocker.patch("api.ApiClient")
    article_url = "helpscout.com/article"
    article = {"url": article_url, "id": 1}
    client.get_article_by_slug.return_value = article
    client._http_action.return_value = {"article": article, "articles": {"items": [article]}}
    return client

@pytest.mark.parametrize("test_text, skip_articles, expected", [
    ('![alt text](media/foo.png)', False, '<img alt="alt text" src="http://test.com/bar/media/foo.png"/>'),
    ("[testing](http://google.com)", False, '<a href="http://google.com">testing</a>'),
    ("[foo](media/foo.png)", False, '<a href="http://test.com/bar/media/foo.png">foo</a>'),
    ("[bar](#some-paragraph)", False, '<a href="#some-paragraph">bar</a>'),
    ("[bar](other/article.md)", True,'<a href="other/article.md">bar</a>'),
    ("[bar](other/article.md)", False,'<a href="helpscout.com/article">bar</a>')
])
def test_convert_text(mocker, mock_api_client, mock_config, test_text, skip_articles, expected):
    file_path = "bar/foo.md"
    mocker.patch("builtins.open", mocker.mock_open(read_data=test_text))
    article = Article(file_path, mock_config)
    article.api_client = mock_api_client
    assert article.convert_text(skip_articles) == "<p>{}</p>".format(expected)


@pytest.mark.parametrize("article_path, slug, title, collection_name", [
    ("foo/bar/gar.md", "gar", "Gar", "bar"),
    ("bar/test_file.md", "test-file", "Test File", "bar"),
])
def test_article_info(mocker,  mock_config, mock_api_client, article_path, slug, title, collection_name):
    article = Article(article_path, mock_config)
    article.api_client = mock_api_client
    assert article.slug == slug
    assert article.title == title
    assert article.collection.name == collection_name






