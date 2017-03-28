def count_city(filename):
    for event, element in ET.iterparse(filename, events=("start", "end")):
        if element.tag == "node" or element.tag =="way":
            for tag in element.iter("tag"):
                if tag.attrib['k'] == 'addr:city' and tag.attrib['v'] == 'Witchita':
                    print tag.attrib['v'] 
city = count_city("Wichita_map.osm")