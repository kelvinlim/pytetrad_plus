
from pytetrad_plus import MyTetradSearch

import pandas as pd

import semopy

from dgraph_flex import DgraphFlex

obj = DgraphFlex()
# add edges to graph object
obj.add_edge('A', '-->', 'B', color='green', strength=-0.5, pvalue=0.01)
obj.add_edge('B', '-->', 'C', color='red', strength=-.5, pvalue=0.001)
obj.add_edge('C', '-->', 'E', color='green', strength=0.5, pvalue=0.005)
obj.add_edge('D', 'o-o', 'B')
# load into graphviz object and render to window
obj.show_graph()


from pytetrad_plus import MyTetradSearch
import pprint

ts = MyTetradSearch()

# read data
df = ts.read_csv(f'HINF5660 2025 extra credit data.csv')




searchResult = ts.run_model_search(df, model='gfci',
                                                    #knowledge=knowledge,
                                                    score={'sem_bic': {'penalty_discount': 1.0}},
                                                    test={'fisher_z': {'alpha': .05}})

edges = list(searchResult['setEdges'])
pprint.pprint(edges)

from dgraph_flex import DgraphFlex
# create graph output
obj = DgraphFlex()
# add edges to graph object
for edge in edges:
  source,edge_type, target = edge.split(' ')
  obj.add_edge(source,edge_type, target, color='black')

obj.show_graph()

# %%
# run the sem
import semopy

lavaan_model = ts.edges_to_lavaan(searchResult['setEdges'])
    
# run semopy
sem_results = ts.run_semopy(lavaan_model, df)
    
# plot into png
png_path = 'extra_credit.png'

# create the semopy package graph
g = semopy.semplot(sem_results['model'], png_path,  plot_covs = True)

pass

# %%
# see results
sem_results['estimates']

# %%
def add_sem_results_to_graph(obj, df, format: bool = True):
    """
    Add the semopy results to the graph object.
    Args:
        obj (DgraphFlex): The graph object to add the results to.
        df (pd.DataFrame): The semopy results dataframe.
        format (bool): Whether to format the estimates or not. Defaults to True.
    
    """
    # iterate over the estimates id the df semopy output
    # and add them to the graph object

    # iterate over the estimates and add them to the graph
    # object
    
    for index, row in df.iterrows():
        if row['op'] == '~':
            source = row['rval']
            target = row['lval']
            estimate = row['Estimate']
            pvalue = row['p-value']
            # modify the edge in the existing graph obj
            # set the color based on the sign of estimate, green for positive, red for negative
            color = 'green' if estimate > 0 else 'red'
            
            obj.modify_existing_edge(source, target, color=color, strength=estimate, pvalue=pvalue)
            pass

ts.add_sem_results_to_graph(obj, sem_results['estimates'])
obj.save_graph(plot_format='png', plot_name='extra_credit_sem',res=96)


