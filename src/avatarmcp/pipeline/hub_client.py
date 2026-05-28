"""VRoid Hub OAuth and VRM download client."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import secrets
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)

HUB_BASE_URL = os.environ.get("VROID_HUB_BASE_URL", "https://hub.vroid.com").rstrip("/")
HUB_API_VERSION = os.environ.get("VROID_HUB_API_VERSION", "11")
DEFAULT_REDIRECT_URI = os.environ.get("VROID_HUB_REDIRECT_URI", "http://127.0.0.1:10793/api/v1/pipeline/hub/callback")


def _pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Failed to read hub token file: %s", exc)
        return {}


def _save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class VRoidHubClient:
    """Minimal VRoid Hub API client (OAuth PKCE + download licenses)."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.token_path = storage_dir / "token.json"
        self.pending_path = storage_dir / "oauth_pending.json"
        self.client_id = os.environ.get("VROID_HUB_CLIENT_ID", "").strip()
        self.client_secret = os.environ.get("VROID_HUB_CLIENT_SECRET", "").strip()
        self.redirect_uri = DEFAULT_REDIRECT_URI

    def _headers(self, access_token: str | None = None) -> dict[str, str]:
        headers = {"X-Api-Version": HUB_API_VERSION, "Accept": "application/json"}
        token = access_token or self.get_access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def get_access_token(self) -> str | None:
        env_token = os.environ.get("VROID_HUB_ACCESS_TOKEN", "").strip()
        if env_token:
            return env_token
        data = _load_json(self.token_path)
        token = str(data.get("access_token", "")).strip()
        if not token:
            return None
        expires_at = float(data.get("expires_at", 0) or 0)
        if expires_at and time.time() >= expires_at - 30:
            logger.info("VRoid Hub token expired; re-auth required")
            return None
        return token

    def auth_status(self) -> dict[str, Any]:
        token = self.get_access_token()
        pending = _load_json(self.pending_path)
        return {
            "authenticated": bool(token),
            "client_id_configured": bool(self.client_id),
            "client_secret_configured": bool(self.client_secret),
            "redirect_uri": self.redirect_uri,
            "pending_oauth": bool(pending.get("state")),
            "token_path": str(self.token_path),
            "docs": "https://developer.vroid.com/en/api/",
        }

    def auth_start(self) -> dict[str, Any]:
        if not self.client_id:
            return {
                "success": False,
                "error": "VROID_HUB_CLIENT_ID not set. Register app at https://hub.vroid.com/oauth/applications",
            }
        verifier, challenge = _pkce_pair()
        state = secrets.token_urlsafe(24)
        pending = {
            "state": state,
            "code_verifier": verifier,
            "created_at": time.time(),
        }
        _save_json(self.pending_path, pending)
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "default",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        url = f"{HUB_BASE_URL}/oauth/authorize?{urlencode(params)}"
        return {
            "success": True,
            "authorize_url": url,
            "state": state,
            "redirect_uri": self.redirect_uri,
            "message": "Open authorize_url in browser, then call hub_auth with auth_step=complete and auth_code",
        }

    async def auth_complete(self, auth_code: str, state: str = "") -> dict[str, Any]:
        if not self.client_id or not self.client_secret:
            return {"success": False, "error": "VROID_HUB_CLIENT_ID and VROID_HUB_CLIENT_SECRET required"}
        pending = _load_json(self.pending_path)
        if state and pending.get("state") and pending.get("state") != state:
            return {"success": False, "error": "OAuth state mismatch"}
        verifier = str(pending.get("code_verifier", "")).strip()
        if not verifier:
            return {"success": False, "error": "No pending OAuth session; call auth_step=start first"}

        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code_verifier": verifier,
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{HUB_BASE_URL}/oauth/token",
                    data=payload,
                    headers={"X-Api-Version": HUB_API_VERSION},
                )
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            logger.warning("Hub token exchange failed: %s", exc)
            return {"success": False, "error": str(exc)}

        access = body.get("access_token")
        if not access:
            return {"success": False, "error": "No access_token in Hub response", "raw": body}

        expires_in = float(body.get("expires_in", 3600) or 3600)
        token_doc = {
            "access_token": access,
            "refresh_token": body.get("refresh_token"),
            "expires_at": time.time() + expires_in,
            "token_type": body.get("token_type", "Bearer"),
        }
        _save_json(self.token_path, token_doc)
        if self.pending_path.is_file():
            try:
                self.pending_path.unlink()
            except OSError:
                pass
        return {"success": True, "message": "VRoid Hub OAuth complete", "expires_in": expires_in}

    def auth_set_token(self, access_token: str) -> dict[str, Any]:
        token = access_token.strip()
        if not token:
            return {"success": False, "error": "access_token required"}
        _save_json(
            self.token_path,
            {"access_token": token, "expires_at": time.time() + 86400 * 30, "token_type": "Bearer"},
        )
        return {"success": True, "message": "Access token stored"}

    async def download_character(self, character_model_id: str, dest_dir: Path) -> dict[str, Any]:
        token = self.get_access_token()
        if not token:
            return {
                "success": False,
                "error": "Not authenticated. Run hub_auth auth_step=start then complete, or set VROID_HUB_ACCESS_TOKEN",
            }
        if not character_model_id.strip():
            return {"success": False, "error": "character_model_id required"}

        dest_dir.mkdir(parents=True, exist_ok=True)
        headers = self._headers(token)

        try:
            async with httpx.AsyncClient(timeout=120.0, follow_redirects=False) as client:
                license_resp = await client.post(
                    f"{HUB_BASE_URL}/api/download_licenses",
                    json={"character_model_id": character_model_id.strip()},
                    headers={**headers, "Content-Type": "application/json"},
                )
                license_resp.raise_for_status()
                license_body = license_resp.json()
                license_data = license_body.get("data") or {}
                license_id = license_data.get("id")
                if not license_id:
                    return {
                        "success": False,
                        "error": "No download license id returned",
                        "hub_response": license_body,
                    }

                download_resp = await client.get(
                    f"{HUB_BASE_URL}/api/download_licenses/{license_id}/download",
                    headers=headers,
                )
                if download_resp.status_code not in (302, 307, 308):
                    return {
                        "success": False,
                        "error": f"Expected redirect from Hub download, got {download_resp.status_code}",
                        "body": download_resp.text[:500],
                    }
                presigned = download_resp.headers.get("location")
                if not presigned:
                    return {"success": False, "error": "Missing presigned download URL"}

                file_resp = await client.get(presigned, follow_redirects=True)
                file_resp.raise_for_status()
                filename = f"{character_model_id}.vrm"
                dest = dest_dir / filename
                dest.write_bytes(file_resp.content)
        except httpx.HTTPError as exc:
            logger.warning("Hub download failed model=%s error=%s", character_model_id, exc)
            return {"success": False, "error": str(exc), "character_model_id": character_model_id}

        return {
            "success": True,
            "character_model_id": character_model_id,
            "download_path": str(dest),
            "size_kb": round(dest.stat().st_size / 1024, 1),
            "license_id": license_id,
        }
