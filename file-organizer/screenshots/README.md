# Screenshots

This folder is reserved for before/after screenshots of the
`sample_folder` demonstration.

## Why there are no image files here

No screenshot-capture tool was available in the build environment, so
no images were fabricated. Instead, real folder-tree evidence captured
during actual execution is provided in `before_after_evidence.txt`.

## How to capture the screenshots manually

1. Open File Explorer and navigate to `file-organizer/sample_folder`.
2. Take a "before" screenshot (restore the flat layout first if needed):

   ```bash
   cd file-organizer
   python organizer.py sample_folder --undo
   ```

3. Run the organizer:

   ```bash
   python organizer.py sample_folder
   ```

4. Take an "after" screenshot showing the `Images`, `Documents`,
   `Videos`, `Audio`, `Archives`, and `Others` folders.
5. Save both images in this folder (e.g. `before.png`, `after.png`).
