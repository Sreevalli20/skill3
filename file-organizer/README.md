# Automatic File Organizer

A beginner-friendly **Python 3.14.6** CLI tool that automatically organizes
a messy folder (like Downloads) by sorting files into category subfolders
based on their extensions — safely, with duplicate protection, dry-run
preview, and undo support.

## Features

- Sorts files into **Images, Documents, Videos, Audio, Archives, Others**
- **Never overwrites** existing files — duplicates get `_1`, `_2`, ... suffixes
- Skips **hidden files**, **subdirectories**, and the script itself
- **Dry-run mode** to preview moves without changing anything
- **Undo mode** to restore files from the last run
- Handles missing folders, permission errors, and locked files gracefully
- Detailed **execution summary** and persistent **logging**
- 100% **Python standard library** — no external dependencies

## Requirements

- Python **3.14.6** (developed and tested on this version)
- No third-party packages required

## Project Structure

```
file-organizer/
├── organizer.py          # CLI entry point, scanning, moving, summary
├── config.py             # Extension-to-category mapping
├── utils.py              # Categorization, unique names, safe folder creation
├── sample_folder/        # Demo files (flat + nested subfolders)
├── tests/
│   ├── test_organizer.py # 27 unittest test cases
│   └── test_cases.md     # Manual test report with real results
├── logs/
│   └── organizer.log     # Auto-generated activity log
├── screenshots/          # Before/after evidence
└── README.md
```

## Installation

```bash
git clone https://github.com/Sreevalli20/skill3.git
cd skill3/file-organizer
python --version   # verify Python 3.14.6
```

No `pip install` step is needed.

## Usage

```bash
# Organize the sample folder
python organizer.py "sample_folder"

# Preview without making changes
python organizer.py "sample_folder" --dry-run

# Restore files from the last run
python organizer.py "sample_folder" --undo

# Show help
python organizer.py --help
```

Organize any folder by passing its path:

```bash
python organizer.py "C:/Users/You/Downloads"
```

## Example Output

```
===== ORGANIZER SUMMARY =====
Target folder      : ...\file-organizer\sample_folder
Mode               : LIVE
Total files found  : 10
  Images      : 2
  Documents   : 3
  Videos      : 1
  Audio       : 1
  Archives    : 1
  Others      : 2
Skipped            : 3
Failed             : 0
==============================
```

## File Categorization Rules

Extensions are normalized with `Path.suffix.lower()`, so `photo.JPG` and
`archive.backup.zip` are handled correctly.

| Category   | Extensions                              |
|------------|-----------------------------------------|
| Images     | .jpg .jpeg .png .gif                    |
| Documents  | .pdf .docx .txt .xlsx .pptx             |
| Videos     | .mp4 .mkv .avi                          |
| Audio      | .mp3 .wav                               |
| Archives   | .zip .rar                               |
| Others     | Unknown extensions and no extension     |

## Duplicate Handling

If `Documents/report.pdf` already exists when `report.pdf` is moved, the
file is saved as `report_1.pdf`, then `report_2.pdf`, and so on. No file
ever overwrites another.

## Error Handling & Safety

- Missing or invalid target paths produce a clear error (exit code 1)
- Permission errors and locked files are logged; remaining files continue
- Dry-run creates **no** folders and moves **no** files
- Undo never overwrites an occupied original path
- Category folders are skipped on repeated runs (non-recursive scan)
- If `logs/` is unavailable, logging falls back to the console

## Testing

```bash
cd file-organizer
python -m unittest discover -s tests -v
```

27 tests covering categorization, duplicates, hidden files, subfolders,
empty/missing folders, dry-run, undo, CLI args, move failures, and logging.
See `tests/test_cases.md` for the manual test report.

## Known Limitations

- Scans only the **top level** of the target folder (non-recursive)
- Undo restores files from the **most recent recorded moves** (manifest in
  `logs/move_manifest.json`); it is not a full version-history system
- On case-insensitive filesystems (Windows/macOS), `photo.jpg` and
  `photo.JPG` cannot coexist in the same folder
- Undo leaves empty category folders behind (safe to delete manually)
- `screenshots/` contains tree evidence; capture real screenshots manually
  (see `screenshots/README.md`)
