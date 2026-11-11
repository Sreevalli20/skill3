"""Unit tests for the Automatic File Organizer.

Run from the file-organizer directory:
    python -m unittest discover -s tests -v
"""

import io
import json
import logging
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

# Ensure the project root is importable when tests run from anywhere.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import organizer
from config import EXTENSION_MAP, DEFAULT_CATEGORY
from utils import categorize, is_hidden, unique_destination, safe_makedirs


def make_file(folder: Path, name: str, content: str = "x") -> Path:
    path = folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class TestCategorize(unittest.TestCase):
    def test_lowercase_extension(self):
        self.assertEqual(categorize(Path("a.pdf"), EXTENSION_MAP, DEFAULT_CATEGORY), "Documents")

    def test_uppercase_extension(self):
        self.assertEqual(categorize(Path("photo.JPG"), EXTENSION_MAP, DEFAULT_CATEGORY), "Images")

    def test_multi_dot_filename(self):
        self.assertEqual(
            categorize(Path("archive.backup.zip"), EXTENSION_MAP, DEFAULT_CATEGORY), "Archives"
        )

    def test_no_extension(self):
        self.assertEqual(categorize(Path("data"), EXTENSION_MAP, DEFAULT_CATEGORY), DEFAULT_CATEGORY)

    def test_unknown_extension(self):
        self.assertEqual(categorize(Path("unknown.xyz"), EXTENSION_MAP, DEFAULT_CATEGORY), DEFAULT_CATEGORY)


