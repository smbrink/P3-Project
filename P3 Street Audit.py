import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "Wichita_map.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle", "North", "South", "First", "Greenwich", "Maize"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Cir": 'Circle',
            "Cir.": "circle",
            "Ct": "Court",
            "Ct.": "Court",
            "N": "North",
            "S": "South",
            "S.": "South",
            "W": "West",
            "E": "East",
            "Rd": "Road",
            "Dr": "Drive",
            "Pl": "Place"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(OSMFILE):
    osm_file = open(OSMFILE, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start","end")):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])           
    osm_file.close()
    return street_types
Streets = audit(OSMFILE)
print Streets