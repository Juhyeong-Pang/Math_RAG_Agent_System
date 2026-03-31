import os
import re
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def clean_latex_and_fractions(text):
    if not isinstance(text, str):
        return text

    def frac_to_decimal(match):
        num = float(match.group(1))
        den = float(match.group(2))
        return str(round(num / den, 3))

    text = re.sub(r"\\frac\{(\d+)\}\{(\d+)\}", frac_to_decimal, text)

    text = re.sub(r"\\text\{([^}]+)\}", r"\1", text)

    text = text.replace("\\", "").replace("{", "").replace("}", "")

    return text


if __name__ == "__main__":
    file_path = os.path.join("data", "test_with_answer_raw.csv")
    df = pd.read_csv(file_path)

    if "answer" in df.columns:
        df["answer"] = df["answer"].apply(clean_latex_and_fractions)

    output_path = os.path.join("data", "test_with_answer.csv")

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
