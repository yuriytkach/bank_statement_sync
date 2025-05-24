import unittest
import os
import pandas as pd  # Though not directly used in tests, processor_raif uses it.
from processor_raif import process as process_raif
from tests.test_utils import create_excel_file


class TestProcessorRaif(unittest.TestCase):
    TEST_FILES_DIR = "test_files"
    RAIF_HEADER_KEY = "Дата і час здійснення операції"

    def setUp(self):
        os.makedirs(self.TEST_FILES_DIR, exist_ok=True)

    def tearDown(self):
        for filename in os.listdir(self.TEST_FILES_DIR):
            os.remove(os.path.join(self.TEST_FILES_DIR, filename))
        if not os.listdir(self.TEST_FILES_DIR):
            os.rmdir(self.TEST_FILES_DIR)

    def _create_raif_excel(
        self,
        file_name: str,
        header_location_data: list[list],
        actual_header_row: list[str],
        data_rows: list[list],
    ) -> str:
        full_sheet_data = (
            header_location_data
            + ([actual_header_row] if actual_header_row else [])
            + data_rows
        )
        filepath = os.path.join(self.TEST_FILES_DIR, file_name)
        create_excel_file(filepath, "Sheet1", full_sheet_data)
        return filepath

    def test_process_raif_typical_file(self):
        header_location_data = [["АТ «Райффайзен Банк»"]]
        actual_header = [
            self.RAIF_HEADER_KEY,
            "Деталі операції",
            "Сума у валюті операції",
            "Валюта",
            "Сума у валюті рахунку",
            "Сума кешбеку",
        ]
        # Dates are mm/dd/yyyy to match processor_raif's dayfirst=False
        data_rows = [
            ["01/13/2023 10:15:00", "Покупка: Groceries", 150.00, "UAH", 150.00, 0],
            [
                "02/14/2023 12:00:00",
                "Повернення: Refund for item",
                50.00,
                "UAH",
                50.00,
                0,
            ],
            [
                "03/15/2023 14:30:00",
                "Оплата послуг: Internet",
                200.00,
                "UAH",
                200.00,
                2.00,
            ],
            [
                "04/16/2023 16:45:00",
                "Переказ коштів: Transfer to friend",
                1000.00,
                "UAH",
                1000.00,
                0,
            ],
            [None, "Should be skipped", 10.0, "UAH", 10.0, 0],
            [
                "05/17/2023 18:00:00",
                "Покупка: Coffee Shop : With Sub Category",
                75.00,
                "EUR",
                3000.00,
                0,
            ],
        ]
        filepath = self._create_raif_excel(
            "raif_typical.xlsx", header_location_data, actual_header, data_rows
        )

        result = process_raif(filepath)

        self.assertEqual(len(result), 5)
        self.assertEqual(
            result[0],
            {
                "Date": "2023/01/13",
                "Details": "Groceries <Покупка> 10:15:00",
                "Sum": "-150.00",
            },
        )
        self.assertEqual(
            result[1],
            {
                "Date": "2023/02/14",
                "Details": "Refund for item <Повернення> 12:00:00",
                "Sum": "50.00",
            },
        )
        self.assertEqual(
            result[2],
            {
                "Date": "2023/03/15",
                "Details": "Internet <Оплата послуг> 14:30:00 [cashback 2.00]",
                "Sum": "-200.00",
            },
        )
        self.assertEqual(
            result[3],
            {
                "Date": "2023/04/16",
                "Details": "Transfer to friend <Переказ коштів> 16:45:00",
                "Sum": "-1000.00",
            },
        )
        # Rate: 3000.00 / 75.00 = 40.00
        self.assertEqual(
            result[4],
            {
                "Date": "2023/05/17",
                "Details": "Coffee Shop : With Sub Category <Покупка> 18:00:00 (75.00 EUR @ 40.00)",
                "Sum": "-3000.00",
            },
        )

    def test_process_raif_header_not_on_first_row(self):
        header_location_data = [
            ["АТ «Райффайзен Банк»"],
            ["Some random data"],
            ["More random data"],
        ]
        actual_header = [
            self.RAIF_HEADER_KEY,
            "Деталі операції",
            "Сума у валюті рахунку",
        ]
        data_rows = [["06/10/2023 09:00:00", "Test Purchase", 123.00]]  # mm/dd/yyyy

        filepath = self._create_raif_excel(
            "raif_header_middle.xlsx", header_location_data, actual_header, data_rows
        )
        result = process_raif(filepath)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0],
            {
                "Date": "2023/06/10",
                "Details": "Test Purchase 09:00:00",
                "Sum": "-123.00",
            },
        )

    def test_process_raif_missing_optional_columns(self):
        header_location_data = [["АТ «Райффайзен Банк»"]]
        actual_header = [
            self.RAIF_HEADER_KEY,
            "Деталі операції",
            "Сума у валюті рахунку",
        ]
        data_rows = [["07/15/2023 09:00:00", "Simple Purchase", 250.00]]  # mm/dd/yyyy

        filepath = self._create_raif_excel(
            "raif_missing_cols.xlsx", header_location_data, actual_header, data_rows
        )
        result = process_raif(filepath)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0],
            {
                "Date": "2023/07/15",
                "Details": "Simple Purchase 09:00:00",
                "Sum": "-250.00",
            },
        )

    def test_process_raif_various_transaction_types(self):
        header_location_data = [["АТ «Райффайзен Банк»"]]
        actual_header = [
            self.RAIF_HEADER_KEY,
            "Деталі операції",
            "Сума у валюті операції",
            "Валюта",
            "Сума у валюті рахунку",
            "Сума кешбеку",
        ]
        # Dates mm/dd/yyyy
        data_rows = [
            ["08/01/2023 10:00:00", "Повернення: Return", 100.00, "UAH", 100.00, 0],
            ["08/02/2023 11:00:00", "Поповнення: Deposit", 500.00, "UAH", 500.00, 0],
            [
                "08/03/2023 12:00:00",
                "Кешбек: Cashback received",
                10.00,
                "UAH",
                10.00,
                0,
            ],  # Processor takes sum from "Сума у валюті рахунку"
            ["08/04/2023 13:00:00", "Інше: Other type", 70.00, "UAH", 70.00, 0],
        ]
        filepath = self._create_raif_excel(
            "raif_transaction_types.xlsx",
            header_location_data,
            actual_header,
            data_rows,
        )
        result = process_raif(filepath)

        self.assertEqual(len(result), 4)
        self.assertEqual(
            result[0],
            {
                "Date": "2023/08/01",
                "Details": "Return <Повернення> 10:00:00",
                "Sum": "100.00",
            },
        )
        self.assertEqual(
            result[1],
            {
                "Date": "2023/08/02",
                "Details": "Deposit <Поповнення> 11:00:00",
                "Sum": "500.00",
            },
        )
        self.assertEqual(
            result[2],
            {
                "Date": "2023/08/03",
                "Details": "Cashback received <Кешбек> 12:00:00",
                "Sum": "10.00",
            },
        )
        self.assertEqual(
            result[3],
            {
                "Date": "2023/08/04",
                "Details": "Other type <Інше> 13:00:00",
                "Sum": "-70.00",
            },
        )

    def test_process_raif_empty_file_no_header_match(self):
        header_location_data = [["АТ «Райффайзен Банк»"], ["No header here really"]]
        # actual_header_row is empty or not containing RAIF_HEADER_KEY
        filepath = self._create_raif_excel(
            "raif_no_header_match.xlsx", header_location_data, [], []
        )

        with self.assertRaises(ValueError):  # Expecting ValueError if header not found
            process_raif(filepath)

    def test_process_raif_file_with_header_but_no_data(self):
        header_location_data = [["АТ «Райффайзен Банк»"]]
        actual_header = [
            self.RAIF_HEADER_KEY,
            "Деталі операції",
            "Сума у валюті рахунку",
        ]
        data_rows = []

        filepath = self._create_raif_excel(
            "raif_header_no_data.xlsx", header_location_data, actual_header, data_rows
        )
        result = process_raif(filepath)

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
