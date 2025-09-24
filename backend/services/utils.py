import os
from backend.global_variables import DATA_PATH
import pandas as pd

def open_csv_data(file_name):
    if os.path.exists(DATA_PATH + file_name):
        return pd.read_csv(DATA_PATH + file_name)
    else:
        return pd.DataFrame()