import pandas as pd


def process(input_file):
    """
    Processes a type2 XLS/XLSX file and returns a list of records,
    each record is a dict with keys: Date (yyyy/mm/dd), Details, Sum.
    """
    # First, find the header row by looking for the known header string
    df0 = pd.read_excel(input_file, header=None)
    header_name = "Дата і час здійснення операції"
    header_rows = df0.index[df0.iloc[:, 0] == header_name].tolist()
    if not header_rows:
        raise ValueError("Header row not found in type2 file")
    header_idx = header_rows[0]

    # Read the data with proper header
    df = pd.read_excel(input_file, header=header_idx)
    records = []
    for _, row in df.iterrows():
        dt_raw = row["Дата і час здійснення операції"]
        if pd.isna(dt_raw):
            continue
        # Parse date and time
        dt = pd.to_datetime(dt_raw, dayfirst=False)
        date_str = dt.strftime("%Y/%m/%d")
        time_str = dt.strftime("%H:%M:%S")

        # Parse main text and category from 'Деталі операції'
        raw_det = str(row["Деталі операції"])
        if ":" in raw_det:
            cat, rest = raw_det.split(":", 1)
            category = cat.strip()
            main_text = rest.strip()
        else:
            category = ""
            main_text = raw_det

        details = main_text
        if category:
            details += f" <{category}>"
        details += f" {time_str}"

        # Currency conversion info if Валюта exists
        curr = row.get("Валюта")
        if pd.notna(curr) and str(curr).strip() != "UAH":
            sum_oper = float(row["Сума у валюті операції"])
            sum_acc = float(row["Сума у валюті рахунку"])
            rate = sum_acc / sum_oper if sum_oper != 0 else 0
            details += f" ({sum_oper:.2f} {curr} @ {rate:.2f})"

        # Cashback info if present
        cashback = row.get("Сума кешбеку")
        if pd.notna(cashback) and float(cashback) != 0:
            details += f" [cashback {float(cashback):.2f}]"

        # Sum logic
        sum_value = float(row["Сума у валюті рахунку"])
        if category in ("Повернення", "Поповнення", "Кешбек"):
            out_sum = sum_value
        else:
            out_sum = -abs(sum_value)
        sum_str = f"{out_sum:.2f}"

        records.append({"Date": date_str, "Details": details, "Sum": sum_str})

    return records
