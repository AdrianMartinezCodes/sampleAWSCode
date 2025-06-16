import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from aioresponses import aioresponses
from api.project import app  # adjust if needed

BASE_META_URL = "http://some-url/latest/meta-data"


@pytest.mark.asyncio
async def test_metadata_root_keys():
    with aioresponses() as mock:
        mock.get(f"{BASE_META_URL}/", status=200, body="hostname\nami-id\n")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/metadata?meta_data_url={BASE_META_URL}")
            payload = response.json()
            assert response.status_code == 200
            assert payload["status"] == "success"
            assert "available_keys" in payload["data"]
            assert "hostname" in payload["data"]["available_keys"]


@pytest.mark.asyncio
async def test_metadata_specific_key():
    with aioresponses() as mock:
        mock.get(f"{BASE_META_URL}/hostname", status=200, body="ip-10-0-0-1")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/metadata?meta_data_url={BASE_META_URL}&key=hostname"
            )
            payload = response.json()
            assert response.status_code == 200
            assert payload["status"] == "success"
            assert payload["data"]["key"] == "hostname"
            assert payload["data"]["value"] == "ip-10-0-0-1"


@pytest.mark.asyncio
async def test_metadata_key_not_found():
    with aioresponses() as mock:
        mock.get(f"{BASE_META_URL}/not-real", status=404)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/metadata?meta_data_url={BASE_META_URL}&key=not-real"
            )
            assert response.status_code == 502


@pytest.mark.asyncio
async def test_no_metadata_url_provided():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/metadata")
        assert response.status_code == 422
