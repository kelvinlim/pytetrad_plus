#! /usr/bin/env python3
"""
try_mypytetrad.py
======================
This script is used to test the mypytetrad package. 
It can be used to  check if the package is 
installed correctly and can be run directly.


"""
import json
import sys

from pytetrad_plus import MyTetradSearch

import pandas as pd

import semopy

if __name__ == "__main__":

    # Create an instance of MyTetradSearch
    ts = MyTetradSearch()

    # load a dataframe for testing
    df_file = "pytetrad_plus/boston_data_raw.csv"
    df = ts.read_csv(df_file)
    if df.empty:
        print(f"Failed to load the DataFrame from {df_file}. Please check the file.")
        sys.exit(1)
        
    # add the lag columns
    df_lag = ts.add_lag_columns(df, lag_stub='_lag')
    # standardize the data
    df_lag_std = ts.standardize_df_cols(df_lag)
    
    print(f"DataFrame loaded and lag columns added, columns standardized. Number of rows: {len(df_lag)}")
    
    # read the prior file for testing
    prior_lines = ts.read_prior_file('pytetrad_plus/boston_prior.txt')
    # extract knowledge from the prior lines
    knowledge = ts.extract_knowledge(prior_lines)
    
    ## Run the search
    searchResult = ts.run_model_search(df_lag_std, model='gfci', 
                                            knowledge=knowledge, 
                                            score={'sem_bic': {'penalty_discount': 1.0}},
                                            test={'fisher_z': {'alpha': .05}})
    
    
    lavaan_model = ts.edges_to_lavaan(searchResult['setEdges'])
    
    # run semopy
    sem_results = ts.run_semopy(lavaan_model, df_lag_std)
    
    # plot into png
    png_path = 'pytetrad_plus/boston_data.png'
    g = semopy.semplot(sem_results['model'], png_path,  plot_covs = True)

    # get the estmates
    estimates_sem = sem_results['estimates']
    
    # summary of the estimates
    estimates = ts.summarize_estimates(estimates_sem)
    
    result = {  'setEdges': list(searchResult['setEdges']), 
                'ESMean': estimates['mean_abs_estimates'],
                'ESStd': estimates['std_abs_estimates'],
                'estimatesSEM': sem_results['estimatesDict']
                } 
 
    # write the result to a json file
    with open('pytetrad_plus/boston_result.json','w') as f:
        json.dump(result, f, indent=4)
        
        
    # do the stability analysis
    # run the stability search
    stable_edges, sorted_edges = ts.run_stability_search(df, model='gfci',
                                            knowledge=knowledge,
                                            score={'sem_bic': {'penalty_discount': 1.0}},
                                            test={'fisher_z': {'alpha': .05}},
                                            runs=100,
                                            min_fraction=0.75,
                                            subsample_fraction=0.9)

    lavaan_model = ts.edges_to_lavaan(stable_edges)
    
    # run semopy, using the lagged and standardized data
    sem_results = ts.run_semopy(lavaan_model, df_lag_std)
    
    # plot into png
    png_path = 'pytetrad_plus/boston_data_stability.png'
    g = semopy.semplot(sem_results['model'], png_path,  plot_covs = True)

    # get the estimates
    estimates_sem = sem_results['estimates']
    
    # summary of the estimates
    estimates = ts.summarize_estimates(estimates_sem)
    
    result = {  'setEdges': stable_edges, 
                'ESMean': estimates['mean_abs_estimates'],
                'ESStd': estimates['std_abs_estimates'],
                'estimatesSEM': sem_results['estimatesDict']
                } 
 
    # write the result to a json file
    with open('pytetrad_plus/boston_result_stability.json','w') as f:
        json.dump(result, f, indent=4)
        


    print("Stability analysis results saved to boston_result_stability.json")
    
    
    # run permutation
    # create 100 permutations
    permuted_dfs = ts.create_permuted_dfs(df, n_permutations=100)
    # run the search on each permutation
    permuted_results = []
    
    # range of penalty_discount values
    penalty_discount_values = [1.0,2,3,4,5,6,7,8,9,10]
    # iterate over the penalty_discount values
    for penalty_discount in penalty_discount_values:
        # iterate over the permuted dataframes
        for permuted_df in permuted_dfs:
            
            # add lag columns
            permuted_df_lag = ts.add_lag_columns(permuted_df, lag_stub='_lag')
            # standardize the data
            permuted_df_lag_std = ts.standardize_df_cols(permuted_df_lag)
            # run the search
            searchResult = ts.run_model_search(permuted_df_lag_std, model='gfci', 
                                                knowledge=knowledge, 
                                                score={'sem_bic': {'penalty_discount': penalty_discount}},
                                                test={'fisher_z': {'alpha': .05}})
            # create dictionary for result to include penalty_discount
            info = {
                'penaltyDiscount': penalty_discount,
                'numEdges': len(searchResult['setEdges']),
                'edges': list(searchResult['setEdges'])
            }
            permuted_results.append(info)
        
    # save the results to a json file
    with open('pytetrad_plus/boston_permuted_results.json','w') as f:
        json.dump(permuted_results, f, indent=4)
    print("Permutation results saved to boston_permuted_results.json")
    pass