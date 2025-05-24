import unittest
import os
import csv
from output import write_csv  # Assuming output.py is in the root or PYTHONPATH


class TestOutput(unittest.TestCase):
    TEST_FILES_DIR = "test_files"

    def setUp(self):
        os.makedirs(self.TEST_FILES_DIR, exist_ok=True)
        self.output_file_path = os.path.join(self.TEST_FILES_DIR, "output_test.csv")

    def tearDown(self):
        if os.path.exists(self.output_file_path):
            os.remove(self.output_file_path)
        # Remove directory if it's empty
        if os.path.exists(self.TEST_FILES_DIR) and not os.listdir(self.TEST_FILES_DIR):
            os.rmdir(self.TEST_FILES_DIR)

    def test_write_csv_typical_data(self):
        records = [
            {"Date": "2023/01/01", "Details": "Transaction 1", "Sum": "100.00"},
            {
                "Date": "2023/01/02",
                "Details": "Transaction 2 with, comma",
                "Sum": "-50.25",
            },
            {
                "Date": "2023/01/03",
                "Details": 'Transaction 3 with "quotes"',
                "Sum": "0.00",
            },
        ]
        write_csv(records, self.output_file_path)

        with open(
            self.output_file_path, mode="r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            self.assertEqual(header, ["Date", "Details", "Sum"])

            expected_data = [
                ["2023/01/01", "Transaction 1", "100.00"],
                ["2023/01/02", "Transaction 2 with, comma", "-50.25"],
                ["2023/01/03", 'Transaction 3 with "quotes"', "0.00"],
            ]
            for i, row in enumerate(reader):
                self.assertEqual(row, expected_data[i])
            # Check if all expected_data was consumed
            self.assertEqual(
                i + 1,
                len(expected_data),
                "Number of data rows in CSV does not match expected.",
            )

    def test_write_csv_empty_records(self):
        records = []
        write_csv(records, self.output_file_path)

        with open(
            self.output_file_path, mode="r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            self.assertEqual(header, ["Date", "Details", "Sum"])

            # Check if there are any more rows
            with self.assertRaises(StopIteration):
                next(reader)

    def test_write_csv_field_order(self):
        records = [{"Sum": "10.00", "Details": "Item A", "Date": "2023/02/01"}]
        write_csv(records, self.output_file_path)

        with open(
            self.output_file_path, mode="r", newline="", encoding="utf-8"
        ) as csvfile:
            lines = csvfile.readlines()
            self.assertEqual(lines[0].strip(), "Date,Details,Sum")
            self.assertEqual(lines[1].strip(), "2023/02/01,Item A,10.00")
            self.assertEqual(len(lines), 2)  # Header + 1 data row


if __name__ == "__main__":
    unittest.main()
