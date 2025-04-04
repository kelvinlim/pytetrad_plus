#from pytetrad.tools import TetradSearch
import pytetrad.tools.translate as tr
import pandas as pd

# Correctly import the CLASS 'TetradSearch' from WITHIN the MODULE 'TetradSearch'
try:
    from pytetrad.tools.TetradSearch import TetradSearch as TetradSearchBaseClass
    print(f"DEBUG: Successfully imported TetradSearchBaseClass, type: {type(TetradSearchBaseClass)}")
    # Optional check to be absolutely sure it's a class now
    if not isinstance(TetradSearchBaseClass, type):
        print("ERROR: Imported object is not actually a class type!")
        exit()
except ImportError:
    print("FATAL ERROR: Could not import the 'TetradSearch' class from the 'pytetrad.tools.TetradSearch' module.")
    print("Please double-check the library's structure and your installation.")
    # You might want to explore the structure if the import fails:
    # import pytetrad.tools
    # print("Contents of 'pytetrad.tools':", dir(pytetrad.tools))
    # import pytetrad.tools.TetradSearch
    # print("Contents of 'pytetrad.tools.TetradSearch':", dir(pytetrad.tools.TetradSearch))
    exit()
except Exception as e:
    print(f"FATAL: An unexpected error occurred during import: {e}")
    exit()
print(f"DEBUG: Type of imported TetradSearch: {type(TetradSearchBaseClass)}")
# Add this to see its attributes, might help identify if it's a class or module
# print(f"Attributes of TetradSearch: {dir(TetradSearch)}")

class MyTetradSearch(TetradSearchBaseClass):
    def __init__(self):

        # create a dummy dataframe to init object
        dummy_df = pd.DataFrame({
            'dummy1': [1, 2, 3, 4, 5],
            'dummy2': [5, 4, 3, 2, 1]
        })
        # Call the parent class's constructor
        # super().__init__(*args, **kwargs)
        super().__init__(dummy_df)

    
    def load_df(self,df):
        """
        Loads a pandas DataFrame into the TetradSearch object.
        """
        self.data = tr.pandas_data_to_tetrad(df)
        return self.data
    
if __name__ == "__main__":
    # Example usage of MyTetradSearch
    
    # Create an instance of MyTetradSearch
    my_tetrad_search = MyTetradSearch()

    # load a dataframe for testing
    df_file = "pytetrad_plus/boston_data.csv"
    df = pd.read_csv(df_file)
    
    if df.empty:
        print(f"Failed to load the DataFrame from {df_file}. Please check the file.")
    else:
        # Load the DataFrame into the TetradSearch object
        my_tetrad_search.load_df(df)
        print("Data loaded successfully.")