"""Configuration for the Automatic File Organizer.

Maps file extensions to category folder names and defines
global constants used across the application.
"""

# Extension (lowercase, including the dot) -> category name
EXTENSION_MAP = {
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    # Documents
    ".pdf": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".xlsx": "Documents",
    ".pptx": "Documents",
    # Videos
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
}

# Category used for unknown extensions and files with no extension.
DEFAULT_CATEGORY = "Others"

# Categories in display order (Others always last).
CATEGORY_ORDER = ["Images", "Documents", "Videos", "Audio", "Archives", DEFAULT_CATEGORY]

# Folders that are never treated as files to move.
SKIP_DIR_NAMES = {"logs", "screenshots", "tests", "__pycache__"}
