import pandas as pd

def load_transactions(file_path):
    return pd.read_csv(file_path)