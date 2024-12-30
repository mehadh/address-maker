import os
import zipfile
import fiona
import random
import requests
from uszipcode import SearchEngine
import addfips
import sys
from smartystreets_python_sdk import StaticCredentials, ClientBuilder                               
from smartystreets_python_sdk.us_street import Lookup    
callsToAPI = 0
callsWithResult = 0
client = None

os.chdir(sys.path[0])

tiger_path_one_line = os.path.join(os.path.expanduser('~'), 'Desktop', 'TIGER')


def zip2fips(zipCode):
    with SearchEngine() as search:
        result = search.by_zipcode(zipCode)
    fips = addfips.AddFIPS().get_county_fips(result.county, state=result.state)
    #print("ZIP {} associate with FIPS {}".format(zipCode, fips))
    return fips

def grabTiger(fips, zipCode):
    #zip_folder = "./TIGER"
    zip_folder = tiger_path_one_line
    
    if not os.path.exists(zip_folder):
        os.makedirs(zip_folder)
    
    url = "https://www2.census.gov/geo/tiger/TIGER_RD18/LAYER/EDGES/"
    fName = "tl_rd22_{}_edges.zip".format(fips)
    response = requests.get(url+fName)
    response.raise_for_status()
    
    zip_path = os.path.join(zip_folder, fName)
    with open(zip_path, "wb+") as file:
        file.write(response.content)
    #print("download TIGER file on zip {} in folder {}".format(zipCode, zip_folder))
    return zip_path

def getZipEdge(zipCode):
    try:
        fips = zip2fips(zipCode)
    except Exception as e:
        print("Exception in zip2fips")
        print(e)
        return False
    folder_path = tiger_path_one_line+"/tl_rd22_{}_edges".format(fips)
    if os.path.exists(folder_path):
        #print("!! exist folder {} !!".format(folder_path))
        return True
    try:
        return grabTiger(fips, zipCode)
    except Exception as e:
        print("Exception in grabTiger")
        print(e)
        return False


def load_shapefile(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        zip_folder = os.path.splitext(zip_path)[0]
        z.extractall(zip_folder)
        shp_path = [s for s in z.namelist() if ".shp" in s][0]
        #print("unzip on tiger data")
        return fiona.open(zip_folder + '/' + shp_path)

def filter_roads(df):
    if df is None:
        return None
    return [feature for feature in df if feature['properties']['ROADFLG'] == 'Y']

def derive_address(road_df):
    while True:
        road_segment = random.choice(road_df)
        road_properties = dict(road_segment['properties'])

        road_name = road_properties.get('FULLNAME', None)
        lfromadd = road_properties.get('LFROMADD', None)
        ltoadd = road_properties.get('LTOADD', None)
        rfromadd = road_properties.get('RFROMADD', None)
        rtoadd = road_properties.get('RTOADD', None)
        
        if road_name is not None and lfromadd is not None and ltoadd is not None and rfromadd is not None and rtoadd is not None:
            try:
                lfromadd = int(lfromadd)
                ltoadd = int(ltoadd)
                rfromadd = int(rfromadd)
                rtoadd = int(rtoadd)
                
                if lfromadd <= ltoadd and rfromadd <= rtoadd: 
                    break
                else:
                    #print("Invalid address ranges, retrying...")
                    pass
            except ValueError:
                #print("Invalid address range format, retrying...")
                continue
        else:
            #print("Missing properties, retrying...") # DEBUG: ENABLE
            pass
    if random.choice([True, False]):
        address_num = random.randint(lfromadd, ltoadd)
    else:
        address_num = random.randint(rfromadd, rtoadd)

    return "{} {}".format(address_num, road_name)


def giveRoads(zipCode):
    success = getZipEdge(zipCode)
    if not success:
        return None
    fips = zip2fips(zipCode)
    
    zip_path = tiger_path_one_line+"/tl_rd22_{}_edges.zip".format(fips)
    df = load_shapefile(zip_path)

    addresses = []
    roads = filter_roads(df)
    #print("roads ready")
    return roads

def setupSmarty():
    global client
    auth_id = "none"
    auth_token = "none"
    credentials = StaticCredentials(auth_id, auth_token)
    client = ClientBuilder(credentials).build_us_street_api_client()
    return True

def validate(street, zipcode):
    global callsToAPI
    global callsWithResult
    lookup = Lookup()
    lookup.street = street
    lookup.zipcode = zipcode
    client.send_lookup(lookup)
    callsToAPI += 1
    if len(lookup.result) != 0:
        callsWithResult += 1
        #if lookup.result[0].components.zipcode == zipcode and lookup.result[0].metadata.rdi == "Residential":
        if lookup.result[0].metadata.rdi == "Residential":
            print("lookup yield good")
            return lookup.result[0]
        else:
            print("lookup yield with bad zip or commercial")
            return False
    else:
        print("lookup yield 0")
        return False

def processAddress(roads, zipcode):
    while True:
        address = derive_address(roads)
        result = validate(address, zipcode)
        if result != False:
            return result

def resultToStr(addObj):
    return addObj.delivery_line_1+", "+addObj.components.city_name+", "+addObj.components.state_abbreviation+" "+addObj.components.zipcode

data_path_one_line = os.path.join(os.path.expanduser('~'), 'Desktop', 'DATA')

def addressesToFile(zipCode, amount):
    setupSmarty()  # initialize API
    roads = giveRoads(zipCode)

    if not os.path.exists(data_path_one_line):
        os.makedirs(data_path_one_line)
    
    with open(data_path_one_line+"/"+zipCode+".txt", "a") as f:
        for index in range(amount):
            address = processAddress(roads, zipCode)
            result = resultToStr(address)
            f.write(result + "\n")
            print("{}".format(result))
    
    print("Completed request! Calls to API: "+str(callsToAPI)+" Calls with result: "+str(callsWithResult))
