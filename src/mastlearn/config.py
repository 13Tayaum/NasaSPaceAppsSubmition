# Import all libraries
from pathlib import Path
import numpy as np 
from astroquery.mast import Observations

# Define all the types of data that will be use

InnitialTypes = {
    "IMAGES", "SPECTRUM", "SED", "TIMESERIES", "CATALOG"
}

def SearchObservation(target:str, radius_:str="0.02 deg", collections:list[str]=None, MaxObservations:int=50):
    ''' Searches the MAST catalog by the provided target and if a collection is specified then it will display acording to the collection (such as HST or JWST)            
        SearchObservation(target:str, radius_:str="0.02 deg", collections:list[str]=None, MaxObservations:int=50):
    '''
    observations = Observations.query_object(target, radius=radius_)
    if len(observations) == 0:
        raise ValueError(f"No observations found for target{target}")
    if collections:
        allowed = {str(value).upper() for value in collections}
        actual = np.asarray(observations["obs_collection"], dtype=str)
        keep = np.isin(np.char.upper(actual), list(allowed))
        observations = observations[keep]
    return observations[:max_observations]

def GetProducts()
