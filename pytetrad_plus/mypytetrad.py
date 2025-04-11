#! /usr/bin/env python3

#from pytetrad.tools import TetradSearch

import json
import os
from pathlib import Path
import socket
from typing import Optional

from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler

# set the PATH if needed
hostname = socket.gethostname()
home_directory = Path.home()
# check if .javaenv.txt file exists
javaenv_path = os.path.join(home_directory, '.javarc')
if os.path.exists(javaenv_path):
    # load the file
    load_dotenv(dotenv_path=javaenv_path)
    java_home = os.environ.get("JAVA_HOME")
    java_path = f"{java_home}/bin"
    current_path = os.environ.get('PATH')
    # add this to PATH
    os.environ['PATH'] = f"{current_path}{os.pathsep}{java_path}"

    # add to path
    graphviz_bin = os.environ.get("GRAPHVIZ_BIN")
    os.environ['PATH'] = f"{current_path}{os.pathsep}{graphviz_bin}"

    pass

elif 'c30' in hostname:
    java_home = "R:/DVBIC/jdk21.0.4_7"
    # init JAVA_HOME
    os.environ['JAVA_HOME'] = java_home
    java_path = f"{java_home}/bin"
    current_path = os.environ.get('PATH')
    # add this to PATH
    os.environ['PATH'] = f"{current_path}{os.pathsep}{java_path}"
    pass

import graphviz
import re
import pytetrad.tools.translate as tr
import pandas as pd
import semopy

__version_info__ = ('0', '2', '2')
__version__ = '.'.join(__version_info__)

version_history = \
"""
0.2.2 - generate semopy plot
0.2.1 - add subsample_df and reading in csv
0.2.0 - add reading of .javarc for JAVA_HOME
0.1.2 - reworked data file paths
0.1.1 - refactored to generalize operations with run_model_search
0.1.0 - initial version  
"""

