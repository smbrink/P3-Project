
# P3 Data Wrangling OpenStreetMap 



## I chose my hometown of Wichita, KS <https://mapzen.com/data/metro-extracts/your-extracts/8c887a425e33> from MapZen for this project. I had to do a custom extract to get the recommended amount of data. I chose Wichita, KS because I was curious and wanted to understand all the data involved. 

##                                      Custom Wichita, Ks Map Extract Visual.

<img src="MapZen.jpeg">

## Data Overview P3.

File Sizes:

```
Wichita_map.osm.......... 52.4 MB
Wichita.db............... 29.7 MB
Nodes.csv................ 18.7 MB
Nodes_tags.csv........... 760  KB
Ways.csv................. 1.6  MB
Ways_nodes.csv........... 6.2  MB
Ways_tags.csv............ 6.1  MB
```

## Used to get the number of Tags

```
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
```

## Number of Nodes

```
sqlite> Select Count(*) From Nodes;
```


223140

# Number of Ways

```
sqlite> Select Count(*) From Ways;
```

27033

# Problems with the Data Set

### After downloading the Data Set and examining a small sample it became apparent that the top two main issues  were the abbreviations of names in the streets/inconsistant street names and the addition of ZIP+4 Postal Codes. 

### In order to audit the abbreviation of names/inconsistant street names issue I used the code I helped write from the Case Study as shown below then I followed that up with the write_data.py script to fix.


```
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

# Used in the write_data.py script to fix streets data.
def update_name(name, mapping): 
    for search_error in mapping:
        if search_error in name:
            name = re.sub(r'\b' + search_error + r'\b\.?', mapping[search_error], name)
    return name
```

### I also noticed while examining the dataset that some of the postal codes had what is known as ZIP+4 or the five digit zipcode with a hyphen and four additional digits at the end identifying specific delivery routes. I decided to drop the extra 4 digits to stay consistant with the majority of the other postal codes. Below is the code to audit the postal codes and I followed that up with the write_data.py script to fix the inconsistant codes.

```
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

# Used in write_data.py to update inconsistant postal codes.
def updated_postcodes(postcode):
    search = re.match(r'^\D*(\d{5}).*', postcode)
    clean_postcode = search.group(1)
    return clean_postcode
```

# Additional Problems with the Data Set

## After digging a little deeper I noticed some of the Cities names were misspelled, specifically some instances of Wichita were spelled as Witchita. I decided to leave the misspellings of Wichita alone since there was only a small number of them (also they could of possibly been misspelled on purpose due to the tie-in with the Wizard of Oz).

```
sqlite> SELECT tags.value, COUNT(*) as count
   ...> FROM (SELECT * FROM ways_tags UNION ALL
   ...> SELECT * From nodes_tags) tags WHERE
   ...> key Like "%city%" Group By
   ...> value Order By count DESC
   ...> Limit 4;
Wichita|524
Derby|8
Haysville|6
Witchita|5
```

```
sqlite> Select Count(*) From nodes_tags
   ...> Where value = 'Witchita';
   
3   
```

## Used to check the cities names.
```
def city_check(filename):
    for event, element in ET.iterparse(filename, events=("start", "end")):
        if element.tag == "node" or element.tag =="way":
            for tag in element.iter("tag"):
                if tag.attrib['k'] == 'addr:city':
                    print tag.attrib['v']
                
city = city_check("Wichita_map.osm")
```

## Used to get the number of misspelled Witchita's.
```
def count_city(filename):
    for event, element in ET.iterparse(filename, events=("start", "end")):
        if element.tag == "node" or element.tag =="way":
            for tag in element.iter("tag"):
                if tag.attrib['k'] == 'addr:city' and tag.attrib['v'] == 'Witchita':
                    print tag.attrib['v'] 
city_spelling = count_city("Wichita_map.osm")
```


# SQL Queries to Gather Data.

## Multiple Queries to get a feeling for the data.

```
sqlite> Select Count(*) From nodes_tags Where value = 'Quick Trip';
2
sqlite> Select Count(*) From nodes_tags Where value = 'convenience';
21
sqlite> Select Count(*) From nodes_tags Where value = 'fast_food';
65
sqlite> Select Count(*) From nodes_tags Where value = 'bank';
27
sqlite> Select Count(*) From nodes_tags Where value = 'school';
284
sqlite> Select Count(*) From nodes_tags Where value = 'restaurant';
86
sqlite> Select Count(*) From nodes_tags Where value = 'sports_centre';
14
sqlite> Select Count(*) From nodes_tags Where value = 'tree';
84
sqlite> Select Count(*) From nodes_tags Where value = 'cafe';
11
sqlite> Select Count(*) From nodes_tags Where value = 'motel';
32
sqlite> Select Count(*) From nodes_tags Where value = 'hotel';
48
sqlite> Select Count(*) From nodes_tags Where value = 'pizza';
5
sqlite> Select Count(*) From nodes_tags Where key = 'shop';
127
sqlite> Select Count(*) From nodes_tags Where key = 'highway';
2576
```