class TestUtils(unittest.TestCase):
    def test_is_hidden(self):
        self.assertTrue(is_hidden(Path(".hidden")))
        self.assertFalse(is_hidden(Path("visible.txt")))

    def test_unique_destination_no_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            dest = unique_destination(d, "report.pdf")
            self.assertEqual(dest.name, "report.pdf")

    def test_unique_destination_duplicate(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            make_file(d, "report.pdf")
            make_file(d, "report_1.pdf")
            dest = unique_destination(d, "report.pdf")
            self.assertEqual(dest.name, "report_2.pdf")

    def test_safe_makedirs_dry_run_creates_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "NewCat"
            self.assertTrue(safe_makedirs(d, dry_run=True))
            self.assertFalse(d.exists())

    def test_safe_makedirs_real(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "NewCat"
            self.assertTrue(safe_makedirs(d))
            self.assertTrue(d.is_dir())


class TestOrganize(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        # Isolate manifest/log paths so tests never touch the real logs/ dir.
        self._orig = (organizer.MANIFEST_FILE, organizer.LOG_DIR, organizer.LOG_FILE)
        organizer.MANIFEST_FILE = self.folder / "manifest.json"
        organizer.LOG_DIR = self.folder / "logs"
        organizer.LOG_FILE = organizer.LOG_DIR / "organizer.log"

    def tearDown(self):
        (organizer.MANIFEST_FILE, organizer.LOG_DIR, organizer.LOG_FILE) = self._orig
        self._tmp.cleanup()

    def run_organize(self, dry_run=False):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = organizer.organize(self.folder, dry_run=dry_run)
        return code, buf.getvalue()

    def test_mixed_file_types(self):
        make_file(self.folder, "a.jpg")
        make_file(self.folder, "b.pdf")
        make_file(self.folder, "c.mp4")
        make_file(self.folder, "d.mp3")
        make_file(self.folder, "e.zip")
        code, _ = self.run_organize()
        self.assertEqual(code, 0)
        self.assertTrue((self.folder / "Images" / "a.jpg").exists())
        self.assertTrue((self.folder / "Documents" / "b.pdf").exists())
        self.assertTrue((self.folder / "Videos" / "c.mp4").exists())
        self.assertTrue((self.folder / "Audio" / "d.mp3").exists())
        self.assertTrue((self.folder / "Archives" / "e.zip").exists())

    def test_no_overwrite_on_repeat_run(self):
        make_file(self.folder, "report.pdf")
        make_file(self.folder, "Documents/report.pdf")  # pre-existing collision
        code, _ = self.run_organize()
        self.assertEqual(code, 0)
        # original destination untouched; moved file got a unique name
        self.assertTrue((self.folder / "Documents" / "report.pdf").exists())
        self.assertTrue((self.folder / "Documents" / "report_1.pdf").exists())
        # second run must not move category contents again
        code2, _ = self.run_organize()
        self.assertEqual(code2, 0)
        self.assertEqual(len(list((self.folder / "Documents").iterdir())), 2)

    def test_duplicate_filenames(self):
        # Two files same name can't coexist; simulate via pre-existing dest.
        make_file(self.folder, "Images/dup.txt")
        # 'dup.txt' is inside a subdir -> skipped. Instead test unique_destination
        # end-to-end: create category file that collides.
        make_file(self.folder, "a.txt")
        make_file(self.folder, "Documents/a.txt")
        # Documents/a.txt skipped (subdir); a.txt moves to Documents/a_1.txt? No:
        # Documents dir exists and contains a.txt already -> dest is a_1.txt
        code, _ = self.run_organize()
        self.assertEqual(code, 0)
        self.assertTrue((self.folder / "Documents" / "a_1.txt").exists())
        self.assertTrue((self.folder / "Documents" / "a.txt").exists())

    def test_hidden_files_skipped(self):
        make_file(self.folder, ".secret.txt")
        make_file(self.folder, "visible.txt")
        code, _ = self.run_organize()
        self.assertEqual(code, 0)
        self.assertTrue((self.folder / ".secret.txt").exists())
        self.assertTrue((self.folder / "Documents" / "visible.txt").exists())

    def test_subdirectories_skipped(self):
        make_file(self.folder, "sub/inner.txt")
        code, _ = self.run_organize()
        self.assertEqual(code, 0)
        self.assertTrue((self.folder / "sub/inner.txt").exists())

    def test_no_extension_goes_to_others(self):
        make_file(self.folder, "data")
        code, _ = self.run_organize()
        self.assertEqual(code, 0)
        self.assertTrue((self.folder / "Others" / "data").exists())

    def test_unknown_extension_goes_to_others(self):
        make_file(self.folder, "unknown.xyz")
        code, _ = self.run_organize()
        self.assertEqual(code, 0)
        self.assertTrue((self.folder / "Others" / "unknown.xyz").exists())

    def test_empty_folder(self):
        code, out = self.run_organize()
        self.assertEqual(code, 0)
        self.assertIn("Total files found  : 0", out)

    def test_missing_folder(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = organizer.organize(self.folder / "does_not_exist")
        self.assertEqual(code, 1)
        self.assertIn("does not exist", buf.getvalue())

    def test_dry_run_changes_nothing(self):
        make_file(self.folder, "a.jpg")
        make_file(self.folder, "b.txt")
        code, out = self.run_organize(dry_run=True)
        self.assertEqual(code, 0)
        self.assertIn("DRY-RUN", out)
        self.assertTrue((self.folder / "a.jpg").exists())
        self.assertTrue((self.folder / "b.txt").exists())
        self.assertFalse((self.folder / "Images").exists())
        self.assertFalse((self.folder / "Documents").exists())

    def test_move_failure_continues(self):
        make_file(self.folder, "good.txt")
        make_file(self.folder, "bad.xyz")
        real_move = organizer.shutil.move

        def flaky_move(src, dst):
            if str(src).endswith("bad.xyz"):
                raise OSError("simulated locked file")
            return real_move(src, dst)

        with mock.patch.object(organizer.shutil, "move", side_effect=flaky_move):
            code, _ = self.run_organize()
        self.assertEqual(code, 1)  # one failure reported
        self.assertTrue((self.folder / "Documents" / "good.txt").exists())
        self.assertTrue((self.folder / "bad.xyz").exists())  # untouched

    def test_undo_restores_files(self):
        src = make_file(self.folder, "restore_me.pdf")
        code, _ = self.run_organize()
        self.assertEqual(code, 0)
        dest = self.folder / "Documents" / "restore_me.pdf"
        self.assertTrue(dest.exists())

        # Point manifest + log at temp locations for the undo test.
        manifest = self.folder / "manifest.json"
        organizer.MANIFEST_FILE = manifest
        organizer.LOG_DIR = self.folder / "logs"
        organizer.LOG_FILE = organizer.LOG_DIR / "organizer.log"
        try:
            organizer.save_manifest([{"source": str(src), "destination": str(dest)}])
            buf = io.StringIO()
            with redirect_stdout(buf):
                ucode = organizer.undo_moves()
            self.assertEqual(ucode, 0)
            self.assertTrue(src.exists())
            self.assertFalse(dest.exists())
        finally:
            organizer.MANIFEST_FILE = PROJECT_ROOT / "logs" / "move_manifest.json"
            organizer.LOG_DIR = PROJECT_ROOT / "logs"
            organizer.LOG_FILE = PROJECT_ROOT / "logs" / "organizer.log"

    def test_undo_never_overwrites(self):
        make_file(self.folder, "clash.txt")
        code, _ = self.run_organize()
        self.assertEqual(code, 0)
        dest = self.folder / "Documents" / "clash.txt"
        # recreate an occupant at the original path
        make_file(self.folder, "clash.txt", "occupant")

        organizer.MANIFEST_FILE = self.folder / "manifest.json"
        try:
            organizer.save_manifest([{"source": str(self.folder / "clash.txt"),
                                      "destination": str(dest)}])
            buf = io.StringIO()
            with redirect_stdout(buf):
                organizer.undo_moves()
            self.assertEqual((self.folder / "clash.txt").read_text(), "occupant")
            self.assertTrue(dest.exists())
        finally:
            organizer.MANIFEST_FILE = PROJECT_ROOT / "logs" / "move_manifest.json"


class TestCLI(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as cm:
            organizer.parse_args(["--help"])
        self.assertEqual(cm.exception.code, 0)

    def test_missing_folder_arg(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = organizer.main([])
        self.assertEqual(code, 2)
        self.assertIn("target folder", buf.getvalue())

    def test_main_with_dry_run(self):
        with tempfile.TemporaryDirectory() as td:
            make_file(Path(td), "z.png")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = organizer.main([td, "--dry-run"])
            self.assertEqual(code, 0)
            self.assertTrue((Path(td) / "z.png").exists())


class TestLogging(unittest.TestCase):
    def test_logger_configured(self):
        organizer.setup_logging()
        self.assertTrue(organizer.logger.handlers)
        self.assertTrue(any(isinstance(h, logging.FileHandler)
                            for h in organizer.logger.handlers))


if __name__ == "__main__":
    unittest.main()