# Correctly import the CLASS 'TetradSearch' from WITHIN the MODULE 'TetradSearch'
try:
    from pytetrad.tools.TetradSearch import TetradSearch as TetradSearchBaseClass
    #print(f"DEBUG: Successfully imported TetradSearchBaseClass, type: {type(TetradSearchBaseClass)}")
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
#print(f"DEBUG: Type of imported TetradSearch: {type(TetradSearchBaseClass)}")
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

    def read_csv(self, file_path: str) -> pd.DataFrame:
        """Read a CSV file and return a pandas DataFrame.
        Args:
            file_path (str): Path to the CSV file.

        Returns:
            pd.DataFrame: pandas DataFrame
        """
        self.full_df = pd.read_csv(file_path)
        return self.full_df

    def add_lag_columns(self, df: pd.DataFrame, lag_stub='_') -> pd.DataFrame:
        """
        Lag the dataframe by shifting the columns by one row

        Args:
            df (pd.DataFrame): the dataframe to lag
            lag_stub (str): the string to append to the column names for the lagged variables

        Returns:
            pd.DataFrame: the lagged dataframe
        """
        
        # create a copy of the dataframe
        df_lag = df.copy()
        
        # create additional columns for the lagged variables, naming them  lagdrinks, lagsad, etc.
        cols_to_lag = df.columns.tolist()
        # shift by one row
        for col in cols_to_lag:
            df_lag[f'{col}{lag_stub}'] = df[col].shift(1)
        
        # drop the first row
        df_lag = df_lag.dropna()
        
        # reset index
        df_lag = df_lag.reset_index(drop=True)
        
        return df_lag
    
    def load_df_into_ts(self,df):
        """
        Loads a pandas DataFrame into the TetradSearch object.
        """
        self.data = tr.pandas_data_to_tetrad(df)
        return self.data
    
    def subsample_df(self, df: Optional[pd.DataFrame] = None,    
                    fraction: float = 0.9,
                    random_state: Optional[int] = None) -> pd.DataFrame:
        """
        Randomly subsample the DataFrame to a fraction of rows
        Args:
            df - pandas DataFrame
            fraction - proportion of rows to keep, default 0.9
            random_state - random state for reproducibility
        Returns:
            df - pandas DataFrame
        """
        if df is None:
            if hasattr(self, 'full_df') and self.full_df is not None:
                df = self.full_df
            else:
                raise ValueError("DataFrame must be provided.")
        if fraction <= 0 or fraction > 1:
            raise ValueError(f"fraction must be between 0 and 1")
        
        # Use the DataFrame's built-in sample method with the specified fraction
        # The `random_state` parameter ensures reproducibility if an integer is provided
        scrambled_df = df.sample(frac=fraction, random_state=random_state)

        # Step 2: Sort the sampled DataFrame by its original index
        # This restores the original relative order of the kept rows
        self.subsampled_df = scrambled_df.sort_index()
        
        return self.subsampled_df

    def standardize_df_cols(self, df, diag=False):
        """
        standardize the columns in the dataframe
        https://machinelearningmastery.com/normalize-standardize-machine-learning-data-weka/
        
        * get the column names for the dataframe
        * convert the dataframe into  a numeric array
        * scale the data
        * convert array back to a df
        * add back the column names
        * set to the previous df
        """
        
        # describe original data - first two columns
        if diag:
            print(df.iloc[:,0:2].describe())
        # get column names
        colnames = df.columns
        # convert dataframe to array
        data = df.values
        # standardize the data
        std_data = StandardScaler().fit_transform(data)
        # convert array back to df, use original colnames
        newdf = pd.DataFrame(std_data, columns = colnames)
        # describe new data - first two columns
        if diag:
            print(newdf.iloc[:,0:2].describe())
        
        return newdf
    
    def run_stability_search(self, full_df: pd.DataFrame,
                            model: str = 'gfci',
                            knowledge: Optional[dict] = None,
                            score = {'sem_bic': {'penalty_discount': 1.0}},
                            test ={'fisher_z': {'alpha': .05}},
                            runs: int = 100,
                            min_fraction: float= 0.75,
                            subsample_fraction: float = 0.9,
                            random_state: Optional[int] = None,
                            lag_flag = True) -> list:
        """
        Run a stability search on the DataFrame using the specified model.
        
        Edges are tabluated for each run using a set.
        Edges that are present for a minimum of min_fraction of runs will be retained
        and returned.
        The edges are returned as a list of strings.
        
        Args:
            df: pd.DataFrame - the DataFrame to perform the stability search on
            model: str - the model to use for the search
            knowledge: Optional[dict] - additional knowledge to inform the search
            score: dict - scoring parameters
            test: dict - testing parameters
            runs: int - number of runs to perform
            min_fraction: float - minimum fraction of runs an edge must appear in to be retained
            subsample_fraction: float - fraction of data to subsample for each run
            random_state: Optional[int] - random state for reproducibility
            lag_flag: - if True, add lagged columns to the DataFrame
        Returns:
            list - list with the results
        """

        # dictionary where key is the edge and value is the number of times it was found
        edge_counts = {}
        
        # loop over the number of runs
        for i in range(runs):
            # subsample the DataFrame
            df = self.subsample_df(full_df, fraction=subsample_fraction, random_state=random_state)
            
            # check if lag_flag is True
            if lag_flag:
                # add lagged columns
                df = self.add_lag_columns(df, lag_stub='_lag')
                
            # standardize the data
            df = self.standardize_df_cols(df)
                
            # run the search
            searchResult = self.run_model_search(df, model=model, 
                                                knowledge=knowledge, 
                                                score=score,
                                                test=test)
            # get the edges
            edges = searchResult['setEdges']
            # loop over the edges
            for edge in edges:
                edge_counts[edge] = edge_counts.get(edge, 0) + 1

            pass
        # check similarity of edges, sort alphabetically
        # get all the keys and then sort them
        sorted_edge_keys = sorted(edge_counts.keys())
        
        sorted_edge_counts = {}
        # loop over the sorted keys and store the fractional count 
        for edge in sorted_edge_keys:
            sorted_edge_counts[edge] = edge_counts[edge]/runs
            
        # loop over the edges and keep only those that are present in at least min_fraction of runs
        min_count = int(runs * min_fraction)
        stable_edges = [edge for edge, count in edge_counts.items() if count >= min_count]
        # return the edges
        return stable_edges, sorted_edge_counts
    
    

    def read_prior_file(self, prior_file) -> list:
        """
        Read a prior file and return the contents as a list of strings
        Args:
            prior_file - string with the path to the prior file
            
        Returns:
            list - list of strings representing the contents of the prior file
        """
        if not os.path.exists(prior_file):
            raise FileNotFoundError(f"Prior file {prior_file} not found.")
        
        with open(prior_file, 'r') as f:
            self.prior_lines = f.readlines()
        
        return self.prior_lines

    def extract_knowledge(self, prior_lines) -> dict:
        """
        returns the knowledge from the prior file
        Args:
            prior_lines - list of strings representing the lines in the prior file
        Returns:
            dict - a dictionary where keys are
                addtemporal, forbiddirect, requiredirect
                 
                For addtemporal is a dictionary where the keys are the tier numbers (0 based) and 
                values are lists of the nodes in that tier.

                For forbiddirect and requiredirect, they will be empty in this case as this method is only for addtemporal.
        """
        tiers = {}
        inAddTemporal = False
        stop = False
        for line in prior_lines:
            # find the addtemporal line
            if line.startswith('addtemporal'):
                inAddTemporal = True
                continue
            # find the end of the addtemporal block
            if inAddTemporal and (line.startswith('\n') or line.startswith('forbiddirect')):
                inAddTemporal = False
                continue
            if inAddTemporal:
                # expect 1 binge_lag vomit_lag panasneg_lag panaspos_lag pomsah_lag

                # split the line
                line = line.strip()
                items = line.split()

                # add to dictionary
                if len(items) != 0:
                    tiers[int(items[0])-1] = items[1:]

        knowledge = {
            'addtemporal': tiers
        }

        return knowledge   

    def load_knowledge(self, knowledge:dict):
        """
        Load the knowledge
        
        The standard prior.txt file looks like this:
        
        /knowledge

        addtemporal
        1 Q2_exer_intensity_ Q3_exer_min_ Q2_sleep_hours_ PANAS_PA_ PANAS_NA_ stressed_ Span3meanSec_ Span3meanAccuracy_ Span4meanSec_ Span4meanAccuracy_ Span5meanSec_ Span5meanAccuracy_ TrailsATotalSec_ TrailsAErrors_ TrailsBTotalSec_ TrailsBErrors_ COV_neuro_ COV_pain_ COV_cardio_ COV_psych_
        2 Q2_exer_intensity Q3_exer_min Q2_sleep_hours PANAS_PA PANAS_NA stressed Span3meanSec Span3meanAccuracy Span4meanSec Span4meanAccuracy Span5meanSec Span5meanAccuracy TrailsATotalSec TrailsAErrors TrailsBTotalSec TrailsBErrors COV_neuro COV_pain COV_cardio COV_psych

        forbiddirect

        requiredirect
        
        The input dict will have the keys of addtemporal, forbiddirect, requiredirect
        
        For the addtemporal key, the value will be another dict with the keys of 1, 2, 3, etc.
        representing the tiers. The values will be a list of the nodes in that tier.
        
        Args:
        search - search object
        knowledge - dictionary with the knowledge
        
        """
        
        # check if addtemporal is in the knowledge dict
        if 'addtemporal' in knowledge:
            tiers = knowledge['addtemporal']
            for tier, nodes in tiers.items():
                # tier is a number, tetrad uses 0 based indexing so subtract 1
                for node in nodes:
                    self.add_to_tier(tier, node)
                    pass

        # if there are other knowledge types, load them here
        pass

    def extract_edges(self, text):
        """
        Extract out the edges between Graph Edges and Graph Attributes
        """
        edges = set()
        nodes = set()
        pairs = set()  # alphabetical order of nodes of an edge
        # get the lines
        lines = text.split('\n')
        startFlag=False  # True when we are in the edges, False when not
        for line in lines:
            # check if line begins with a number and period
            # convert line to python string
            line = str(line)
            if re.match(r"^\d+\.", line):
            # if startFlag == False:
            #     if "Graph Edges:" in line:
            #         startFlag = True
            #         continue  # continue to next line
            # if startFlag == True:
                # # check if there is edge information a '--'
                # if '-' in line:
                    # this is an edge so add to the set
                    # strip out the number in front  1. drinks --> happy
                    # convert to a string
                    linestr = str(line)
                    clean_edge = linestr.split('. ')[1]
                    edges.add(clean_edge)
                    
                    # add nodes
                    nodeA = clean_edge.split(' ')[0]
                    nodes.add(nodeA)
                    nodeB = clean_edge.split(' ')[2]
                    nodes.add(nodeB)
                    combined_string = ''.join(sorted([nodeA, nodeB]))
                    pairs.add(combined_string)
                    pass
        return edges, nodes, pairs   

    def summarize_estimates(self, df):
        """
        Summarize the estimates
        """
        # get the Estimate column from the df 
        estimates = df['Estimate']       
        # get the absolute value of the estimates
        abs_estimates = estimates.abs()
        # get the mean of the absolute values
        mean_abs_estimates = abs_estimates.mean()
        # get the standard deviation of the absolute values
        std_abs_estimates = abs_estimates.std()
        return {'mean_abs_estimates': mean_abs_estimates, 'std_abs_estimates': std_abs_estimates}
        
    def edges_to_lavaan(self, edges, exclude_edges = ['---','<->','o-o']):
        """
        Convert edges to a lavaan string
        """
        lavaan_model = ""
        for edge in edges:
            nodeA = edge.split(' ')[0]
            nodeB = edge.split(' ')[2]
            edge_type = edge.split(' ')[1]
            if edge_type in exclude_edges:
                continue
            # remember that for lavaan, target ~ source
            lavaan_model += f"{nodeB} ~ {nodeA}\n"
        return lavaan_model
    
    def run_semopy(self, lavaan_model, data):  
        
        """
        run sem using semopy package
        
        lavaan_model - string with lavaan model
        data - pandas df with data
        """
        
        # create a sem model   
        model = semopy.Model(lavaan_model)

        ## TODO - check if there is a usable model,
        ## for proj_dyscross2/config_v2.yaml - no direct edges!
        ## TODO - also delete output files before writing to them so that
        ## we don't have hold overs from prior runs.
        opt_res = model.fit(data)
        estimates = model.inspect()
        stats = semopy.calc_stats(model)
        
        # change column names lval to dest and rval to src
        estimatesRenamed = estimates.rename(columns={'lval': 'dest', 'rval': 'src'})
        # convert the estimates to a dict using records
        estimatesDict = estimatesRenamed.to_dict(orient='records')        

        return ({'opt_res': opt_res,
                 'estimates': estimates, 
                 'estimatesDict': estimatesDict,
                 'stats': stats,
                 'model': model})
        
    # def run_model_search(self, df, model='gfci', 
    #                      knowledge=None, 
    #                      score=None,
    #                      test=None):
    def run_model_search(self, df, **kwargs):
        """
        Run a search
        
        Args:
        df - pandas dataframe
        
        kwargs:
        model - string with the model to use, default gfci
        knowledge - dictionary with the knowledge
        score - dictionary with the arguments for the score
            e.g. {"sem_bic": {"penalty_discount": 1}}
            
        test - dictionary with the arguments for the test alpha 
        
        Returns:
        result - dictionary with the results
        """
    
        model = kwargs.get('model', 'gfci')
        knowledge = kwargs.get('knowledge', None)
        score = kwargs.get('score', None)
        test = kwargs.get('test', None)
        depth = kwargs.get('depth', -1)
        
        # load the data into the TetradSearch object
        self.load_df_into_ts(df)
        
        # check if score is not None
        if score is not None:  
            ## Use a SEM BIC score
            if 'sem_bic' in score:
                penalty_discount = score['sem_bic']['penalty_discount']
                res =self.use_sem_bic(penalty_discount=penalty_discount)
                
        if test is not None:
            if 'fisher_z' in test:
                alpha = test['fisher_z'].get('alpha',.01)
                self.use_fisher_z(alpha=alpha)
            
        # check if depth is not None
        if depth != -1:
            self.set_depth(depth)
            
        if knowledge is not None:
            self.load_knowledge(knowledge)
        
        ## Run the selected search
        if model == 'fges':
            x = self.run_fges()
        elif model == 'gfci':   
            x = self.run_gfci(max_degree=1000,
                              complete_rule_set_used=False)
            

        soutput = self.get_string()
        setEdges, setNodes, setPairs = self.extract_edges(soutput)
        
        result = {'setEdges': setEdges, 
                  'setNodes': setNodes, 
                  'setPairs': setPairs,
                  'raw_output': soutput
                  } 
        
        return result

