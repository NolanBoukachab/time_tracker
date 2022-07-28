import pytest

from pathlib import Path
from time_tracker.app import app, close_db, get_db, init_db


@pytest.fixture()
def setup_db():
    def delete_db():
        db_path = Path(__file__).parent.parent / "time_tracker.db"
        db_path.unlink(missing_ok=True)

    delete_db()
    with app.app_context():
        init_db()
    yield
    delete_db()


@pytest.fixture()
def db(setup_db):
    with app.app_context():
        conn = get_db()
        yield conn
        close_db(None)


@pytest.fixture()
def create_user(db):
    def wrapped(username, password):
        db.execute(
            """
            INSERT INTO users(username, password)
            VALUES (:username, :password)
            """,
            dict(username=username, password=password),
        )
        db.commit()

        user = db.execute(
            """
            SELECT * FROM users
            WHERE username = :username
            """,
            dict(username=username),
        ).fetchone()

        return user

    return wrapped


@pytest.fixture()
def client():
    return app.test_client()


def test_add_event_success(db, create_user, client):
    # arrange
    user = create_user("john", "test")
    with client.session_transaction() as sess:
        sess["user_id"] = user["id"]

    # act
    params = dict(date="2022-01-01", hours="7", comments="Work")
    response = client.post("/add_event", data=params)

    # assert
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert len(db.execute("SELECT * FROM events").fetchall()) == 1


def test_add_event_fail(db, create_user, client):
    # arrange
    user = create_user("john", "test")
    with client.session_transaction() as sess:
        sess["user_id"] = user["id"]

    # act
    params = dict(date="2022-01-01", hours="0", comments="Work")
    response = client.post("/add_event", data=params)

    # assert
    assert response.status_code == 304
    assert response.headers["Location"] == "/"
    assert len(db.execute("SELECT * FROM events").fetchall()) == 0
