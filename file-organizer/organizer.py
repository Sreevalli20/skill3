"""Automatic File Organizer - Intermediate Python CLI Automation Script.

Sorts the files inside a target folder into category subfolders
(Images, Documents, Videos, Audio, Archives, Others) based on file
extensions, with safe duplicate handling and an optional undo feature.

Usage:
    python organizer.py "sample_folder"
    python organizer.py "sample_folder" --dry-run
    python organizer.py "sample_folder" --undo
    python organizer.py --help
"""

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

from config import EXTENSION_MAP, DEFAULT_CATEGORY, CATEGORY_ORDER
from utils import categorize, is_hidden, unique_destination, safe_makedirs

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "organizer.log"
MANIFEST_FILE = LOG_DIR / "move_manifest.json"

logger = logging.getLogger("file_organizer")


def setup_logging() -> None:
    """Configure logging to logs/organizer.log.

    Falls back to console-only logging if the log directory cannot be
    created, so logging never crashes the application.
    """
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as exc:
        print(f"Warning: could not open log file {LOG_FILE}: {exc}", file=sys.stderr)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def load_manifest() -> list:
    """Load the list of recorded file moves (used by --undo)."""
    if not MANIFEST_FILE.exists():
        return []
    try:
        return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Could not read move manifest %s: %s", MANIFEST_FILE, exc)
        return []


def save_manifest(moves: list) -> None:
    """Persist the list of recorded file moves for --undo."""
    if not moves:
        return
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        MANIFEST_FILE.write_text(json.dumps(moves, indent=2), encoding="utf-8")
    except OSError as exc:
        logger.error("Could not write move manifest %s: %s", MANIFEST_FILE, exc)


def undo_moves() -> int:
    """Move previously organized files back to their original locations.

    Never overwrites an existing file: if the original path is occupied,
    the file is skipped and reported.
    """
    moves = load_manifest()
    if not moves:
        print("No recorded moves to undo.")
        return 0

    restored = 0
    skipped = 0
    failed = 0
    remaining = []

    for entry in moves:
        src = Path(entry["destination"])
        dst = Path(entry["source"])
        try:
            if not src.exists():
                logger.warning("Undo: destination missing, skipping %s", src)
                skipped += 1
                remaining.append(entry)
                continue
            if dst.exists():
                logger.warning("Undo: original path occupied, skipping %s", dst)
                skipped += 1
                remaining.append(entry)
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            logger.info("Undo: restored %s -> %s", src, dst)
            restored += 1
        except OSError as exc:
            logger.error("Undo: failed to restore %s: %s", src, exc)
            failed += 1
            remaining.append(entry)

    save_manifest(remaining)
    print(f"\nUndo complete: {restored} restored, {skipped} skipped, {failed} failed.")
    return 0 if failed == 0 else 1


def organize(folder: Path, dry_run: bool = False) -> int:
    """Scan *folder* and move each file into its category subfolder."""
    if not folder.exists():
        print(f"Error: target folder does not exist: {folder}")
        logger.error("Target folder does not exist: %s", folder)
        return 1
    if not folder.is_dir():
        print(f"Error: target path is not a folder: {folder}")
        logger.error("Target path is not a folder: %s", folder)
        return 1

    self_path = Path(__file__).resolve()
    category_dirs = {name: folder / name for name in CATEGORY_ORDER}

    total = 0
    moved_per_category = {name: 0 for name in CATEGORY_ORDER}
    skipped = 0
    failed = 0
    moves = []

    try:
        entries = sorted(folder.iterdir(), key=lambda p: p.name.lower())
    except OSError as exc:
        print(f"Error: cannot read folder {folder}: {exc}")
        logger.error("Cannot read folder %s: %s", folder, exc)
        return 1

    for path in entries:
        # Skip directories, hidden files, and organizer.py itself.
        if not path.is_file():
            skipped += 1
            logger.info("Skipped (not a regular file): %s", path.name)
            continue
        if is_hidden(path):
            skipped += 1
            logger.info("Skipped (hidden file): %s", path.name)
            continue
        try:
            if path.resolve() == self_path:
                skipped += 1
                logger.info("Skipped (organizer script itself): %s", path.name)
                continue
        except OSError:
            pass

        # Skip files that already live inside a category folder
        # (avoids re-organizing on repeated runs).
        if path.parent.resolve() != folder.resolve():
            skipped += 1
            continue

        total += 1
        category = categorize(path, EXTENSION_MAP, DEFAULT_CATEGORY)
        dest_dir = category_dirs[category]
        dest = unique_destination(dest_dir, path.name)

        if dest.name != path.name:
            logger.info("Duplicate handling: %s -> %s", path.name, dest.name)

        if dry_run:
            print(f"[DRY-RUN] {path.name} -> {category}/{dest.name}")
            logger.info("[DRY-RUN] Would move %s -> %s", path, dest)
            moved_per_category[category] += 1
            continue

        if not safe_makedirs(dest_dir, dry_run=False, logger=logger):
            failed += 1
            continue

        try:
            shutil.move(str(path), str(dest))
            moves.append({"source": str(path), "destination": str(dest)})
            moved_per_category[category] += 1
            logger.info("Moved %s -> %s", path, dest)
        except OSError as exc:
            failed += 1
            logger.error("Failed to move %s: %s", path, exc)
            print(f"  Warning: could not move {path.name}: {exc}")

    if moves and not dry_run:
        existing = load_manifest()
        save_manifest(existing + moves)

    # Summary
    print("\n===== ORGANIZER SUMMARY =====")
    print(f"Target folder      : {folder}")
    print(f"Mode               : {'DRY-RUN (no changes made)' if dry_run else 'LIVE'}")
    print(f"Total files found  : {total}")
    for name in CATEGORY_ORDER:
        count = moved_per_category[name]
        if count or (name == DEFAULT_CATEGORY):
            print(f"  {name:<12}: {count}")
    print(f"Skipped            : {skipped}")
    print(f"Failed             : {failed}")
    print("==============================")

    logger.info(
        "Run finished: total=%d moved=%s skipped=%d failed=%d dry_run=%s",
        total, moved_per_category, skipped, failed, dry_run,
    )
    return 0 if failed == 0 else 1


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Automatically organize files in a folder by extension.",
    )
    parser.add_argument(
        "folder",
        nargs="?",
        help='Target folder to organize (e.g. "sample_folder").',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be moved without changing anything.",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Move files back to their original locations (last run).",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.undo:
        setup_logging()
        return undo_moves()

    if not args.folder:
        print("Error: please provide a target folder.")
        print('Usage: python organizer.py "sample_folder" [--dry-run]')
        return 2

    setup_logging()
    folder = Path(args.folder).expanduser().resolve()
    logger.info("=== Organizer run started (dry_run=%s) ===", args.dry_run)
    return organize(folder, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
