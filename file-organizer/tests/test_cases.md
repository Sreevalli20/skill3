# Manual Test Report — Automatic File Organizer

All results below were obtained by **actually executing** the application
on Python 3.14.6 (Windows). Unit tests: `python -m unittest discover -s tests`
→ **27 tests ran, 0 failures**.

| Test ID      | Scenario                        | Expected result                                  | Actual result                                                        | Status |
|--------------|---------------------------------|--------------------------------------------------|----------------------------------------------------------------------|--------|
| TC_ORG_01    | Mixed file types                | Each file moved to its category folder           | 10 files moved: Images 2, Documents 3, Videos 1, Audio 1, Archives 1, Others 2 | Pass |
| TC_ORG_02    | Duplicate filenames             | No overwrite; unique name generated (`name_1.ext`)| Unit test: `report.pdf` + pre-existing `Documents/report.pdf` → `report_1.pdf` created, original untouched | Pass |
| TC_ORG_03    | File without extension          | `data` → `Others/data`                           | Confirmed in live run and tree listing                               | Pass |
| TC_ORG_04    | Missing folder                  | Clear error, exit code 1                         | `Error: target folder does not exist: ...nonexistent_folder`, exit=1  | Pass |
| TC_ORG_05    | Uppercase extension             | `sunset.JPG`, `README.TXT` categorized correctly | Both moved to Images/Documents respectively                          | Pass |
| TC_ORG_06    | Hidden files                    | `.hidden_file`, `.secret.txt` skipped            | Hidden file remained at top level; logged as skipped                 | Pass |
| TC_ORG_07    | Nested subfolders               | `nested_sub/`, `nested_deep/` contents untouched | `inner.txt`, `inner_deep.txt` never moved                            | Pass |
| TC_ORG_08    | Multi-dot filename              | `archive.backup.zip` → Archives                  | Moved to `Archives/archive.backup.zip` (suffix `.zip` used)          | Pass |
| TC_ORG_09    | Empty folder                    | Summary shows 0 files, no crash                  | Unit test: `Total files found : 0`, exit 0                           | Pass |
| TC_ORG_10    | Dry-run mode                    | Preview only; zero filesystem changes            | All 10 moves printed as `[DRY-RUN]`; no folders/files created         | Pass |

## Additional verified behaviors

| Scenario                  | Result |
|---------------------------|--------|
| Repeated execution        | Second live run: `Total files found: 0`, category folders skipped — no re-organization |
| `--undo`                  | All 10 files restored to original flat layout; manifest updated; empty category folders may remain |
| `--help`                  | Usage and options displayed correctly |
| Move failure handling     | Unit test mocks `shutil.move` failure: remaining files still processed, exit code 1 |
| Logging                   | `logs/organizer.log` records moves, skips, duplicates, errors; falls back to console if unwritable |
| No accidental overwrites  | `unique_destination()` increments `name_1`, `name_2`, ... until a free name is found |
