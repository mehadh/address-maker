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
import zipcodes
from addressgen import *
callsToAPI = 0
callsWithResult = 0
client = None

os.chdir(sys.path[0])

def setupSmarty():
    global client
    auth_id = ""
    auth_token = ""
    credentials = StaticCredentials(auth_id, auth_token)
    client = ClientBuilder(credentials).build_us_street_api_client()
    return True

def getZip(city, state):
    zipList = zipcodes.filter_by(city=city, state=state)
    rList = [data['zip_code'] for data in zipList]
    return rList

def nValidate(street, city, state, zipList):
    global callsToAPI
    global callsWithResult
    lookup = Lookup()
    lookup.street = street
    lookup.city = city
    lookup.state = state
    #lookup.zipcode = zipcode
    client.send_lookup(lookup)
    callsToAPI += 1
    if len(lookup.result) != 0:
        callsWithResult += 1
        return lookup.result[0] # quantity over quality fix
        #print(lookup.result[0].metadata.rdi) #DEBUG API PLAN
        #if lookup.result[0].components.zipcode == zipcode and lookup.result[0].metadata.rdi == "Residential":
        if lookup.result[0].metadata.rdi == "Residential" and lookup.result[0].components.zipcode in zipList:
            #print("lookup yield good")
            return lookup.result[0]
        else:
            #print("lookup yield with bad zip or commercial")
            return False
    else:
        #print("lookup yield 0")
        return False

def cityAddress(roads, city, state, zipList):
    while True:
        address = derive_address(roads)
        #result = nValidate(address, city, state, zipList)
        result = address # validate bypass
        if result != False:
            return result

def cityToAddress(city, state, amount, surpress=False):
    setupSmarty()  # initialize API
    zipList = getZip(city, state)
    zipCode = random.choice(zipList)
    roads = giveRoads(zipCode)
    data_path_one_line = os.path.join(os.path.expanduser('~'), 'Desktop', 'DATA')
    if not os.path.exists(data_path_one_line):
        os.makedirs(data_path_one_line)
    
    for index in range(amount):
        try:
            address = cityAddress(roads, city, state, zipList)
        except Exception as e:
            print("except!!::", e)
            #break
        #result = resultToStr(address)
        result = "{}, {}, {} {}".format(address, city, state, zipCode)
        with open(data_path_one_line+"/"+city+state+".txt", "a") as f:
            f.write(result + "\n")
        if not surpress:
            print("{}".format(result))
    if not surpress:
        print("Completed request! Calls to API: "+str(callsToAPI)+" Calls with result: "+str(callsWithResult))
    return True

def extHandler(city, state, amount, surpress=False):
    try:
        result = cityToAddress(city, state, amount, surpress)
        return result
    except Exception as e:
        print(e)
        return False