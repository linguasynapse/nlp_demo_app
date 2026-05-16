# Improved version using json.dump() for perfect escaping
import pandas as pd
from pathlib import Path
import json

INPUT_XLSX = Path("i18n_strings.xlsx")
OUTPUT_PY = Path("i18n/strings.py")
SHEET_NAME = "strings"

def main():
    df = pd.read_excel(
        INPUT_XLSX, 
        sheet_name=SHEET_NAME, 
        dtype=str,
        keep_default_na=False,
        engine='openpyxl'  # Explicit engine
    )
    
    df = df.fillna('')
    
    required_cols = {"key", "context"}
    lang_cols = [c for c in df.columns if c not in required_cols]

    if not lang_cols:
        raise RuntimeError("No language columns found")

    strings = {}

    for lang in lang_cols:
        strings[lang] = {}

        for _, row in df.iterrows():
            key = str(row["key"]).strip()
            value = row.get(lang, "")

            if not key or key == "nan" or key == "":
                continue

            if value and str(value).strip():
                # Normalize line breaks
                value_str = str(value)
                value_str = value_str.replace('\r\n', '\n').replace('\r', '\n')
                strings[lang][key] = value_str

    OUTPUT_PY.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PY, "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# AUTO-GENERATED FILE — DO NOT EDIT\n")
        f.write("# Source: i18n_strings.xlsx\n\n")
        f.write("STRINGS = ")
        
        # This one line replaces all the manual escaping!
        json.dump(strings, f, indent=4, ensure_ascii=False)
        
        # Add trailing newline for clean file
        f.write("\n")

    print(f"✔ strings.py generated ({len(lang_cols)} languages)")
    print(f"  Total keys: {sum(len(v) for v in strings.values())}")

if __name__ == "__main__":
    main()