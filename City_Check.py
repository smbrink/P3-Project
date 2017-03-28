def city_check(filename):
    for event, element in ET.iterparse(filename, events=("start", "end")):
        if element.tag == "node" or element.tag =="way":
            for tag in element.iter("tag"):
                if tag.attrib['k'] == 'addr:city':
                    print tag.attrib['v']

city = city_check("Wichita_map.osm")