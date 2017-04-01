Postcode_Audit

import re
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

def is_postcode(elem):
    return (elem.attrib['k'] == 'addr:postcode')

def audit_postcode(postcodes, postcode):
    postcodes[postcode].add(postcode)
    return postcodes

def post_audit(osmfile):
    post_file = open(osmfile, "r")
    postcodes = defaultdict(set)
    for event, elem in ET.iterparse(post_file, events=("start", "end")):
        if elem.tag == 'node' or elem.tag == 'way':
            for tag in elem.iter('tag'):
                if is_postcode(tag):
                    audit_postcode(postcodes, tag.attrib['v'])
    post_file.close()
    return postcodes

post_audit('Wichita_map.osm')