if __name__ == "__main__":
    # Example usage of MyTetradSearch
    


    # Create an instance of MyTetradSearch
    ts = MyTetradSearch()

    # load a dataframe for testing
    df_file = "pytetrad_plus/boston_data.csv"
    df = pd.read_csv(df_file)
    
    if df.empty:
        print(f"Failed to load the DataFrame from {df_file}. Please check the file.")
    else:
        # Load the DataFrame into the TetradSearch object
        ts.load_df_into_ts(df)
        print("Data loaded successfully.")

    # read the prior file for testing
    prior_lines = ts.read_prior_file('pytetrad_plus/boston_prior.txt')
    # extract knowledge from the prior lines
    knowledge = ts.extract_knowledge(prior_lines)
    # load the knowledge into the TetradSearch object
    ts.load_knowledge(knowledge)


    ## Run the search
    searchResult = ts.run_model_search(df, model='gfci', 
                                            knowledge=knowledge, 
                                            score={'sem_bic': {'penalty_discount': 1.0}},
                                            test={'fisher_z': {'alpha': .05}})
    
    
  
    
    lavaan_model = ts.edges_to_lavaan(searchResult['setEdges'])
    
    # run semopy
    sem_results = ts.run_semopy(lavaan_model, df)
    
    # plot into png
    png_path = 'pytetrad_plus/boston_data.png'
    g = semopy.semplot(sem_results['model'], png_path,  plot_covs = True)

    # get the estmates
    estimates_sem = sem_results['estimates']
    
    # summary of the estimates
    estimates = ts.summarize_estimates(estimates_sem)
    
    result = {'setEdges': list(searchResult['setEdges']), 
                'setNodes': list(searchResult['setNodes']), 
                'setPairs': list(searchResult['setPairs']), 
                'ESMean': estimates['mean_abs_estimates'],
                'ESStd': estimates['std_abs_estimates'],
                'estimatesSEM': sem_results['estimatesDict']
                } 
 
    # write the result to a json file
    with open('pytetrad_plus/boston_result.json','w') as f:
        json.dump(result, f, indent=4)
    pass  # assign the method for testing