import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Use a separate test database so we never touch real data
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_user():
    response = client.post("/register", json={"email": "pytestuser@example.com", "password": "mypassword123"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "pytestuser@example.com"
    assert "id" in data


def test_register_duplicate_email_fails():
    client.post("/register", json={"email": "dupe@example.com", "password": "pass123"})
    response = client.post("/register", json={"email": "dupe@example.com", "password": "pass123"})
    assert response.status_code == 400


def test_login_success():
    client.post("/register", json={"email": "loginuser@example.com", "password": "mypassword123"})
    response = client.post("/login", data={"username": "loginuser@example.com", "password": "mypassword123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_fails():
    client.post("/register", json={"email": "wrongpass@example.com", "password": "correctpass"})
    response = client.post("/login", data={"username": "wrongpass@example.com", "password": "wrongpass"})
    assert response.status_code == 401


def get_auth_headers():
    client.post("/register", json={"email": "appuser@example.com", "password": "mypassword123"})
    login_res = client.post("/login", data={"username": "appuser@example.com", "password": "mypassword123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_application():
    headers = get_auth_headers()
    response = client.post("/applications/", json={
        "company_name": "TestCorp",
        "job_title": "Backend Developer",
        "status": "applied"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "TestCorp"


def test_list_applications_requires_auth():
    response = client.get("/applications/")
    assert response.status_code == 401


def test_full_application_lifecycle():
    headers = get_auth_headers()

    # Create
    create_res = client.post("/applications/", json={
        "company_name": "LifecycleCorp",
        "job_title": "SDE",
        "status": "applied"
    }, headers=headers)
    app_id = create_res.json()["id"]

    # Update
    update_res = client.put(f"/applications/{app_id}", json={"status": "interview"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "interview"

    # Delete
    delete_res = client.delete(f"/applications/{app_id}", headers=headers)
    assert delete_res.status_code == 200