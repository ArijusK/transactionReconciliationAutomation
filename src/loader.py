import pandas as pd

def load_transactions(file_path):
    try: 
        return pd.read_csv(file_path)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Transaction file not found: {file_path}"
        )

    except pd.errors.EmptyDataError:
        raise ValueError(
            f"Transaction file is empty: {file_path}"
        )