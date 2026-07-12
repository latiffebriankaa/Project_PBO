"""Unit test suite for BeresFile application."""

import json
import unittest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
from unittest.mock import MagicMock, patch

from models.file_item import FileItem
from rules.rule_ekstensi import RuleEkstensi
from rules.rule_ai import RuleAI
from services.file_organizer import FileOrganizer, ProcessResult


class TestFileItem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.test_file = self.temp_path / "test_document.pdf"
        self.test_file.write_text("dummy content")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_properties(self):
        item = FileItem(self.test_file)
        self.assertEqual(item.name, "test_document")
        self.assertEqual(item.ext, ".pdf")
        self.assertTrue(item.size > 0)
        self.assertIsInstance(item.mod_time, datetime)
        self.assertEqual(item.parent_dir, self.temp_path)
        self.assertTrue(item.is_file())

    def test_sanitize_name(self):
        item = FileItem(self.test_file)
        self.assertEqual(item.sanitize_name("my test  file"), "my_test_file")
        self.assertEqual(item.sanitize_name("test<>:|?*file"), "test_file")
        self.assertEqual(item.sanitize_name("...test_file..."), "test_file")
        self.assertEqual(item.sanitize_name(""), "file")

    def test_rename(self):
        item = FileItem(self.test_file)
        new_path = item.rename("new name")
        self.assertEqual(new_path.name, "new_name.pdf")

        with self.assertRaises(ValueError):
            item.rename("")
        with self.assertRaises(ValueError):
            item.rename("  ")

    def test_move_to(self):
        item = FileItem(self.test_file)
        target = self.temp_path / "SubFolder"
        dest = item.move_to(target)
        self.assertEqual(dest, target / "test_document.pdf")


class TestRuleEkstensi(unittest.TestCase):
    def setUp(self):
        self.rule = RuleEkstensi()

    def test_determine_category(self):
        mock_file = MagicMock()
        
        # General mappings
        mock_file.ext = ".pdf"
        self.assertEqual(self.rule.determine_category(mock_file), "PDF")
        
        mock_file.ext = ".docx"
        self.assertEqual(self.rule.determine_category(mock_file), "Word")

        mock_file.ext = ".zip"
        self.assertEqual(self.rule.determine_category(mock_file), "Arsip")

        mock_file.ext = ".unknown"
        self.assertEqual(self.rule.determine_category(mock_file), "Lainnya")

    def test_determine_category_special_naming(self):
        mock_file = MagicMock()
        
        # Image screenshots vs logo
        mock_file.ext = ".png"
        mock_file.name = "screenshot_2026"
        self.assertEqual(self.rule.determine_category(mock_file), "Screenshot")

        mock_file.name = "my_logo_design"
        self.assertEqual(self.rule.determine_category(mock_file), "Logo")

        mock_file.name = "photo"
        self.assertEqual(self.rule.determine_category(mock_file), "Gambar")

        # Installers
        mock_file.ext = ".exe"
        mock_file.name = "setup_app"
        self.assertEqual(self.rule.determine_category(mock_file), "Installer")

        mock_file.name = "my_game"
        self.assertEqual(self.rule.determine_category(mock_file), "Program")

    def test_generate_new_name(self):
        mock_file = MagicMock()
        mock_file.name = "tugas_kuliah"
        mock_file.mod_time = datetime(2026, 7, 12, 10, 0, 0)
        mock_file.sanitize_name = lambda s: s.replace(" ", "_")
        
        new_name = self.rule.generate_new_name(mock_file, "PDF")
        self.assertEqual(new_name, "2026-07-12_tugas_kuliah_PDF")


