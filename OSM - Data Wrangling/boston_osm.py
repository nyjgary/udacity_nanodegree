# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 20:47:31 2016

@author: garyng
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import operator 
import os 

osm_file = open("boston.osm", "r")
os.chdir('/Users/garyng/Documents/Udacity/Nanodegree/P3')

## Create a dictionary of street names by types 

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def group_street_name(street_types, street_name): 
    m = street_type_re.search(street_name)
    if m: 
        street_type = m.group() 
        street_types[street_type].add(street_name)
    
def create_street_dict(): 
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file): 
        if is_street_name(elem): 
            group_street_name(street_types, elem.attrib["v"])  
    return street_types
    
street_dict = create_street_dict()


## Count street types 

def tally_count(street_dict): 
    street_count_dict = {}
    for k in street_dict.keys():
        street_count_dict[k] = len(street_dict[k]) 
    street_count_dict = sort_by_count(street_count_dict)
    return street_count_dict
        
def sort_by_count(x): 
    sorted_x = sorted(x.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_x 

street_count = tally_count(street_dict)
pprint.pprint(street_count)
    
    
## Audit street types 
    
good_street_types = ["Street", "Avenue", "Drive", "Square", "Broadway", 
                     "Place", "Park", "Center", "Road", "Way", "Boulevard",
                     "Lane"]    
    
def audit_street_types(street_dict, good_street_types):
    other_street_dict = street_dict.copy()
    for k in other_street_dict.keys(): 
        if k in good_street_types: 
            other_street_dict.pop(k, None)
    return other_street_dict 
            
other_street_dict = audit_street_types(street_dict, good_street_types)
pprint.pprint(other_street_dict)    


## Correct street types 

mapping = { "St": "Street",
            "St.": "Street", 
            "Rd.": "Road",
            "Ave": "Avenue"
            }

#def tally_street_type(street_types, street_name):
#    m = street_type_re.search(street_name)
#    if m:
#        street_type = m.group()
#        street_types[street_type] += 1
#
#
#
#def count_street_type(): 
#    for event, elem in ET.iterparse(osm_file):
#        if is_street_name(elem):
#            tally_street_type(street_types, elem.attrib['v'])   
#    sorted_street_types = sort_by_count(street_types)
#    return sorted_street_types 
#    
#all_street_counts = count_street_type()
#pprint.pprint(all_street_counts)
        
## Audit unusual street types 

#
#good_street_types = ["Street", "Avenue", "Drive", "Square", "Broadway", 
#                     "Place", "Park", "Center", "Road", "Way", "Boulevard",
#                     "Lane"]
#
#other_streets = defaultdict(int)
#
#def check_other_streets(other_streets, street_name): 
#    m = street_type_re.search(street_name)
#    if m:
#        street_type = m.group()
#        if street_type not in expected:
#            street_types[street_type].add(street_name)            
#     
#
#def audit_street_type(other_streets, street_name):
#    m = street_type_re.search(street_name)
#    if m:
#        street_type = m.group()
#        if street_type not in good_street_types:
#            other_streets[street_type].add(street_name)
            


#
#expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
#            "Trail", "Parkway", "Commons"]
#
#
#            
#
#    
#def audit(osmfile):
#    osm_file = open(osmfile, "r")
#    street_types = defaultdict(set)
#    for event, elem in ET.iterparse(osm_file, events=("start",)):
#
#        if elem.tag == "node" or elem.tag == "way":
#            for tag in elem.iter("tag"):
#                if is_street_name(tag):
#                    audit_street_type_all(street_types, tag.attrib['v'])
#    osm_file.close()
#    return street_types
#
#def audit_street_type_nonexpected(street_types, street_name):
#    m = street_type_re.search(street_name)
#    if m:
#        street_type = m.group()
#        if street_type not in expected:
#            street_types[street_type].add(street_name)
#
#street_types = audit(OSMFILE)
#pprint.pprint(dict(street_types))
#
