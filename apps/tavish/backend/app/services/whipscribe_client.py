from pathlib import Path
from typing import Any

import httpx


class WhipScribeClient:
    BASE_URL = "https://whipscribe.com/api/v1"

    def __init__(self, api_key: str):
        self.headers = {"X-API-Key": api_key}

    async def upload_file(self, file_path: str) -> str:
        path = Path(file_path)
        async with httpx.AsyncClient(timeout=300) as client:
            with path.open("rb") as handle:
                response = await client.post(
                    f"{self.BASE_URL}/transcribe",
                    headers=self.headers,
                    files={"file": (path.name, handle)},
                    data={"source": "api"},
                )
        response.raise_for_status()
        return response.json()["job_id"]

    async def poll_job(self, job_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                response = await client.get(f"{self.BASE_URL}/jobs/{job_id}", headers=self.headers)
                response.raise_for_status()
                data = response.json()
                if data.get("status") in ("done", "failed"):
                    return data
                import asyncio

                await asyncio.sleep(3)

    async def get_transcript(self, job_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self.BASE_URL}/jobs/{job_id}/result?format=json", headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def create_clip(self, job_id: str, start_s: float, end_s: float, title: str) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.BASE_URL}/jobs/{job_id}/clips",
                headers=self.headers,
                json={"start_s": start_s, "end_s": end_s, "title": title, "caption_style": "bold-yellow"},
            )
        response.raise_for_status()
        return response.json()["clip_id"]

    async def poll_clip(self, clip_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                response = await client.get(f"{self.BASE_URL}/clips/{clip_id}", headers=self.headers)
                response.raise_for_status()
                clip = response.json().get("clip", {})
                if clip.get("status") in ("done", "failed"):
                    return clip
                import asyncio

                await asyncio.sleep(3)
