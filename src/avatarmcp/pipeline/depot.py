"""Local avatar depot catalog - VRM and .vroid project index."""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

KIND_VRM = "vrm"
KIND_VROID = "vroid"
SOURCE_HUB = "hub"
SOURCE_VROID_EXPORT = "vroid_export"
SOURCE_VROID_PROJECT = "vroid_project"
SOURCE_MANUAL = "manual"
SOURCE_STAGING = "staging"


class AvatarDepot:
    """JSON-backed catalog over pipeline work dirs."""

    def __init__(self, work_dir: Path) -> None:
        self.work_dir = work_dir
        self.depot_dir = work_dir / "depot"
        self.vrm_dir = self.depot_dir / "vrm"
        self.vroid_dir = self.depot_dir / "projects"
        self.catalog_path = self.depot_dir / "catalog.json"
        for folder in (self.depot_dir, self.vrm_dir, self.vroid_dir):
            folder.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.catalog_path.is_file():
            return {"version": 1, "entries": {}}
        try:
            data = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Depot catalog read failed: %s", exc)
            return {"version": 1, "entries": {}}
        if "entries" not in data:
            data["entries"] = {}
        return data

    def _save(self, data: dict[str, Any]) -> None:
        self.catalog_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def register(
        self,
        path: str | Path,
        *,
        kind: str,
        source: str = SOURCE_MANUAL,
        name: str = "",
        character_model_id: str = "",
        model_type: str = "",
        copy_into_depot: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        src = Path(path)
        if not src.is_file():
            return {"success": False, "error": f"File not found: {path}"}

        ext = src.suffix.lower()
        if kind == KIND_VRM and ext != ".vrm":
            return {"success": False, "error": f"Expected .vrm, got {ext}"}
        if kind == KIND_VROID and ext != ".vroid":
            return {"success": False, "error": f"Expected .vroid, got {ext}"}

        dest = src
        if copy_into_depot:
            target_dir = self.vrm_dir if kind == KIND_VRM else self.vroid_dir
            dest = target_dir / src.name
            if src.resolve() != dest.resolve():
                dest.write_bytes(src.read_bytes())

        entry_id = uuid.uuid4().hex[:12]
        entry = {
            "id": entry_id,
            "kind": kind,
            "source": source,
            "name": name or src.stem,
            "path": str(dest.resolve()),
            "character_model_id": character_model_id,
            "model_type": model_type,
            "editable_in_studio": kind == KIND_VROID,
            "registered_at": time.time(),
            "size_kb": round(dest.stat().st_size / 1024, 1),
            "metadata": metadata or {},
        }

        data = self._load()
        data["entries"][entry_id] = entry
        self._save(data)
        return {"success": True, "entry": entry}

    def get(self, entry_id: str) -> dict[str, Any]:
        data = self._load()
        entry = data["entries"].get(entry_id)
        if not entry:
            return {"success": False, "error": f"Depot entry not found: {entry_id}"}
        return {"success": True, "entry": entry}

    def list_entries(
        self,
        *,
        kind: str = "",
        source: str = "",
        limit: int = 100,
    ) -> dict[str, Any]:
        data = self._load()
        items = list(data["entries"].values())
        items.sort(key=lambda e: float(e.get("registered_at", 0)), reverse=True)
        if kind:
            items = [e for e in items if e.get("kind") == kind]
        if source:
            items = [e for e in items if e.get("source") == source]
        return {
            "success": True,
            "count": len(items[:limit]),
            "depot_dir": str(self.depot_dir),
            "entries": items[:limit],
        }

    def scan_work_dirs(self, staging_dir: Path, hub_dir: Path, output_dir: Path) -> dict[str, Any]:
        """Register unknown VRM/VROID files found in pipeline folders."""
        added: list[str] = []
        data = self._load()
        known_paths = {e.get("path") for e in data["entries"].values()}

        def _scan(folder: Path, kind: str, source: str, pattern: str) -> None:
            if not folder.is_dir():
                return
            for path in folder.glob(pattern):
                resolved = str(path.resolve())
                if resolved in known_paths:
                    continue
                reg = self.register(
                    path,
                    kind=kind,
                    source=source,
                    copy_into_depot=False,
                )
                if reg.get("success"):
                    added.append(reg["entry"]["id"])
                    known_paths.add(resolved)

        _scan(staging_dir, KIND_VRM, SOURCE_STAGING, "*.vrm")
        _scan(hub_dir, KIND_VRM, SOURCE_HUB, "*.vrm")
        _scan(output_dir, KIND_VRM, SOURCE_VROID_EXPORT, "*.vrm")
        _scan(self.vroid_dir, KIND_VROID, SOURCE_VROID_PROJECT, "*.vroid")

        return {"success": True, "new_entries": added, "added_count": len(added)}
