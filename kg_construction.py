import os
from  neo4j import GraphDatabase, RoutingControl

from dotenv import load_dotenv
load_dotenv('.env')

URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    records, summary, keys = driver.execute_query(
        "MATCH (p:Person) RETURN p.name AS name",
        database_="neo4j",
    )
# Loop through results and do something with them
for record in records:
    print(record.data())  # obtain record as dict

# Summary information
print("The query `{query}` returned {records_count} records in {time} ms.".format(
    query=summary.query, records_count=len(records),
    time=summary.result_available_after
), keys)



