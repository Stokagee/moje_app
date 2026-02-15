"""Endpoint pro forwarding frontend logů do Loki."""
from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()
LOKI_URL = os.getenv("LOKI_URL", "http://loki:3100/loki/api/v1/push")


@router.post("/logs/frontend")
async def forward_frontend_logs(logs: dict):
    """
    Předá frontend logy do Loki.

    Tím se obejde CORS problém - backend posílá do Loki jako server-to-server.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LOKI_URL,
                json=logs,
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )
            response.raise_for_status()
        return {"status": "ok", "logs_sent": len(logs.get("streams", []))}
    except httpx.HTTPError as e:
        # Log error ale nerozbíjej aplikaci
        import logging
        logging.getLogger(__name__).warning(f"Failed to forward logs to Loki: {e}")
        raise HTTPException(status_code=503, detail=f"Loki unavailable: {e}")
