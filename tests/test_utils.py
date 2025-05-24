import pandas as pd


def create_excel_file(filepath: str, sheet_name: str, data: list[list]):
    """
    Creates an Excel (XLSX) file at the given filepath with the given sheet_name and writes the data into it.

    Args:
        filepath: The path where the Excel file will be created.
        sheet_name: The name of the sheet within the Excel file.
        data: A list of lists representing rows of data.
    """
    try:
        df = pd.DataFrame(data)
        df.to_excel(
            filepath, sheet_name=sheet_name, index=False, header=False
        )  # Added header=False
        print(f"Excel file created successfully at {filepath}")
    except Exception as e:
        print(f"Error creating Excel file: {e}")
