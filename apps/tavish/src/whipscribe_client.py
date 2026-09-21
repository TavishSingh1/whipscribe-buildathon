import os
import httpx
import asyncio
from typing import Optional, Dict, Any, List

class WhipScribeClient:
    BASE_URL = "https://whipscribe.com/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-API-Key": self.api_key}

    async def upload_file(self, file_path: str) -> str:
        """Upload an audio file and return the job_id."""
        url = f"{self.BASE_URL}/transcribe"
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {"source": "api"}
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(url, headers=self.headers, files=files, data=data)
                response.raise_for_status()
                return response.json()["job_id"]

    async def poll_job(self, job_id: str) -> Dict[str, Any]:
        """Poll job status until done or failed."""
        url = f"{self.BASE_URL}/jobs/{job_id}"
        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                status = data.get("status")
                if status in ("done", "failed"):
                    return data
                await asyncio.sleep(3)

    async def get_transcript(self, job_id: str) -> Dict[str, Any]:
        """Get the full transcript JSON."""
        url = f"{self.BASE_URL}/jobs/{job_id}/result?format=json"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def create_clip(self, job_id: str, start_s: float, end_s: float, title: str, caption_style: str = "bold-yellow") -> str:
        """Render a 9:16 vertical MP4 and return the clip_id."""
        url = f"{self.BASE_URL}/jobs/{job_id}/clips"
        payload = {
            "start_s": start_s,
            "end_s": end_s,
            "title": title,
            "caption_style": caption_style
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()["clip_id"]

    async def poll_clip(self, clip_id: str) -> Dict[str, Any]:
        """Poll clip rendering status until done or failed."""
        url = f"{self.BASE_URL}/clips/{clip_id}"
        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json().get("clip", {})
                if data.get("status") in ("done", "failed"):
                    return data
                await asyncio.sleep(3)
