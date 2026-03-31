import json
import os
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def convert_jsons_to_csv(source_dir: str, output_file: str):
    """
    Reads all JSON files in a directory and merges them into a single CSV file.
    """
    source_path = Path(source_dir)
    json_files = list(source_path.glob("*.json"))

    data_list = []

    print(f"Starting conversion: Processing {len(json_files)} files...")

    for file_path in tqdm(json_files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                data["file_name"] = file_path.name
                data_list.append(data)
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

    df = pd.DataFrame(data_list)

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"\nConversion complete! Results saved to '{output_file}'.")
    print("Data Preview:")
    print(df.head(3))


if __name__ == "__main__":
    convert_jsons_to_csv(
        source_dir="data/MATH/test",
        output_file="data/test.csv",
    )
