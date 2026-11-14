# I spent too long commenting becuase i heard this will most likely
# become opensource so yea, if anyone is using this, thank me. 
# Number of hours spent writing this file: 4
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
    collections:list[str]|None = None,
    maxObservations:int = 50
):
    '''
        A function that searches through MAST
        - target:str is the location or the name of the target 
        - radius_:str is the search raduis aroudn the target
        - collections:list[str]|None is the names of optional missions 
          or archive collections (such as JWST etc.)
        - maxObservations:int is the maximum number of returned 
          observations
    '''
    # First we will query Mast for observations
    observations = Observations.query_object(target, radius=radius_) 
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
def GetProducts(observations:Table):
    '''
        This function actually retrieves the data producst regarding the 
        observation, one observation can have multiple product data
        - observations:Table is the the observation
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
def SelectProducts(
    products:Table,
    productTypes:set|None=None,
    maxProducts:int=20,
    publicOnly:bool=True
):
    '''
        This function filters the product table based on the product types
        - products:array is a 2D array containing all the products (not like a 
          vanilla array though)
        - productTypes:set is a set that is used to filter out all the products
        - maxProducts:int specifies the maximum number of selected products
        - publicOnly:bool specifies whether to include non public products too
          when the rights field is available. 
    '''
    if productTypes == None:
        # If user did not specify the productTypes then we wil be using the INITIAL_TYPES 
        # as the product types
        productTypes = INITIAL_TYPES
    # Next we will first make all product types in uppercase (for consistancy and ease)
    allowed = {str(value).upper() for value in productTypes}
    # Checks if the products have 2 columns "productFilename", "dataproduct_type" and 
    # raises an error if there is a missing columns
    required = {"productFilename", "dataproduct_type"}
    missing = required - set(products.colnames)
    if missing:
        raise ValueError(
            "MAST product table is missing columns: "
            + ", ".join(sorted(missing))
        )
    selected = [] # This will hold rows indexes of accepted products
    for index, row in enumerate(products):
        # The enumerate allows teh for loop to loop through the index of the product and
        # the product data itself
        filename = str(row["productFilename"]) # Extracts filename
        kind = str(row["dataproduct_type"]).upper() # Extracts teh product type for the file name
        # First we need to reject all non FITS files
        if not IsFits(filename) or kind not in allowed:
            continue 
        # Next we need to check if there is public only filtering and whether the product table has 
        # dataRights column 
        if publicOnly and "dataRights" in products.colnames:
            # We will then skip all products that are not public
            if str(row["dataRights"]).upper() != "PUBLIC":
                continue
        # We will now see if there are any other catagories and we will filter it so that only the specified 
        # catagories are taken in
        if productTypes in products.colnames:
            catagory = str(row["productTypes"]).upper()
            # catagories outiside of  "SCIENCE", "CATALOG", "LIGHTCURVE", "TARGETPIXELS" are skiped 
            if catagory not in {
                "SCIENCE", "CATALOG", "LIGHTCURVE", "TARGETPIXELS"
            }:
                continue
        selected.append(index) # Stores the index of the accepted products
        # We now break teh loop if the maximum products is reached
        if len(selected) >= maxProducts:
            break
    return products[selected] if selected else products[:0] # Returns rows of selected if slected has indexes 
                                                            # If not then returns a empty set
# Now we need to combine all the functions above
def SearchAndDownload(
    target:str,
    radius:str = "0.02 deg",
    collections:list[]|None = None,
    maxObservations:int = 50,
    maxProducts:int = 20,
    productTypes:set|None = None
):
    '''
        This function cordinates all the functions in the in this file
        - All arguments are either understood in the previous functions or are very self explanitory
    '''
    root = Path(__file__).resolve().parent[2] # Stores the project directory 
    rawDir = root / "data" / "raw" # Diretcory of downloaded FITS files 
    manifestDir = root / "data" / "manifest" # Directory of the csv files discribing search and downloads
    # We next need to ensure that we create this directories if they dont exist
    rawDir.mkdir(parents=True, exist_ok=True)
    manifestDir.mkdir(parents=True, exist_ok=True)
    # Now we need to call all the previous functions
    observations = SearchObservations(target, radius, collections, maxObservations)
    products = GetProducts(observations)
    selected = SelectProducts(products, productTypes, maxProducts)
    # Now we are saving observation records and selected products
    observations.write(manifestDir / "observations.csv", format="csv", overwrite=True)
    selected.write(manifestDir / "selected_products.csv", format=csv, overwrite=True)
    # We will next check whether anything was selected
    if len(selected) == 0:
        raise ValueError("No mathcing PUBLIC FITS producst are found, please try a different target")
    # Now we are asking Astroquery to download selected files
    manifest = Observations.downloadProducts(selected, download_dir=str(rawDir), flat=False, cache=True)
    # Next we will download manifest if manifest exists
    if manifest is not None:
        manifest.write(manifestDir / "download.csv", format="csv", overwrite=True)
    return observations, selected, manifest
