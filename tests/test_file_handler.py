import unittest
import os
import tempfile
import zipfile
import shutil
from converter.file_handler import process_uploaded_file, cleanup_temp_directory

class MockGradioFile:
    def __init__(self, name):
        self.name = name

class TestFileHandler(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory to hold test files, distinct from dirs created by the functions
        self.test_files_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the directory holding test files
        shutil.rmtree(self.test_files_dir)

    def test_process_single_file(self):
        # Create a dummy temporary file
        dummy_file_path = os.path.join(self.test_files_dir, "test_file.js")
        with open(dummy_file_path, "w") as f:
            f.write("console.log('hello');")

        mock_file_obj = MockGradioFile(name=dummy_file_path)

        file_paths, temp_dir_created = process_uploaded_file(mock_file_obj)

        self.assertIsNotNone(file_paths, "process_uploaded_file returned None for file_paths")
        self.assertIsNotNone(temp_dir_created, "process_uploaded_file returned None for temp_dir_created")
        self.assertEqual(len(file_paths), 1)
        self.assertTrue(os.path.exists(file_paths[0]))
        self.assertEqual(os.path.basename(file_paths[0]), "test_file.js")

        cleanup_temp_directory(temp_dir_created)
        self.assertFalse(os.path.exists(temp_dir_created))

    def test_process_zip_file(self):
        # Create a dummy zip file
        zip_file_path = os.path.join(self.test_files_dir, "test_archive.zip")
        file1_content = "var a = 1;"
        file2_content = "This is a text file."

        with zipfile.ZipFile(zip_file_path, 'w') as zf:
            zf.writestr("file1.js", file1_content)
            zf.writestr("subdir/file2.txt", file2_content) # Add a file in a subdirectory

        mock_zip_obj = MockGradioFile(name=zip_file_path)

        file_paths, temp_dir_created = process_uploaded_file(mock_zip_obj)

        self.assertIsNotNone(file_paths, "process_uploaded_file returned None for file_paths (zip)")
        self.assertIsNotNone(temp_dir_created, "process_uploaded_file returned None for temp_dir_created (zip)")

        # Sort paths to ensure consistent order for assertions
        file_paths.sort()

        self.assertEqual(len(file_paths), 2, f"Expected 2 files, got {len(file_paths)}: {file_paths}")

        # Check base names and existence
        basenames = sorted([os.path.basename(p) for p in file_paths])
        self.assertListEqual(basenames, ["file1.js", "file2.txt"])

        for p in file_paths:
            self.assertTrue(os.path.exists(p), f"File {p} does not exist after extraction.")

        # Verify content of one file as a sanity check
        file1_js_path = next((p for p in file_paths if p.endswith("file1.js")), None)
        self.assertIsNotNone(file1_js_path)
        with open(file1_js_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, file1_content)

        cleanup_temp_directory(temp_dir_created)
        self.assertFalse(os.path.exists(temp_dir_created))

    def test_process_invalid_zip_file(self):
        # Create an empty (invalid) zip file
        invalid_zip_path = os.path.join(self.test_files_dir, "invalid.zip")
        with open(invalid_zip_path, "w") as f:
            f.write("This is not a zip file")

        mock_invalid_zip_obj = MockGradioFile(name=invalid_zip_path)
        file_paths, temp_dir_created = process_uploaded_file(mock_invalid_zip_obj)

        self.assertIsNone(file_paths, "File paths should be None for invalid zip.")
        # temp_dir_created might exist or not depending on when error occurs,
        # but cleanup_temp_directory should handle it.
        # The important part is that process_uploaded_file signals an error.
        if temp_dir_created: # cleanup if it was created before error detection
            cleanup_temp_directory(temp_dir_created)


if __name__ == "__main__":
    unittest.main()
