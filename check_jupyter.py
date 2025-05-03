# check if in a jupyter notebook
def in_jupyter():
    try:
        # Check if the IPython module is available
        from IPython import get_ipython
        ipython = get_ipython()
        
        # Check if the current environment is a Jupyter Notebook
        if ipython is not None and 'IPKernelApp' in ipython.config:
            return True
    except ImportError:
        pass
    
    return False

# main function to test if in jupyter
if __name__ == "__main__":
    if in_jupyter():
        print("Running in a Jupyter Notebook.")
    else:
        print("Not running in a Jupyter Notebook.")
        

