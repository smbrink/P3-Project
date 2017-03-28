import xml.etree.cElementTree as ET
from pprint import pprint

def count_tags(Filename):
    tags = {}
    for event, elem in ET.iterparse (Filename):
        if elem.tag not in tags.keys():
            tags[elem.tag] = 1
        else:
            tags[elem.tag] += 1
    return tags
ICT_tags = count_tags('Wichita_map.osm')
pprint(ICT_tags)