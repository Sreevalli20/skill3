"""Reusable helper functions for the Automatic File Organizer."""

import logging
from pathlib import Path


def categorize(path: Path, extension_map: dict, default_category: str) -> str:
    """Return the category name for a file based on its extension.

    The extension is normalized with Path.suffix.lower(), so
    'photo.JPG' -> '.jpg' and 'archive.backup.zip' -> '.zip'.
    """
    suffix = path.suffix.lower()
    return extension_map.get(suffix, default_category)


def is_hidden(path: Path) -> bool:
    """Return True if the file or any of its parents is hidden."""
    return any(part.startswith(".") for part in path.parts)


def unique_destination(directory: Path, filename: str) -> Path:
    """Return a destination path inside *directory* that does not exist.

    If 'report.pdf' is taken, tries 'report_1.pdf', 'report_2.pdf', ...
    Never overwrites an existing file.
    """
    candidate = directory / filename
    if not candidate.exists():
        return candidate

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = directory / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def safe_makedirs(directory: Path, dry_run: bool = False, logger: logging.Logger = None) -> bool:
    """Create *directory* (and parents) if needed.

    Returns True if the directory exists (or was created), False on failure.
    In dry-run mode nothing is created; returns True so the caller can
    still compute what *would* happen.
    """
    if directory.exists():
        return True
    if dry_run:
        if logger:
            logger.info("[DRY-RUN] Would create directory: %s", directory)
        return True
    try:
        directory.mkdir(parents=True, exist_ok=True)
        if logger:
            logger.info("Created directory: %s", directory)
        return True
    except OSError as exc:
        if logger:
            logger.error("Failed to create directory %s: %s", directory, exc)
        return False
