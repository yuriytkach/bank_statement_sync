import unittest
import os
import pandas as pd
from structure_detector import detect_structure
from tests.test_utils import create_excel_file

class TestStructureDetector(unittest.TestCase):
    TEST_FILES_DIR = "test_files"

    def setUp(self):
        os.makedirs(self.TEST_FILES_DIR, exist_ok=True)

    def tearDown(self):
        for filename in os.listdir(self.TEST_FILES_DIR):
            os.remove(os.path.join(self.TEST_FILES_DIR, filename))
        # Also remove the directory if it's empty, be careful if other tests might use it.
        # For this specific setup, it's generally safe if only this test class uses it.
        if not os.listdir(self.TEST_FILES_DIR):
            os.rmdir(self.TEST_FILES_DIR)

    def test_detect_privat_structure(self):
        filepath = os.path.join(self.TEST_FILES_DIR, "privat_test.xlsx")
        data = [["Виписка з Ваших карток за період..."]]
        create_excel_file(filepath, "Sheet1", data)
        self.assertEqual(detect_structure(filepath), "privat")

    def test_detect_raif_structure(self):
        filepath = os.path.join(self.TEST_FILES_DIR, "raif_test.xlsx")
        data = [["АТ «Райффайзен Банк»", "Some other data"], ["Second_row_data"]]
        create_excel_file(filepath, "Sheet1", data)
        self.assertEqual(detect_structure(filepath), "raif")

    def test_detect_unknown_structure(self):
        filepath = os.path.join(self.TEST_FILES_DIR, "unknown_test.xlsx")
        data = [["Some unknown header"]]
        create_excel_file(filepath, "Sheet1", data)
        with self.assertRaises(ValueError):
            detect_structure(filepath)

    def test_detect_empty_file(self):
        filepath = os.path.join(self.TEST_FILES_DIR, "empty_test.xlsx")
        data = []
        create_excel_file(filepath, "Sheet1", data)
        # Depending on pandas behavior and structure_detector's handling of empty/malformed files,
        # this might be ValueError, IndexError, or a custom exception.
        # ValueError is a good general start if structure_detector is expected to raise it.
        # If pandas itself raises an error before structure_detector (e.g. trying to read [0,0]),
        # then that error (e.g. IndexError) would be caught.
        # Let's assume structure_detector is robust enough to attempt reading and then decides it's unknown or invalid.
        with self.assertRaises(ValueError): # Or IndexError, or specific custom error
            detect_structure(filepath)

if __name__ == '__main__':
    unittest.main()
