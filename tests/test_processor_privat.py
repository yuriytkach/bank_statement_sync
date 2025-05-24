import unittest
import os
import datetime
import pandas as pd  # Required for process_privat, and potentially for type hints if used
from processor_privat import process as process_privat
from tests.test_utils import create_excel_file


class TestProcessorPrivat(unittest.TestCase):
    TEST_FILES_DIR = "test_files"
    PRIVAT_DETECTION_ROW = ["Виписка з Ваших карток за період..."]

    def setUp(self):
        os.makedirs(self.TEST_FILES_DIR, exist_ok=True)

    def tearDown(self):
        for filename in os.listdir(self.TEST_FILES_DIR):
            os.remove(os.path.join(self.TEST_FILES_DIR, filename))
        if not os.listdir(self.TEST_FILES_DIR):
            os.rmdir(self.TEST_FILES_DIR)

    def test_process_privat_typical_file(self):
        filepath = os.path.join(self.TEST_FILES_DIR, "privat_typical.xlsx")
        header = [
            "Дата",
            "Опис операції",
            "Категорія",
            "Валюта картки",
            "Сума в валюті картки",
            "Валюта транзакції",
            "Сума в валюті транзакції",
        ]
        data_rows = [
            [
                "01.01.2023 10:00:00",
                "Payment for goods",
                "Products",
                "UAH",
                -100.50,
                "UAH",
                -100.50,
            ],
            [
                "02.01.2023 12:30:00",
                "Online purchase",
                "Shopping",
                "USD",
                -50.00,
                "EUR",
                -45.00,
            ],
            [
                None,
                "Should be skipped",
                "Junk",
                "UAH",
                -10.0,
                "UAH",
                -10.0,
            ],  # Row with missing date
            [
                "03.01.2023 15:00:00",
                "Coffee",
                "",
                "UAH",
                -25.75,
                "UAH",
                -25.75,
            ],  # No category
        ]
        excel_data = [self.PRIVAT_DETECTION_ROW, header] + data_rows
        create_excel_file(filepath, "Sheet1", excel_data)

        result = process_privat(filepath)

        self.assertEqual(len(result), 3)  # Row with None date should be skipped
        self.assertEqual(
            result[0],
            {
                "Date": "2023/01/01",
                "Details": "Payment for goods <Products> 10:00:00",
                "Sum": "-100.50",
            },
        )
        # Rate: abs(-50.00) / abs(-45.00) = 50.00 / 45.00 = 1.111... -> "1.11"
        self.assertEqual(
            result[1],
            {
                "Date": "2023/01/02",
                "Details": "Online purchase <Shopping> 12:30:00 (-45.00 EUR @ 1.11)",
                "Sum": "-50.00",
            },
        )
        self.assertEqual(
            result[2],
            {"Date": "2023/01/03", "Details": "Coffee 15:00:00", "Sum": "-25.75"},
        )

    def test_process_privat_missing_optional_columns(self):
        filepath = os.path.join(self.TEST_FILES_DIR, "privat_missing_category.xlsx")
        # Missing "Категорія"
        header = [
            "Дата",
            "Опис операції",
            "Валюта картки",
            "Сума в валюті картки",
            "Валюта транзакції",
            "Сума в валюті транзакції",
        ]
        data_rows = [
            ["05.01.2023 09:00:00", "Service payment", "UAH", -200.00, "UAH", -200.00]
        ]
        excel_data = [self.PRIVAT_DETECTION_ROW, header] + data_rows
        create_excel_file(filepath, "Sheet1", excel_data)

        result = process_privat(filepath)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0],
            {
                "Date": "2023/01/05",
                "Details": "Service payment 09:00:00",
                "Sum": "-200.00",
            },
        )

    def test_process_privat_different_currencies(self):
        filepath = os.path.join(self.TEST_FILES_DIR, "privat_currencies.xlsx")
        header = [
            "Дата",
            "Опис операції",
            "Категорія",
            "Валюта картки",
            "Сума в валюті картки",
            "Валюта транзакції",
            "Сума в валюті транзакції",
        ]
        data_rows = [
            [
                "06.01.2023 11:00:00",
                "International order",
                "Services",
                "UAH",
                -1500.00,
                "USD",
                -40.00,
            ],  # Rate 1500/40 = 37.50
            [
                "07.01.2023 14:20:00",
                "Refund",
                "Income",
                "UAH",
                300.00,
                "USD",
                8.00,
            ],  # Rate abs(300)/abs(8) = 37.50
        ]
        excel_data = [self.PRIVAT_DETECTION_ROW, header] + data_rows
        create_excel_file(filepath, "Sheet1", excel_data)

        result = process_privat(filepath)
        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0],
            {
                "Date": "2023/01/06",
                "Details": "International order <Services> 11:00:00 (-40.00 USD @ 37.50)",
                "Sum": "-1500.00",
            },
        )
        self.assertEqual(
            result[1],
            {
                "Date": "2023/01/07",
                "Details": "Refund <Income> 14:20:00 (8.00 USD @ 37.50)",
                "Sum": "300.00",
            },
        )

    def test_process_privat_empty_file(self):
        filepath = os.path.join(self.TEST_FILES_DIR, "privat_empty.xlsx")
        header = [
            "Дата",
            "Опис операції",
            "Категорія",
            "Валюта картки",
            "Сума в валюті картки",
            "Валюта транзакції",
            "Сума в валюті транзакції",
        ]
        # No data rows
        excel_data = [self.PRIVAT_DETECTION_ROW, header]
        create_excel_file(filepath, "Sheet1", excel_data)

        result = process_privat(filepath)
        self.assertEqual(result, [])

    def test_process_privat_file_no_header(self):
        filepath = os.path.join(self.TEST_FILES_DIR, "privat_no_header.xlsx")
        # The "header" that process_privat will try to read (row 2 of excel) is not the expected one.
        incorrect_header = ["Not", "a", "real", "header", "at", "all", "huh"]
        data_rows = [
            [
                "01.01.2023 10:00:00",
                "Some data",
                "Category",
                "UAH",
                -100.0,
                "UAH",
                -100.0,
            ]
        ]
        excel_data = [self.PRIVAT_DETECTION_ROW, incorrect_header] + data_rows
        create_excel_file(filepath, "Sheet1", excel_data)

        with self.assertRaises(
            KeyError
        ):  # Expecting KeyError due to missing column names like "Дата"
            process_privat(filepath)


if __name__ == "__main__":
    unittest.main()
