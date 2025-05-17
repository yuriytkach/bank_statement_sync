import csv


def write_csv(records, output_file):
    """
    Writes a list of records to CSV.
    Each record must be a dict with keys: 'Date', 'Details', 'Sum'.
    """
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Details", "Sum"])
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)
