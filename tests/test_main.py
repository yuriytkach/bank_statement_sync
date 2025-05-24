import unittest
import os
import subprocess
import csv
from tests.test_utils import create_excel_file


class TestMainIntegration(unittest.TestCase):
    TEST_FILES_DIR = "test_files"
    MAIN_SCRIPT_PATH = "main.py"  # Assuming main.py is in the project root

    def setUp(self):
        os.makedirs(self.TEST_FILES_DIR, exist_ok=True)
        self.privat_input_path = os.path.join(self.TEST_FILES_DIR, "privat_input.xlsx")
        self.raif_input_path = os.path.join(self.TEST_FILES_DIR, "raif_input.xlsx")
        self.unknown_input_path = os.path.join(
            self.TEST_FILES_DIR, "unknown_input.xlsx"
        )

    def tearDown(self):
        for filename in os.listdir(self.TEST_FILES_DIR):
            os.remove(os.path.join(self.TEST_FILES_DIR, filename))
        if os.path.exists(self.TEST_FILES_DIR) and not os.listdir(self.TEST_FILES_DIR):
            os.rmdir(self.TEST_FILES_DIR)

    def _create_privat_test_file(self, file_path):
        privat_detect_row = ["Виписка з Ваших карток за період..."]
        privat_header = [
            "Дата",
            "Опис операції",
            "Категорія",
            "Валюта картки",
            "Сума в валюті картки",
            "Валюта транзакції",
            "Сума в валюті транзакції",
        ]
        privat_data = [
            [
                "01.01.2023 10:00:00",
                "Test Op 1",
                "Cat A",
                "UAH",
                -100.00,
                "UAH",
                -100.00,
            ],
            ["02.01.2023 12:00:00", "Test Op 2", "Cat B", "USD", -50.00, "EUR", -45.00],
        ]
        full_data = [privat_detect_row, privat_header] + privat_data
        create_excel_file(file_path, "Sheet1", full_data)

    def _create_raif_test_file(self, file_path):
        raif_detect_row = ["АТ «Райффайзен Банк»"]
        raif_header = [
            "Дата і час здійснення операції",
            "Деталі операції",
            "Сума у валюті операції",
            "Валюта",
            "Сума у валюті рахунку",
            "Сума кешбеку",
        ]
        # Dates are mm/dd/yyyy for processor_raif's dayfirst=False
        raif_data = [
            ["01/15/2023 10:15:00", "Raif Op 1: Detail", 150.00, "UAH", 150.00, 0],
            ["02/20/2023 12:30:00", "Raif Op 2: Return", 75.00, "UAH", 75.00, 1.50],
        ]
        full_data = [raif_detect_row, ["Some other info"], raif_header] + raif_data
        create_excel_file(file_path, "Sheet1", full_data)

    def test_main_privat_flow(self):
        self._create_privat_test_file(self.privat_input_path)
        expected_output_csv = os.path.join(self.TEST_FILES_DIR, "privat_input.csv")

        result = subprocess.run(
            ["python", self.MAIN_SCRIPT_PATH, self.privat_input_path],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(expected_output_csv))

        expected_csv_data = [
            ["Date", "Details", "Sum"],
            ["2023/01/01", "Test Op 1 <Cat A> 10:00:00", "-100.00"],
            ["2023/01/02", "Test Op 2 <Cat B> 12:00:00 (-45.00 EUR @ 1.11)", "-50.00"],
        ]
        with open(
            expected_output_csv, mode="r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile)
            for i, expected_row in enumerate(expected_csv_data):
                self.assertEqual(next(reader), expected_row)
            with self.assertRaises(StopIteration):  # Ensure no more rows
                next(reader)

    def test_main_raif_flow(self):
        self._create_raif_test_file(self.raif_input_path)
        expected_output_csv = os.path.join(self.TEST_FILES_DIR, "raif_input.csv")

        result = subprocess.run(
            ["python", self.MAIN_SCRIPT_PATH, self.raif_input_path],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(expected_output_csv))

        expected_csv_data = [
            ["Date", "Details", "Sum"],
            ["2023/01/15", "Detail <Raif Op 1> 10:15:00", "-150.00"],
            ["2023/02/20", "Return <Raif Op 2> 12:30:00 [cashback 1.50]", "75.00"],
        ]
        with open(
            expected_output_csv, mode="r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile)
            for i, expected_row in enumerate(expected_csv_data):
                self.assertEqual(next(reader), expected_row)
            with self.assertRaises(StopIteration):  # Ensure no more rows
                next(reader)

    def test_main_input_file_not_found(self):
        non_existent_file = os.path.join(self.TEST_FILES_DIR, "non_existent_file.xlsx")
        result = subprocess.run(
            ["python", self.MAIN_SCRIPT_PATH, non_existent_file],
            capture_output=True,
            text=True,  # No check=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f"Error: File {non_existent_file} does not exist.", result.stderr)

    def test_main_unknown_structure(self):
        unknown_data = [["Unknown Header Line"], ["Some data"]]
        create_excel_file(self.unknown_input_path, "Sheet1", unknown_data)

        result = subprocess.run(
            ["python", self.MAIN_SCRIPT_PATH, self.unknown_input_path],
            capture_output=True,
            text=True,  # No check=True
        )
        self.assertNotEqual(result.returncode, 0)
        # The exact error message might vary depending on detect_structure implementation
        # Checking for a part of the expected error message.
        self.assertTrue(
            "Error detecting structure" in result.stderr
            or "Unknown structure" in result.stderr
            or "Could not determine bank structure" in result.stderr
        )


if __name__ == "__main__":
    unittest.main()
