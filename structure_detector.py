import pandas as pd


def detect_structure(input_file):
    """
    Detects whether the input file is privat (Privat) or raif (Raiffeisen)
    by checking the unique first-row markers.
    Returns 'privat' or 'raif'.
    """
    # Read only the first cell of the first row
    df0 = pd.read_excel(input_file, header=None, nrows=1)
    try:
        first_cell = df0.iloc[0, 0]
    except Exception as e:
        raise ValueError(f"Error reading the file: {e}")
    if isinstance(first_cell, str):
        if "Виписка з Ваших карток за період" in first_cell:
            return "privat"
        if "АТ «Райффайзен Банк»" in first_cell:
            return "raif"
    raise ValueError(f"Unknown file structure: {first_cell}")
