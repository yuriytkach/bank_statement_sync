# processor_privat.py
import pandas as pd


def process(input_file):
    """
    Processes a type1 XLS/XLSX file and returns a list of records,
    each record is a dict with keys: Date (yyyy/mm/dd), Details, Sum.
    """
    # Read the file, skipping the first row; header on second row (index=1)
    df = pd.read_excel(input_file, header=1)
    records = []
    for _, row in df.iterrows():
        # Skip rows without a date
        dt_raw = row["Дата"]
        if pd.isna(dt_raw):
            continue
        # Parse date and time
        dt = pd.to_datetime(dt_raw, dayfirst=True)
        date_str = dt.strftime("%Y/%m/%d")
        time_str = dt.strftime("%H:%M:%S")

        # Start building Details
        details = str(row["Опис операції"])
        category = row.get("Категорія")
        if pd.notna(category) and str(category).strip():
            details += f" <{category}>"
        details += f" {time_str}"

        # Append currency conversion info if currencies differ
        curr_card = row["Валюта картки"]
        curr_trans = row["Валюта транзакції"]
        if curr_card != curr_trans:
            sum_trans = float(row["Сума в валюті транзакції"])
            sum_card = float(row["Сума в валюті картки"])
            rate = abs(sum_card) / sum_trans if sum_trans != 0 else 0
            details += f" ({sum_trans:.2f} {curr_trans} @ {rate:.2f})"

        # Prepare Sum field (with sign, 2 decimals)
        sum_value = float(row["Сума в валюті картки"])
        sum_str = f"{sum_value:.2f}"

        records.append({"Date": date_str, "Details": details, "Sum": sum_str})

    return records
