#from pytetrad.tools import TetradSearch

import json
import os
from pathlib import Path
import socket

from dotenv import load_dotenv

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

import re
import pytetrad.tools.translate as tr
import pandas as pd
import semopy



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

    
    def load_df(self,df):
        """
        Loads a pandas DataFrame into the TetradSearch object.
        """
        self.data = tr.pandas_data_to_tetrad(df)
        return self.data

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
                 'stats': stats})
        
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
        ts.load_df(df)
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