# Bank Statements Excel-to-CSV Converter

A command-line Python 3 tool to normalize two different bank-statement XLS/XLSX formats (Privatbank & Raiffeisen) 
into a uniform CSV with three columns:  
- **Date** (`YYYY/MM/DD`)  
- **Details** (operation description, category, time, exchange rate info, cashback)  
- **Sum** (signed, two decimals)

---

## Prerequisites

- Python 3.7+  
- `git` (optional, for source control)  

---

## 1. Create & Activate a Virtual Environment

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
````

---

## 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

# If you haven’t already:
pip install pre-commit bumpversion
```

---

## 3. Install Pre-commit Hooks

This project ships a `.pre-commit-config.yaml`. To automatically run linters and formatters on each commit:

```bash
pre-commit install
```

To run them manually:

```bash
pre-commit run --all-files
```

---

## 4. Running the Converter

```bash
python main.py path/to/input.xlsx
```

* The script will detect whether the file is in the Privatbank or Raiffeisen format, process it, and emit `input.csv` alongside your original file
* If you pass an invalid path or an unknown format, you’ll see an error message

---

## 5. Bumping the Project Version

We use [`bumpversion`](https://github.com/c4urself/bump2version) (configured in `.bumpversion.cfg`) to keep semantic versioning.

* **Patch bump** (e.g. `1.0.0` → `1.0.1`):

  ```bash
  bumpversion patch
  ```
* **Minor bump** (e.g. `1.0.1` → `1.1.0`):

  ```bash
  bumpversion minor
  ```
* **Major bump** (e.g. `1.1.0` → `2.0.0`):

  ```bash
  bumpversion major
  ```

Each run will:

1. Update the version in your config/files
2. Create a git commit and a tag (`vX.Y.Z`)

---

## License

MIT © Yuriy Tkach