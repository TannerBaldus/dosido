import pytest

from dosido.helpscout_orm import Collection


@pytest.fixture
def mock_config(mocker):
    mock_config = mocker.patch('dosido.config.DosidoConfig')
    mock_config.asset_host = "http://test.com"
    mock_config.get_collection.return_value = 1
    mock_config.site_id = 2
    return mock_config

@pytest.fixture
def mock_api_client(mocker):
    client = mocker.patch("dosido.api.ApiClient")
    client.create_collection.return_value = {"collection": {"id": 1}}
    return client


def test_collection_id(mock_config):
    assert Collection(mock_config, "bar").id == 1


@pytest.mark.parametrize("name, private, no_dir, dir_exists", [
    ("bar", True, True, False),
    ("far", False, False, False),
    ("bur", True, False, True)
])
def test_create_collection(mocker, mock_config, mock_api_client, name, private, no_dir, dir_exists):
    visibility = "private" if private else "public"
    mock_os = mocker.patch("dosido.helpscout_orm.collection.os")
    mock_os.makedirs.return_value = None
    mock_os.path = mocker.MagicMock()
    mock_os.path.isdir.return_value = dir_exists

    collection = Collection(mock_config, name)
    collection.api_client = mock_api_client
    collection.create(private, no_dir)
    mock_api_client.create_collection.assert_called_with(2, name, visibility)
    if no_dir or dir_exists:
        assert not mock_os.makedirs.called, "An attempt to create a dir was made but shouldn't have"
    else:
        assert not mock_os.makedirs.assert_called_with("{}/media".format(name))





