import os
import re

import pandas as pd

df = pd.read_csv(os.path.join("data", "test.csv"))


def extract_answer(text):
    match = re.search(r"\\boxed\{(.+?)\}", str(text))
    if match:
        return match.group(1)
    return None


df["answer"] = df["solution"].apply(extract_answer)

print(df[["solution", "answer"]].head())
df.to_csv("test_with_answer.csv", index=False)
