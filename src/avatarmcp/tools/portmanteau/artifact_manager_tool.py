"""
Artifact Manager Portmanteau Tool for AvatarMCP

Monitors external asset landfalls (Downloads) and routes them to project pipelines.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ArtifactManagerTool:
    """Portmanteau tool for monitoring and depositing external assets."""

    def __init__(self, mcp_server):
        """Initialize artifact manager tool."""
        self.mcp_server = mcp_server
        self.downloads_path = Path(os.path.expanduser("~/Downloads"))
        self.pipelines = {
            "unity": Path("D:/Dev/repos/unity3d-mcp/assets"),
            "resonite": Path("D:/Dev/repos/resonite-mcp/assets"),
            "vrchat": Path("D:/Dev/repos/vrchat-mcp/assets"),
            "openfang": Path("D:/Dev/repos/openfang/exchange"),
            "central_docs": Path("D:/Dev/repos/mcp-central-docs/assets/landfalls"),
        }
        self._register_tool()

    def _register_tool(self):
        """Register the artifact manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def artifact_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Unified tool for artifact pipeline management.

            Parameters:
                operation: The specific operation to perform (required)
                    - "monitor_scan": Scan Downloads for new artifacts
                    - "deposit": Move a specific artifact to its destination
                    - "get_status": Get pipeline status

                Additional parameters:
                    file_path: Relative or absolute path to the file (for "deposit")
                    target: Override target pipeline (optional)
            """
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "monitor_scan":
                    return self._handle_scan(params)
                elif operation == "deposit":
                    return self._handle_deposit(params)
                elif operation == "get_status":
                    return self._get_status()
                else:
                    return {"status": "error", "message": f"Unknown operation '{operation}'"}
            except Exception as e:
                logger.error(f"Artifact manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _classify_file(self, filename: str) -> str:
        """Classify file target based on the Grand Unified Artifact Ontology."""
        fname = filename.lower()

        # Tier 1: Perception (Geometric/Sensory)
        if fname.endswith((".ply", ".splat")) or "worldlabs" in fname:
            return "unity"
        if fname.endswith((".fbx", ".obj", ".unitypackage")):
            return "unity"
        if fname.endswith(".vrm"):
            return "vrchat"
        if fname.endswith(".resonite") or fname.endswith(".brson"):
            return "resonite"

        # Tier 0/4: Substrate / Narrative
        if fname.endswith((".md", ".txt", ".pdf")) or "metadata" in fname:
            return "central_docs"

        # Tier 2: Agency
        if any(x in fname for x in ["vbot", "sentient", "agent", "loop"]):
            return "openfang"

        # Tier 3/5: Essence / Hyper-Reality
        if any(x in fname for x in ["soul", "personality", "kai", "demon", "angel"]):
            return "avatar"

        # Tier 6: Cognitive
        if any(x in fname for x in ["plan", "fantasy", "dream"]):
            return "central_docs"

        return "unknown"

    def _classify_file_with_tier(self, filename: str) -> dict[str, str]:
        """Classify file target and return both target and tier."""
        target = self._classify_file(filename)
        fname = filename.lower()

        tier = "T0: Substrate"

        # Perception
        if any(
            x in fname
            for x in [
                ".ply",
                ".splat",
                ".fbx",
                ".obj",
                ".unitypackage",
                ".vrm",
                ".resonite",
                ".brson",
            ]
        ):
            tier = "T1: Perception"
        # Agency
        elif any(x in fname for x in ["vbot", "sentient", "agent", "loop"]):
            tier = "T2: Agency"
        # Essence
        elif any(x in fname for x in ["soul", "personality"]):
            tier = "T3: Essence"
        # Narrative
        elif any(x in fname for x in ["jhadi", "trope", "lore"]):
            tier = "T4: Narrative"
        # Hyper-Reality
        elif any(x in fname for x in ["kai", "youkai", "demon", "angel"]):
            tier = "T5: Hyper-Reality"
        # Cognitive
        elif any(x in fname for x in ["plan", "fantasy", "dream"]):
            tier = "T6: Cognitive"

        return {"target": target, "tier": tier}

    def _handle_scan(self, params: dict[str, Any]) -> dict[str, Any]:
        """Scan Downloads folder for potential artifacts."""
        if not self.downloads_path.exists():
            return {"status": "error", "message": f"Downloads path {self.downloads_path} not found"}

        artifacts = []
        # Support more extensions for the expanded ontology
        extensions = (
            ".ply",
            ".splat",
            ".vrm",
            ".fbx",
            ".obj",
            ".unitypackage",
            ".resonite",
            ".brson",
            ".sdf",
            ".config",
            ".md",
            ".txt",
            ".pdf",
        )

        for file in self.downloads_path.glob("*"):
            if file.is_file() and file.suffix.lower() in extensions:
                classification = self._classify_file_with_tier(file.name)
                artifacts.append(
                    {
                        "name": file.name,
                        "path": str(file.absolute()),
                        "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
                        "created": file.stat().st_ctime,
                        "suggested_target": classification["target"],
                        "tier": classification["tier"],
                    }
                )

        # Sort by creation time (newest first)
        artifacts.sort(key=lambda x: x["created"], reverse=True)

        return {"status": "success", "count": len(artifacts), "artifacts": artifacts}

    def _handle_deposit(self, params: dict[str, Any]) -> dict[str, Any]:
        """Move an artifact to its destination pipeline."""
        file_path_str = params.get("file_path")
        if not file_path_str:
            return {"status": "error", "message": "file_path is required for deposit"}

        source_file = Path(file_path_str)
        if not source_file.is_absolute():
            source_file = self.downloads_path / source_file

        if not source_file.exists():
            return {"status": "error", "message": f"Source file {source_file} not found"}

        target_key = params.get("target") or self._classify_file(source_file.name)
        if target_key not in self.pipelines:
            return {"status": "error", "message": f"Invalid target pipeline '{target_key}'"}

        target_root = self.pipelines[target_key]

        # Determine specific subdirectory
        sub_dir = "imports"
        if "worldlabs" in source_file.name.lower() or source_file.suffix.lower() in (
            ".ply",
            ".splat",
        ):
            sub_dir = "worldlabs"
        elif source_file.suffix.lower() == ".vrm":
            sub_dir = "vrm"

        destination_dir = target_root / sub_dir
        destination_dir.mkdir(parents=True, exist_ok=True)

        destination_file = destination_dir / source_file.name

        try:
            shutil.move(str(source_file), str(destination_file))
            logger.info(f"Deposited {source_file.name} to {destination_file}")
            return {
                "status": "success",
                "message": f"Successfully deposited {source_file.name} to {target_key}/{sub_dir}",
                "destination": str(destination_file),
            }
        except Exception as e:
            return {"status": "error", "message": f"Move failed: {e!s}"}

    def _get_status(self) -> dict[str, Any]:
        """Return pipeline health and status."""
        return {
            "status": "success",
            "monitoring_path": str(self.downloads_path),
            "pipelines": {k: str(v) for k, v in self.pipelines.items()},
            "health": "active",
            "last_scan": "just now",
        }