class TestRuleAI(unittest.TestCase):
    def test_is_available(self):
        rule = RuleAI("")
        self.assertFalse(rule.is_available())

        rule = RuleAI("AIzaSyDummyKey")
        self.assertTrue(rule.is_available())

    def test_determine_category_non_image(self):
        rule = RuleAI("AIzaSyDummyKey")
        mock_file = MagicMock()
        mock_file.ext = ".txt"
        self.assertEqual(rule.determine_category(mock_file), "")

    @patch("rules.rule_ai.requests")
    def test_generate_new_name_fallback_on_api_error(self, mock_requests):
        # Mock requests failure
        mock_requests.post.side_effect = Exception("API error")
        rule = RuleAI("AIzaSyDummyKey")
        
        mock_file = MagicMock()
        mock_file.ext = ".png"
        mock_file.name = "original_name"
        mock_file.path = Path("original_name.png")
        mock_file.sanitize_name = lambda s: s.replace(" ", "_")

        new_name = rule.generate_new_name(mock_file, "Gambar")
        self.assertEqual(new_name, "original_name")


class TestFileOrganizer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create some test files
        (self.temp_path / "file1.pdf").write_text("content unique 1")
        (self.temp_path / "file2.docx").write_text("content unique 2")
        (self.temp_path / "file3.docx").write_text("content unique 2")  # duplicate of file2
        (self.temp_path / "file4.txt").write_text("content unique 3")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dry_run_process(self):
        rules = [RuleEkstensi()]
        organizer = FileOrganizer(rules=rules, dry_run=True, output_root_name="BeresFileTest")
        result = organizer.process_directory(self.temp_path)

        # Verify results
        self.assertEqual(result.total, 4)
        self.assertEqual(result.processed, 3)  # 3 unique files
        self.assertEqual(result.duplicates, 1)  # 1 duplicate file
        self.assertEqual(result.errors, 0)
        
        # Verify files are NOT moved because dry_run=True
        self.assertTrue((self.temp_path / "file1.pdf").exists())
        self.assertTrue((self.temp_path / "file2.docx").exists())
        self.assertTrue((self.temp_path / "file3.docx").exists())
        self.assertTrue((self.temp_path / "file4.txt").exists())

        # Verify manifest is created
        manifest_path = self.temp_path / "BeresFile_Logs" / "beresfile_manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertTrue(manifest["dry_run"])
        self.assertEqual(len(manifest["actions"]), 3)
        self.assertEqual(len(manifest["logs"]), 4)

    def test_actual_run_process(self):
        rules = [RuleEkstensi()]
        organizer = FileOrganizer(rules=rules, dry_run=False, output_root_name="BeresFileTest")
        result = organizer.process_directory(self.temp_path)

        # Verify results
        self.assertEqual(result.total, 4)
        self.assertEqual(result.processed, 3)
        self.assertEqual(result.duplicates, 1)

        # Original files should be moved (except duplicate which is skipped)
        self.assertFalse((self.temp_path / "file1.pdf").exists())
        self.assertFalse((self.temp_path / "file2.docx").exists())
        self.assertTrue((self.temp_path / "file3.docx").exists())  # Duplicate skipped and remains
        self.assertFalse((self.temp_path / "file4.txt").exists())

        # Subfolders should contain moved files
        output_dir = self.temp_path / "BeresFileTest"
        self.assertTrue(output_dir.exists())
        
        pdf_files = list((output_dir / "PDF").glob("*.pdf"))
        self.assertEqual(len(pdf_files), 1)

        word_files = list((output_dir / "Word").glob("*.docx"))
        self.assertEqual(len(word_files), 1)

        txt_files = list((output_dir / "Teks").glob("*.txt"))
        self.assertEqual(len(txt_files), 1)

    def test_undo_last_run(self):
        rules = [RuleEkstensi()]
        organizer = FileOrganizer(rules=rules, dry_run=False, output_root_name="BeresFileTest")
        
        # Run organizer
        organizer.process_directory(self.temp_path)

        # Ensure files were moved
        self.assertFalse((self.temp_path / "file1.pdf").exists())

        # Perform undo
        undo_logs, manifest_path = organizer.undo_last_run(self.temp_path)
        self.assertEqual(len(undo_logs), 3)

        # Ensure files are restored to their original location
        self.assertTrue((self.temp_path / "file1.pdf").exists())
        self.assertTrue((self.temp_path / "file2.docx").exists())
        self.assertTrue((self.temp_path / "file4.txt").exists())


if __name__ == "__main__":
    unittest.main()
