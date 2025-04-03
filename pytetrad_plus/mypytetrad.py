from pytetrad.tools import TetradSearch
import pytetrad.tools.translate as tr

class MyTetradSearch(TetradSearch):
    def __init__(self, *args, **kwargs):
        # Call the parent class's constructor
        super().__init__(*args, **kwargs)

    
    def load_df(self,df):
        """
        Loads a pandas DataFrame into the TetradSearch object.
        """
        self.data = tr.pandas_data_to_tetrad(df)
        return self.data