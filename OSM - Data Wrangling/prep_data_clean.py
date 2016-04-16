#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import re
import xml.etree.cElementTree as ET
import string 

# import cerberus
# import schema
import os 

os.chdir('/Users/garyng/Documents/Udacity/udacity_nanodegree/OSM - Data Wrangling')

OSM_PATH = "boston.osm"

NODES_PATH = "nodes_clean.csv"
NODE_TAGS_PATH = "nodes_tags_clean.csv"
WAYS_PATH = "ways_clean.csv"
WAY_NODES_PATH = "ways_nodes_clean.csv"
WAY_TAGS_PATH = "ways_tags_clean.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
      # Fill in the attributes under node 
      for var in node_attr_fields: 
        if element.attrib[var]: 
          node_attribs[var] = element.attrib[var]
        else: 
          node_attribs[var] = None 
      # Create dictionaries for node tags and add to tags list
      for tag in element.iter("tag"): 
        full_key = tag.attrib['k']
        if not problem_chars.match(full_key): 
          new_tag = {'id': None, 'key': None, 'value': None, 'type': None} 
          new_tag['id'] = element.attrib['id']
          new_tag['value'] = tag.attrib['v']
          if LOWER_COLON.match(full_key): 
            new_tag['type'] = full_key[ :full_key.find(':')]
            new_tag['key'] = full_key[full_key.find(':')+1: ]
          else: 
            new_tag['type'] = default_tag_type
            new_tag['key'] = full_key
        tags.append(new_tag)
      return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
      # Fill in the attributes under way 
      for var in way_attr_fields: 
        if element.attrib[var]: 
          way_attribs[var] = element.attrib[var]
        else: 
          node_attribs[var] = None 
      # Create dictionaries for way tags 
      for tag in element.iter("tag"): 
        full_key = tag.attrib['k']
        if not problem_chars.match(full_key): 
          new_tag = {'id': None, 'key': None, 'value': None, 'type': None}
          new_tag['id'] = element.attrib['id']
          new_tag['value'] = tag.attrib['v']
          if LOWER_COLON.match(full_key): 
            new_tag['type'] = full_key[ :full_key.find(':')]
            new_tag['key'] = full_key[full_key.find(':')+1: ]
          else: 
            new_tag['type'] = default_tag_type
            new_tag['key'] = full_key
        tags.append(new_tag)

      i=0
      for nd in element.iter("nd"): 
        new_nd = {'id': None, 'node_id': None, 'position': None} 
        new_nd['id'] = element.attrib['id']
        new_nd['node_id'] = nd.attrib['ref']
        new_nd['position'] = i 
        way_nodes.append(new_nd)
        i = i + 1 
      return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


st_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

st_types_good = ["Street", "Avenue", "Drive", "Square", "Broadway", "Place", 
                 "Park", "Center", "Road", "Way", "Boulevard", "Lane", 
                 "Highway", "Terrace"]  

st_types_mapping = {"Ave": "Avenue", 
                   "Ave.": "Avenue", 
                   "ave": "Avenue",
                   "Hwy": "Highway", 
                   "Pl": "Place", 
                   "ST": "Street", 
                   "Sq.": "Square", 
                   "St": "Street", 
                   "St.": "Street", 
                   "st": "Street", 
                   "street": "Street",
                   "Saints": "Saints corrected"
                   } 

cities_good = ["Cambridge", "Boston", "Somerville", "Brookline", "Charlestown",
               "Roxbury Crossing", "South Boston", "East Boston", "Roxbury"]


def clean_element(el):
    if 'way_tags' in el.keys(): 
        tags = el['way_tags']
    elif 'node_tags' in el.keys(): 
        tags = el['node_tags']
    for tag in tags: 
        if tag['key'] == 'street':
            m = st_type_re.search(tag['value'])
            if m: 
                old_street_type = m.group()
                if old_street_type in st_types_mapping: 
                    tag['value'] = str(tag['value']).replace(old_street_type, st_types_mapping[old_street_type])
                else: 
                    pass 
        elif tag['key'] == 'state': 
            if tag['value'] != 'MA': 
                tag['value'] = 'MA' 
        elif tag['key'] == 'city': 
            if tag['value'] not in cities_good: 
                tag['value'] = str(tag['value']).title()
                old_city = str(tag['value'])
                if old_city.find(',') != -1: 
                    tag['value'] = old_city[:old_city.find(',')]    
        elif tag['key'] == 'postcode': 
            zip_remove_char = re.sub('[^0-9]','', tag['value'])
            tag['value'] = str(zip_remove_char[:5])
    return el 


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


#def validate_element(element, validator, schema=SCHEMA):
#    """Raise ValidationError if element does not match schema"""
#    if validator.validate(element, schema) is not True:
#        field, errors = next(validator.errors.iteritems())
#        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
#        error_strings = (
#            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
#            for k, v in errors.iteritems()
#        )
#        raise cerberus.ValidationError(
#            message_string.format(field, "\n".join(error_strings))
#        )


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

#        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            el = clean_element(el)
            if el:
                if validate is True:
                    pass
#                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
