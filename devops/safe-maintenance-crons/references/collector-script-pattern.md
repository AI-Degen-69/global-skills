# Collector Script Pattern

**Purpose:** Deterministic scanner that emits structured JSON for the LLM layer.

## Requirements

- Single Python script, no external deps beyond stdlib
- Outputs JSON to stdout (one object)
- Categories with typed items (file vs directory)
- Includes: path, size (bytes + MB), mtime, age_days
- Excludes denylisted paths (backup mirrors, state DBs, configs, venv)
- Scans profile subdirectories if applicable
- Summary totals at top level

## Example Structure

```json
{
  "scan_time": "2026-06-06T13:48:57.837036",
  "hermes_root": "C:/Users/Tiger/AppData/Local/hermes",
  "categories": {
    "pycache": [{"path": "...", "type": "directory", "size_bytes": 1376644, "size_mb": 1.31, "file_count": 10}],
    "pre_update_backups": [{"path": "...", "size_bytes": 139107356, "size_mb": 132.66, "mtime": "...", "age_days": 0}],
    "bootstrap_cache": [...],
    "config_backups": [...],
    "cache_terminal": [...],
    "cache_screenshots": [...],
    "logs": [...],
    "plans": [...]
  },
  "summary": {"total_candidates": 650, "total_size_mb": 71.77},
  "profiles": {
    "engineer": {
      "logs": [...],
      "cache_terminal": [...],
      "config_baks": [...],
      "pycache": [...],
      "audio_cache": [...],
      "image_cache": [...]
    }
  }
}
```

## Denylist Pattern

```python
DENYLIST_DIRS = {
    HERMES_ROOT / "hermes-backup",
    HERMES_ROOT / ".git",
    HERMES_ROOT / "profiles",
    HERMES_ROOT / "state-snapshots",
    HERMES_ROOT / "sessions",
    HERMES_ROOT / "handoffs",
    HERMES_ROOT / "shared",
}
DENYLIST_EXACT = {
    HERMES_ROOT / "config.yaml",
    HERMES_ROOT / ".env",
    HERMES_ROOT / "auth.json",
    HERMES_ROOT / "channel_directory.json",
    HERMES_ROOT / "SOUL.md",
    HERMES_ROOT / "state.db",
    HERMES_ROOT / "state.db-shm",
    HERMES_ROOT / "state.db-wal",
}
```

## Applied Example

> ⚠️ `hermes-cleanup-collector.py` was retired and moved to `hermes/scripts/.trash/` (2026-07-26). It was NOT actually referenced by `hermes-cleanup-daily.py` (doc was stale). Historical reference only.