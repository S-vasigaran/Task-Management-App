import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app
from database import Base, get_db

TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def register_and_login(username="testuser", password="testpass"):
    client.post("/register", json={"username": username, "email": f"{username}@test.com", "password": password})
    res = client.post("/login", json={"username": username, "password": password})
    return res.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ── Auth ──────────────────────────────────────────────────────

def test_register_success():
    res = client.post("/register", json={"username": "alice", "email": "alice@test.com", "password": "secret"})
    assert res.status_code == 201
    assert res.json()["username"] == "alice"


def test_register_duplicate_username():
    client.post("/register", json={"username": "alice", "email": "alice@test.com", "password": "secret"})
    res = client.post("/register", json={"username": "alice", "email": "other@test.com", "password": "secret"})
    assert res.status_code == 400


def test_login_success():
    register_and_login()
    res = client.post("/login", json={"username": "testuser", "password": "testpass"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password():
    register_and_login()
    res = client.post("/login", json={"username": "testuser", "password": "wrong"})
    assert res.status_code == 401


# ── Tasks ─────────────────────────────────────────────────────

def test_create_task():
    token = register_and_login()
    res = client.post("/tasks", json={"title": "Buy milk"}, headers=auth_headers(token))
    assert res.status_code == 201
    assert res.json()["title"] == "Buy milk"


def test_get_tasks():
    token = register_and_login()
    client.post("/tasks", json={"title": "Task 1"}, headers=auth_headers(token))
    client.post("/tasks", json={"title": "Task 2"}, headers=auth_headers(token))
    res = client.get("/tasks", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["total"] == 2


def test_get_single_task():
    token = register_and_login()
    created = client.post("/tasks", json={"title": "Single"}, headers=auth_headers(token)).json()
    res = client.get(f"/tasks/{created['id']}", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["title"] == "Single"


def test_mark_task_completed():
    token = register_and_login()
    task = client.post("/tasks", json={"title": "Do laundry"}, headers=auth_headers(token)).json()
    res = client.put(f"/tasks/{task['id']}", json={"completed": True}, headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["completed"] is True


def test_delete_task():
    token = register_and_login()
    task = client.post("/tasks", json={"title": "Delete me"}, headers=auth_headers(token)).json()
    res = client.delete(f"/tasks/{task['id']}", headers=auth_headers(token))
    assert res.status_code == 204


def test_cannot_access_other_users_task():
    token1 = register_and_login("user1", "pass1")
    token2 = register_and_login("user2", "pass2")
    task = client.post("/tasks", json={"title": "Private"}, headers=auth_headers(token1)).json()
    res = client.get(f"/tasks/{task['id']}", headers=auth_headers(token2))
    assert res.status_code == 404


def test_filter_by_completed():
    token = register_and_login()
    t = client.post("/tasks", json={"title": "Done task"}, headers=auth_headers(token)).json()
    client.post("/tasks", json={"title": "Pending task"}, headers=auth_headers(token))
    client.put(f"/tasks/{t['id']}", json={"completed": True}, headers=auth_headers(token))

    done = client.get("/tasks?completed=true", headers=auth_headers(token)).json()
    pending = client.get("/tasks?completed=false", headers=auth_headers(token)).json()

    assert done["total"] == 1
    assert pending["total"] == 1


def test_unauthenticated_request():
    res = client.get("/tasks")
    assert res.status_code == 401
