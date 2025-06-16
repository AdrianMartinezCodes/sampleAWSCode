from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import aiohttp
import asyncio
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "MetadataFetcher/1.0"}


def build_response(status: str, code: int, data=None, message=None):
    return {"status": status, "code": code, "data": data, "message": message}


async def fetch_metadata_path(base_url: str, path: str) -> str:
    url = f"{base_url.rstrip('/')}/{path.strip('/')}"
    try:
        logger.info(f"Fetching metadata path: {url}")
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url, timeout=1) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Metadata fetch failed: {response.status}",
                    )
                return await response.text()
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching: {url}")
        raise HTTPException(status_code=504, detail="Metadata request timed out")
    except aiohttp.ClientError as e:
        logger.error(f"Client error fetching {url}: {e}")
        raise HTTPException(status_code=502, detail="Client error fetching metadata")


@app.get("/metadata")
async def get_metadata(
    meta_data_url: str = Query(..., description="Base metadata URL to query"),
    key: Optional[str] = Query(None, description="Optional metadata key to fetch"),
):
    """
    Fetch full or partial metadata from a specified URL.
    - If `key` is not provided, returns the list of available top-level keys.
    - If `key` is provided, returns the value for that specific metadata path.
    """
    if key:
        result = await fetch_metadata_path(meta_data_url, key)
        return build_response("success", 200, data={"key": key, "value": result})
    # Otherwise: fetch base metadata index
    try:
        logger.info(f"Fetching metadata root from: {meta_data_url}/")
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(
                meta_data_url.rstrip("/") + "/", timeout=1
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=502, detail="Failed to fetch metadata"
                    )
                text = await response.text()
                keys = text.strip().splitlines()
                return build_response("success", 200, data={"available_keys": keys})
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching metadata root from: {meta_data_url}")
        return build_response(
            "error", 504, data=None, message="Metadata root request timed out"
        )
    except aiohttp.ClientError as e:
        logger.error(f"Client error fetching metadata root: {e}")
        return build_response(
            "error", 502, data=None, message="Failed to fetch metadata root"
        )
