#! /usr/bin/env python3
"""
try_mypytetrad.py
======================
This script is used to test the mypytetrad package. It can be used to quickly check if the package is installed correctly and can be run directly.
"""
import sys
from pytetrad_plus import MyTetradSearch
import pandas as pd

if __name__ == "__main__":

    # Create an instance of MyTetradSearch
    my_tetrad_search = MyTetradSearch()

    # load a dataframe for testing
    df_file = "pytetrad_plus/boston_data.csv"
    df = pd.read_csv(df_file)
    if df.empty:
        print(f"Failed to load the DataFrame from {df_file}. Please check the file.")
        sys.exit(1)
        
    # Load the DataFrame into the TetradSearch object
    my_tetrad_search.load_df(df)
    
    print("Data loaded successfully.")