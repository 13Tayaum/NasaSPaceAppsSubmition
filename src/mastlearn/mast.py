# I spent too long commenting becuase i heard this will most likely
# become opensource so yea, if anyone is using this, thank me. 
# Number of hours spent writing this file is 1
from pathlib import Path
import numpy as np # Self explanitory for arrays ofcourse
from astroquery.mast import Observations # Tool for geting mast database

INITIAL_TYPES = {
    'IMAGE', 
    'SPECTRUM', 
    'SED', 
    'TIMESERIES', 
    'CATALOG'
} # The innitial default types of data it will always query 
# (If there is more types of data that will be also queries but this is initil)
def SearchObservations(
    target:str, 
    radius_:str = '0.02 deg', 
    collections:array[] = None,
    maxObservations:int = 0
):
    '''
        A function that searches through MAST
        - target:str is the location or the name of the target 
        - radius_:str is the search raduis aroudn the target
        - collections:array[] is the names of optional missions 
          or archive collections (such as JWST etc.)
        - maxObservations:int is the maximum number of returned 
          observations
    '''
    # First we will query Mast for observations
    observations = Observations.query_object(target, radius=radius) 
    # Now we will check if there ar eany observations if not we raise an error
    if len(observations) == 0:
        raise ValueError(f"No MAST observations found for {target}.")
    # Next we need to filter all observations if the collection is specified
    if collections:
        allowed = {str(value).upper() for value in collections}
        actual = np.asarray(observations["obs_collection"], dtype=str)
        keep = np.isin(np.char.upper(actual), list(allowed))
        observations = observations[keep]
    # We finally return all the observations
    return observations[:max_observations]
# Next we will impliment the function that atcually retrives the database
def GetProducts(observations:array[str]):
    '''
        This function actually retrieves the data producst regarding the 
        observation, one observation can have multiple product data
        - observations:array[str] is the teh observatio 
    '''
    # We first need to ensure that there are observations
    if len(observations) == 0:
        raise ValueError("Observation tabel is empty")
    # We need to ask astroquery  to get the unique product list of list
    return Observations.get_unique_product_list(observations)
# Next we will check if file is a FITS file 
def IsFits(filename:str):
    ''''
        This function checks if the the file has a FITS file extention
        filename:str is a filename that ius given to be checked
    '''
    # We will check if filename has a FITS file extention
    return str(filename).lower().endswith((
        ".fits", ".fits.gz", ".fit", ".fit.gz", ".fts", ".fts.gz"
    ))
# Next we will neeed a function to filter product table 
