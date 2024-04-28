LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/akousis/Smart-city-kg/main/data/LibrariesOpenData.csv' AS row
MERGE (l:Library {objectId: toInteger(row.OBJECTID)})
SET
l.latitude = toFloat(row.Y),
l.longitude = toFloat(row.X),
l.name = row.NAME,
l.address = row.ADDRESS,
l.tel = row.TEL,
l.email = row.EMAIL,
l.monday = row.MONDAY,
l.tuesday = row.TUESDAY,
l.wednesday = row.WEDNESDAY,
l.thursday = row.THURSDAY,
l.friday = row.FRIDAY,
l.saturday = row.SATURDAY,
l.lat = row.Lat,
l.long = row.Long,
l.eastItm = row.EastITM,
l.northItm = row.NorthITM,
l.eastIg = row.EastIG,
l.northIg = row.NortIG


LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/akousis/Smart-city-kg/main/data/CityParksOpenData.csv' AS row
MERGE (p:Park {objectId: toInteger(row.OBJECTID)})
SET
p.number = toInteger(row.NUMBER),
p.name = row.NAME,
p.location = row.LOCATION,
p.areaOfCity = row.AREAOFCITY,
p.openingHrs = row.OPENINGHRs,
p.facilities = row.FACILITIES,
p.description = row.DESCR,
p.latitude = toFloat(row.Lat),
p.longitude = toFloat(row.Long),
p.eastItm = toFloat(row.EastITM),
p.northItm = toFloat(row.NorthITM),
p.eastIg = toFloat(row.EastIG),
p.northIg = toFloat(row.NortIG),
p.shapeArea = toFloat(row.Shape__Area),
p.shapeLength = toFloat(row.Shape__Length)

CALL apoc.load.json("https://github.com/akousis/Smart-city-kg/blob/main/data/CityParksOpenData.geojson") YIELD value
UNWIND value.features AS feature
WITH feature.properties AS properties, feature.geometry AS geometry
// Process properties and create nodes
MERGE (n:FeatureNode {id: properties.id}) SET n += properties
// Handle different types of geometries (Point, LineString, Polygon, etc.)
FOREACH (point IN CASE WHEN geometry.type = 'Point' THEN [geometry.coordinates] ELSE [] END |
    CREATE (n)-[:HAS_POINT]->(:Point {coordinates: point})
)
FOREACH (lineString IN CASE WHEN geometry.type = 'LineString' THEN [geometry.coordinates] ELSE [] END |
    FOREACH (point IN lineString |
        CREATE (n)-[:HAS_POINT]->(:Point {coordinates: point})
    )
)
FOREACH (polygon IN CASE WHEN geometry.type = 'Polygon' THEN [geometry.coordinates] ELSE [] END |
    FOREACH (ring IN polygon |
        FOREACH (point IN ring |
            CREATE (n)-[:HAS_POINT]->(:Point {coordinates: point})
        )
    )
)

LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/akousis/Smart-city-kg/main/data/Cycle_Lanes.csv' AS row
MERGE (cl:CycleLane {objectId: toInteger(row.OBJECTID)})
ON CREATE SET
cl.mgid = toInteger(row.MGID),
cl.cycle_lane = row.Cycle_lane,
cl.length_km = toFloat(row.Length_KM),
cl.type = row.Type,
cl.globalid = row.GlobalID,
cl.shapeLength = toFloat(row.Shape__Length)

LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/akousis/Smart-city-kg/main/data/Cycle_Lanes.csv' AS row
MERGE (cl:CycleLane {objectId: toInteger(row.OBJECTID)})
ON MATCH SET
cl.name = row.Cycle_Lane,
cl.cycle_lane = row.Cycle_Lane


LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/akousis/Smart-city-kg/main/data/TennisCourtsOpenData.csv' AS row
MERGE (t:TennisCourt {objectId: toInteger(row.OBJECTID)})
ON CREATE SET
t.x = toInteger(row.X),
t.y = toInteger(row.Y),
t.courtLocation = row.TCOURTLOCN,
t.latitude = toFloat(row.Lat),
t.longitude = toFloat(row.Long),
t.eastItm = toFloat(row.EastITM),
t.northItm = toFloat(row.NorthITM),
t.eastIg = toFloat(row.EastIG),
t.northIg = toFloat(row.NortIG);

LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/akousis/Smart-city-kg/main/data/news.csv' AS row
FIELDTERMINATOR ';'
MERGE (n:News {newsid: toInteger(row.newsid)})
ON CREATE SET
n.headline = row.headline,
n.content = row.content,
n.date = row.date;