import pathlib
from unittest import mock

import cards
import pytest
from cards.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_version():
    result = runner.invoke(app, args=["version"])
    print(f"version: {result.stdout}")
    assert result.stdout.rstrip() == "1.0.0"


def test_mock_version():
    with mock.patch.object(cards, "__version__", "1.2.3"):
        result = runner.invoke(app, args=["version"])
        print(f"version: {result.stdout}")
        assert result.stdout.rstrip() == "1.2.3"


def test_config():
    with mock.patch.object(cards.CardsDB, "path", mock.Mock(return_value="abc")):
        result = runner.invoke(app, ["config"])
        print(f"path: {result.stdout}")
        assert result.stdout.rstrip() == "abc"


@pytest.fixture
def mock_cards_db():
    with mock.patch.object(cards, "CardsDB", autospec=True) as mock_cards_db:
        yield mock_cards_db.return_value


def test_config_using_mock_db(mock_cards_db):
    mock_cards_db.path.return_value = "/foo"
    result = runner.invoke(app, ["config"])
    print(f"path: {result.stdout}")
    assert result.stdout.rstrip() == "/foo"


def test_mock_path():
    with mock.patch.object(cards, "CardsDB", autospec=True) as mock_cards_db:
        mock_cards_db.return_value.path.return_value = "foo"
        with cards.cli.cards_db() as db:
            print(f"db.path={db.path}")
            print(f"db.path()={db.path()}")
        mock_cards_db.return_value.path.assert_called_once_with()
        mock_cards_db.return_value.close.assert_called_once_with()
        mock_cards_db.assert_called_once_with(pathlib.Path.home() / "cards_db")


def test_card_add(mock_cards_db):
    mock_cards_db.add_card = mock.Mock()
    runner.invoke(app, ["add", "foo", "bar", "baz"])
    mock_cards_db.add_card.assert_called_once_with(
        cards.Card("foo bar baz", None, state="todo"),
    )
