import time

import cards
import pytest


@pytest.fixture(scope="session")
def db(tmp_path_factory):
    path = tmp_path_factory.mktemp("cards_db")
    db = cards.CardsDB(path)
    yield db
    db.close()


@pytest.fixture
def cards_db(db):
    db.delete_all()


@pytest.fixture(autouse=True, scope="session")
def footer_session_scope():
    """Report the time at the end of the session."""
    yield
    now = time.time()
    print("\n--")
    print(f"finished: {time.strftime('%d %b %X', time.localtime(now))}")


def test_db_empty(db, cards_db):
    assert db.count() == 0


def test_two(db, cards_db):
    db.add_card(cards.Card("test_card", owner="test_suite"))
    db.add_card(cards.Card("test_card_1", owner="test_suite"))
    assert db.count() == 2


def test_three(db, cards_db):
    db.add_card(cards.Card("first"))
    db.add_card(cards.Card("second"))
    db.add_card(cards.Card("third"))
    assert db.count() == 3


def test_version(capsys):
    cards.cli.version()
    output = capsys.readouterr().out.rstrip()
    assert output == cards.__version__


def test_card_db(monkeypatch, tmp_path):
    def get_temp_path():
        return tmp_path

    monkeypatch.setattr(cards.cli, "get_path", get_temp_path)
    with cards.cli.cards_db() as db:
        assert db.path() == tmp_path


def test_card_db_uses_env_var(monkeypatch, tmp_path_factory):
    path = tmp_path_factory.mktemp("card_db")
    monkeypatch.setenv("CARDS_DB_DIR", path)
    with cards.cli.cards_db() as db:
        assert db.path() == path


def test_card_db_uses_home_path(monkeypatch, tmp_path):
    fake_home_path = tmp_path / "cards_db"

    def get_fake_home():
        return tmp_path

    monkeypatch.setattr(cards.cli.pathlib.Path, "home", get_fake_home)
    with cards.cli.cards_db() as db:
        assert db.path() == fake_home_path
