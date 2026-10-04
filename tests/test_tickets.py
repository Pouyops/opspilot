import pytest
from httpx import ASGITransport, AsyncClient

from app.db import engine
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    await engine.dispose()


async def test_create_and_get_ticket(client):
    resp = await client.post(
        "/tickets", json={"subject": "Test ticket", "body": "Something broke"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "open"

    resp = await client.get(f"/tickets/{data['id']}")
    assert resp.status_code == 200
    assert resp.json()["subject"] == "Test ticket"


async def test_validation_error(client):
    resp = await client.post("/tickets", json={"subject": "x"})
    assert resp.status_code == 422


async def test_not_found(client):
    resp = await client.get("/tickets/999999")
    assert resp.status_code == 404
