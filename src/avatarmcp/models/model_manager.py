"""
VRM Model Manager

Provides advanced model management capabilities including caching, validation,
and lifecycle management for VRM models.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from ..models.vrm_loader import VRMLoader, VRMModel

logger = logging.getLogger(__name__)


@dataclass
class ModelCacheEntry:
    """Represents an entry in the model cache."""

    model: VRMModel
    last_accessed: float
    access_count: int = 0
    file_hash: str | None = None
    file_size: int = 0
    load_time: float = 0.0
    metadata: dict = field(default_factory=dict)


class VRMModelManager:
    """
    Manages loading, caching, and lifecycle of VRM models.

    Features:
    - LRU caching of loaded models
    - Model validation
    - Memory management
    - File change detection
    - Statistics and metrics
    """

    def __init__(self, max_cache_size: int = 10, cache_dir: Path | None = None):
        """
        Initialize the VRM model manager.

        Args:
            max_cache_size: Maximum number of models to keep in memory
            cache_dir: Directory for persistent cache (optional)
        """
        self.max_cache_size = max(max_cache_size, 1)
        self.cache: dict[str, ModelCacheEntry] = {}
        self.cache_dir = cache_dir
        self._setup_cache_directory()
        self._load_cache_metadata()

        # Statistics
        self.stats = {
            "total_loaded": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_load_time": 0.0,
            "total_unloads": 0,
            "validation_errors": 0,
        }

    def _setup_cache_directory(self) -> None:
        """Set up the cache directory if it doesn't exist."""
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _load_cache_metadata(self) -> None:
        """Load cache metadata from disk if available."""
        if not self.cache_dir:
            return

        metadata_file = self.cache_dir / "cache_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    cache_metadata = json.load(f)
                    self.stats.update(cache_metadata.get("stats", {}))
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")

    def _save_cache_metadata(self) -> None:
        """Save cache metadata to disk."""
        if not self.cache_dir:
            return

        metadata_file = self.cache_dir / "cache_metadata.json"
        try:
            with open(metadata_file, "w") as f:
                json.dump({"stats": self.stats}, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache metadata: {e}")

    def _make_cache_key(self, file_path: str | Path) -> str:
        """Generate a cache key for the given file path."""
        return str(Path(file_path).absolute())

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute the SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _is_file_modified(self, file_path: Path, cached_hash: str) -> bool:
        """Check if a file has been modified since it was cached."""
        if not file_path.exists():
            return True
        return self._compute_file_hash(file_path) != cached_hash

    def _make_room_in_cache(self) -> None:
        """Make room in the cache by removing the least recently used items."""
        if len(self.cache) < self.max_cache_size:
            return

        # Sort by last accessed time (oldest first)
        lru = sorted(self.cache.items(), key=lambda x: x[1].last_accessed)

        # Remove the oldest items until we're under the limit
        for key, _ in lru[: len(self.cache) - self.max_cache_size + 1]:
            self._unload_model(key)

    def _unload_model(self, cache_key: str) -> None:
        """Unload a model from the cache."""
        if cache_key in self.cache:
            # Clean up any resources if needed
            # (e.g., GPU resources for the model)

            # Remove from cache
            del self.cache[cache_key]
            self.stats["total_unloads"] += 1

    def validate_vrm_file(self, file_path: str | Path) -> tuple[bool, list[str]]:
        """
        Validate a VRM file.

        Args:
            file_path: Path to the VRM file

        Returns:
            Tuple of (is_valid, issues) where issues is a list of validation messages
        """
        path = Path(file_path)
        issues = []

        # Check file exists
        if not path.exists():
            issues.append(f"File not found: {file_path}")
            return False, issues

        # Check file extension
        if path.suffix.lower() not in (".vrm", ".glb"):
            issues.append(f"Unsupported file extension: {path.suffix}")

        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        file_size = path.stat().st_size
        if file_size > max_size:
            issues.append(
                f"File too large: {file_size / 1024 / 1024:.2f}MB (max {max_size / 1024 / 1024}MB)"
            )

        # TODO: Add more validation checks
        # - VRM version compatibility
        # - Required extensions
        # - Required nodes/bones

        return len(issues) == 0, issues

    def load_model(
        self, file_path: str | Path, force_reload: bool = False, validate: bool = True
    ) -> tuple[VRMModel | None, list[str]]:
        """
        Load a VRM model, using the cache if available.

        Args:
            file_path: Path to the VRM file
            force_reload: If True, force reload the model even if it's in the cache
            validate: If True, validate the VRM file before loading

        Returns:
            Tuple of (model, messages) where messages contains any warnings or errors
        """
        path = Path(file_path).absolute()
        cache_key = self._make_cache_key(path)
        messages = []

        # Check if file exists
        if not path.exists():
            return None, [f"File not found: {path}"]

        # Validate the VRM file if requested
        if validate:
            is_valid, validation_issues = self.validate_vrm_file(path)
            messages.extend(validation_issues)
            if not is_valid:
                self.stats["validation_errors"] += 1
                return None, messages

        # Check if the model is already in the cache
        current_time = time.time()
        if not force_reload and cache_key in self.cache:
            cache_entry = self.cache[cache_key]

            # Check if the file has been modified
            if cache_entry.file_hash and self._is_file_modified(path, cache_entry.file_hash):
                logger.info(f"File modified, reloading: {path}")
            else:
                # Update access time and return cached model
                cache_entry.last_accessed = current_time
                cache_entry.access_count += 1
                self.cache.move_to_end(cache_key)  # Update LRU order
                self.stats["cache_hits"] += 1
                return cache_entry.model, messages
        else:
            self.stats["cache_misses"] += 1

        # Make room in the cache if needed
        self._make_room_in_cache()

        # Load the model
        load_start = time.time()
        try:
            model = VRMLoader.from_file(path)
            load_time = time.time() - load_start

            # Update statistics
            self.stats["total_loaded"] += 1
            self.stats["total_load_time"] += load_time

            # Create cache entry
            file_hash = self._compute_file_hash(path)
            cache_entry = ModelCacheEntry(
                model=model,
                last_accessed=current_time,
                access_count=1,
                file_hash=file_hash,
                file_size=path.stat().st_size,
                load_time=load_time,
                metadata={
                    "path": str(path),
                    "load_timestamp": current_time,
                    "version": "1.0",  # For cache invalidation
                },
            )

            # Add to cache
            self.cache[cache_key] = cache_entry

            return model, messages

        except Exception as e:
            logger.error(f"Failed to load VRM model: {e}", exc_info=True)
            messages.append(f"Failed to load VRM model: {str(e)}")
            return None, messages

    def unload_model(self, file_path: str | Path) -> bool:
        """
        Unload a model from the cache.

        Args:
            file_path: Path to the VRM file or cache key

        Returns:
            True if the model was unloaded, False otherwise
        """
        cache_key = self._make_cache_key(file_path)
        if cache_key in self.cache:
            self._unload_model(cache_key)
            return True
        return False

    def clear_cache(self) -> None:
        """Clear the entire model cache."""
        for cache_key in list(self.cache.keys()):
            self._unload_model(cache_key)

    def get_cache_info(self) -> dict:
        """
        Get information about the cache state.

        Returns:
            Dictionary containing cache statistics and state
        """
        total_size = sum(entry.file_size for entry in self.cache.values())
        avg_load_time = (
            self.stats["total_load_time"] / self.stats["total_loaded"]
            if self.stats["total_loaded"] > 0
            else 0
        )

        return {
            "cache_size": len(self.cache),
            "max_cache_size": self.max_cache_size,
            "total_cached_size": total_size,
            "total_loaded": self.stats["total_loaded"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_ratio": (
                self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"])
                if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
                else 0
            ),
            "avg_load_time": avg_load_time,
            "total_unloads": self.stats["total_unloads"],
            "validation_errors": self.stats["validation_errors"],
        }

    def __del__(self):
        """Clean up resources when the manager is destroyed."""
        self._save_cache_metadata()
        self.clear_cache()


# Global instance for convenience
model_manager = VRMModelManager()
