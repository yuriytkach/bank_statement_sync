import unittest
import os
import subprocess
import csv
import inspect  # Added import
from tests.test_utils import create_excel_file


class TestMainIntegration(unittest.TestCase):
    MAIN_SCRIPT_PATH = "main.py"  # Assuming main.py is in the project root

    def setUp(self):
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

        # Directory where test files are created by test_main.py (e.g., tests/test_files)
        self.creation_dir = os.path.join(os.path.dirname(__file__), "test_files")
        os.makedirs(self.creation_dir, exist_ok=True)

        # Path prefix for arguments passed to main.py (e.g., tests/test_files)
        # This is how main.py, running from project_root, will see the files.
        self.main_py_arg_dir = os.path.join("tests", "test_files")

        # Define full paths for file creation (used by create_excel_file)
        self.privat_input_creation_path = os.path.join(
            self.creation_dir, "privat_input.xlsx"
        )
        self.raif_input_creation_path = os.path.join(
            self.creation_dir, "raif_input.xlsx"
        )
        self.unknown_input_creation_path = os.path.join(
            self.creation_dir, "unknown_input.xlsx"
        )
        # Non-existent file path does not need a creation_path if it's truly non-existent

        # Define paths for main.py arguments (relative to project_root)
        self.privat_input_arg = os.path.join(self.main_py_arg_dir, "privat_input.xlsx")
        self.raif_input_arg = os.path.join(self.main_py_arg_dir, "raif_input.xlsx")
        self.unknown_input_arg = os.path.join(
            self.main_py_arg_dir, "unknown_input.xlsx"
        )

    def tearDown(self):
        # Clean up created Excel files
        if os.path.exists(self.creation_dir):
            for item in os.listdir(self.creation_dir):
                item_path = os.path.join(self.creation_dir, item)
                if os.path.isfile(item_path) and item.endswith(
                    ".xlsx"
                ):  # Only remove .xlsx test files
                    os.remove(item_path)

            # Clean up generated CSV files (which are in tests/test_files relative to project_root)
            # main.py creates CSVs next to its input files.
            # So, if input is tests/test_files/input.xlsx, output is tests/test_files/input.csv
            # self.creation_dir IS tests/test_files (absolute path)
            # So we just need to look for .csv files in self.creation_dir
            for item in os.listdir(self.creation_dir):
                if item.endswith(".csv"):
                    os.remove(os.path.join(self.creation_dir, item))

            # Try to remove the directory if it's empty
            if not os.listdir(self.creation_dir):
                os.rmdir(self.creation_dir)

    def _create_privat_test_file(self, file_creation_path):  # Renamed argument
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
        create_excel_file(
            file_creation_path, "Sheet1", full_data
        )  # Use the passed path

    def _create_raif_test_file(self, file_creation_path):  # Renamed argument
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
            ["01/15/2023 10:15:00", "Raif Op 1: Detail", 150.00, "", 150.00, 0],
            ["02/20/2023 12:30:00", "Повернення: Return", 200.00, "EUR", 75.00, 1.50],
        ]
        full_data = [raif_detect_row, ["Some other info"], raif_header] + raif_data
        create_excel_file(
            file_creation_path, "Sheet1", full_data
        )  # Use the passed path

    def test_main_privat_flow(self):
        self._create_privat_test_file(self.privat_input_creation_path)
        expected_csv_path = os.path.join(
            self.project_root, self.main_py_arg_dir, "privat_input.csv"
        )

        result = subprocess.run(
            ["python", self.MAIN_SCRIPT_PATH, self.privat_input_arg],  # Use _arg
            capture_output=True,
            text=True,
            cwd=self.project_root,  # Removed check=True
        )
        # Added print statements and new assert
        print(
            f"stdout for {self.privat_input_arg if 'privat' in inspect.currentframe().f_code.co_name else self.raif_input_arg}:\n{result.stdout}"
        )
        print(
            f"stderr for {self.privat_input_arg if 'privat' in inspect.currentframe().f_code.co_name else self.raif_input_arg}:\n{result.stderr}"
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"main.py exited with {result.returncode}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertTrue(os.path.exists(expected_csv_path))

        expected_csv_data = [
            ["Date", "Details", "Sum"],
            ["2023/01/01", "Test Op 1 <Cat A> 10:00:00", "-100.00"],
            ["2023/01/02", "Test Op 2 <Cat B> 12:00:00 (-45.00 EUR @ 1.11)", "-50.00"],
        ]
        with open(
            expected_csv_path, mode="r", newline="", encoding="utf-8"
        ) as csvfile:  # Use expected_csv_path
            reader = csv.reader(csvfile)
            for i, expected_row in enumerate(expected_csv_data):
                self.assertEqual(next(reader), expected_row)
            with self.assertRaises(StopIteration):  # Ensure no more rows
                next(reader)

    def test_main_raif_flow(self):
        self._create_raif_test_file(self.raif_input_creation_path)
        expected_csv_path = os.path.join(
            self.project_root, self.main_py_arg_dir, "raif_input.csv"
        )

        result = subprocess.run(
            ["python", self.MAIN_SCRIPT_PATH, self.raif_input_arg],  # Use _arg
            capture_output=True,
            text=True,
            cwd=self.project_root,  # Removed check=True
        )
        # Added print statements and new assert
        print(
            f"stdout for {self.privat_input_arg if 'privat' in inspect.currentframe().f_code.co_name else self.raif_input_arg}:\n{result.stdout}"
        )
        print(
            f"stderr for {self.privat_input_arg if 'privat' in inspect.currentframe().f_code.co_name else self.raif_input_arg}:\n{result.stderr}"
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"main.py exited with {result.returncode}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertTrue(os.path.exists(expected_csv_path))

        expected_csv_data = [
            ["Date", "Details", "Sum"],
            ["2023/01/15", "Detail <Raif Op 1> 10:15:00", "-150.00"],
            [
                "2023/02/20",
                "Return <Повернення> 12:30:00 (200.00 EUR @ 0.38) [cashback 1.50]",
                "75.00",
            ],
        ]
        with open(
            expected_csv_path, mode="r", newline="", encoding="utf-8"
        ) as csvfile:  # Use expected_csv_path
            reader = csv.reader(csvfile)
            for i, expected_row in enumerate(expected_csv_data):
                self.assertEqual(next(reader), expected_row)
            with self.assertRaises(StopIteration):  # Ensure no more rows
                next(reader)

    def test_main_input_file_not_found(self):
        non_existent_file_arg = os.path.join(
            self.main_py_arg_dir, "non_existent_file.xlsx"
        )
        result = subprocess.run(
            ["python", self.MAIN_SCRIPT_PATH, non_existent_file_arg],  # Use _arg
            capture_output=True,
            text=True,
            cwd=self.project_root,  # No check=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            f"Error: File '{non_existent_file_arg}' does not exist.", result.stderr
        )  # Use _arg and ensure quotes

    def test_main_unknown_structure(self):
        unknown_data = [["Unknown Header Line"], ["Some data"]]
        create_excel_file(
            self.unknown_input_creation_path, "Sheet1", unknown_data
        )  # Use _creation_path

        result = subprocess.run(
            ["python", self.MAIN_SCRIPT_PATH, self.unknown_input_arg],  # Use _arg
            capture_output=True,
            text=True,
            cwd=self.project_root,  # No check=True
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
