#!/usr/bin/env python3

import argparse
import logging
import os
import sys

# Import modules for structure detection and processing
from structure_detector import detect_structure
from processor_privat import process as process_privat
from processor_raif import process as process_raif
from output import write_csv


def main():
    parser = argparse.ArgumentParser(
        description="Process XLS/XLSX file and output CSV with Date, Details, and Sum columns."
    )
    parser.add_argument("input_file", help="Path to the input XLS or XLSX file")
    args = parser.parse_args()

    input_file = args.input_file
    # Check that the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Detect the structure of the input file (privat or raif)
    try:
        structure = detect_structure(input_file)
    except Exception as e:
        print(f"Error detecting structure: {e}", file=sys.stderr)
        sys.exit(1)

    # Process the file according to its detected structure
    if structure == "privat":
        records = process_privat(input_file)
    elif structure == "raif":
        records = process_raif(input_file)
    else:
        print(f"Unknown structure '{structure}'.", file=sys.stderr)
        sys.exit(1)

    # Build output CSV path by replacing the extension
    base_name, _ = os.path.splitext(input_file)
    output_file = base_name + ".csv"

    # Write out the CSV
    try:
        write_csv(records, output_file)
    except Exception as e:
        print(f"Error writing CSV: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully wrote output to '{output_file}'")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout,
    )
    main()
