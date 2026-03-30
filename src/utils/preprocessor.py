import os
import sys

import pandas as pd

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    pass