## Top 15 Values of Amenities in Nodes_Tags

```
sqlite> Select value, Count(*) as num
   ...> From nodes_tags
   ...> Where key='amenity'
   ...> Order By num DESC
   ...> Group By value
   ...> Limit 15;
place_of_worship|364
school|283
restaurant|86
fast_food|65
fuel|36
parking|33
fire_station|30
bank|27
police|21
bench|18
library|17
grave_yard|14
townhall|14
waste_basket|12
cafe|11
```


## Top Restaurant's in Nodes_Tags

```
sqlite> SELECT nodes_tags.value, COUNT(*) as num
   ...> FROM nodes_tags 
   ...> JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
   ...> ON nodes_tags.id=i.id
   ...> WHERE nodes_tags.key='cuisine'
   ...> GROUP BY nodes_tags.value
   ...> ORDER BY num DESC;
chinese|15
mexican|9
american|4
pizza|4
regional|3
asian|2
thai|2
bbq|1
breakfast|1
burger|1
french|1
ice_cream|1
indian|1
italian|1
japanese|1
latin|1
sandwich|1
sushi,_hibachi,_japanese_steakhouse,_seafood|1
```

## Top 10 Fast Food Restaurants

```
sqlite> Select nodes_tags.value, Count(*) as num
   ...> From nodes_tags
   ...> Join (Select Distinct(id) From nodes_tags Where value='fast_food') i
   ...> On nodes_tags.id = i.id
   ...> Where nodes_tags.key='name'
   ...> Group By nodes_tags.value
   ...> Order By num DESC
   ...> Limit 10;
   ```

```
McDonald's|10
Spangles|6
Subway|5
Taco Bell|5
Braum's|3
Chipotle|3
Schlotzsky's Deli|3
Arby's|2
Burger King|2
Planet Sub|2
```

## Top 10 Cafes

```
sqlite> Select nodes_tags.value, Count(*) as num
   ...> From nodes_tags
   ...> Join (Select Distinct(id) From nodes_tags Where value='cafe') i
   ...> On nodes_tags.id = i.id
   ...> Where nodes_tags.key='name'
   ...> Group By nodes_tags.value
   ...> Order By num DESC
   ...> Limit 10;
Starbucks|2
Caffe Posto|1
Espresso to Go Go|1
Mead's Corner|1
Panera Bread|1
Reverie Coffee Roasters|1
Scooter's Drive Thru Coffee|1
The Spice Merchant|1
Watermark Books & Cafe|1
```

## Latest update before I downloded the data on 03/13/2017 12:14 AM.

```
sqlite> SELECT timestamp FROM Nodes UNION SELECT timestamp From Ways
   ...> ORDER BY timestamp DESC
   ...> LIMIT 1;
```

```
2017-03-11T21:12:31Z
```

## Top 20 Contributors by Uid

```
sqlite> SELECT e.user, COUNT(*) as num
   ...> FROM (SELECT user FROM Nodes UNION ALL SELECT user FROM Ways) e
   ...> GROUP BY e.user
   ...> ORDER BY num DESC
   ...> LIMIT 20;
woodpeck_fixbot|65011
ToeBee|25951
louisakuchen|25681
BHawthorne|16757
PHerison|14611
Tim Litwiller|8428
balrog-kun|7216
Mark Gray|6783
Rub21|5395
railfan-eric|5352
TIGERcnl|4944
Lambertus|4475
Sundance|4130
Scott Plank|3413
Glen|3254
andrewpmk|3028
Berjoh|2954
bahnpirat|2833
Wichita-dweller|2767
Mark Appier|2521
```

# Improvement of DataSet

I believe the most needed improvement to the dataset of Wichita, KS is more data for local stores, restaurants, and other amenities. After doing multiple queries in SQL there appears to be alot of keys and values missing in the nodes_tags/ways_tags data set. They are missing multiple stores, banks, cafes, and other needed areas.

I believe it could be fixed with some form of APP/API based on Google where if somebody searches Google for an address or business and gets a match Google could check that data with OpenStreetMap to see if it needed to be added therefore increasing the amount of nodes_tags/ways_tags. The main drawback I could see with that would be people concerned about their security with Google sending all or most searches to another database (OpenStreetMaps). It could leave them venerable to hackers and malware. Some people would also probably discontinue using Google for fear of people keeping track of their search data. They would also need to make sure they would only send the required amount of data in a standardized form to OpenStreetMaps as to not overwhelm the dataset or corrupt it.

# Conclusion

After loooking at the data and gathering some of the facts it appears there is still alot of work that needs to be done. Most of the Streets and Highways appear to be correct but there needs to be a greater focus on the amenities area showing all of the options available to someone. All in all though a good deal of information all in one spot.


```python

```
