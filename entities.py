from neo4j import GraphDatabase
from transformers import pipeline
"""
import os

from dotenv import load_dotenv
load_dotenv('.env')

URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)
"""

URI = "neo4j://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "00000000"
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)

ner_pipe = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", aggregation_strategy="simple")

driver = GraphDatabase.driver(URI, auth=AUTH)

headline = "Unleash Your Creative Energy at Cruinniú Lates – Galway City Celebrates Ireland's National Day of Youth Creativity"
tags = ["community", "culture", "news"]
date = "23/4/2024"
content = """
Calling Young Aspiring DJs!
Beats and Beyond: Learn to DJ with Renowned DJ Laura O’Connell
Galway teens (ages 16-18) are invited to explore their musical creativity with Beats and Beyond, a FREE DJ workshop series led by renowned DJ Laura O'Connell. Learn the fundamentals of DJing, connect with friends, and showcase your newfound skills in a community performance! Cruinniú na nÓg is a national day of free creativity for children and young people under 18 and the flagship initiative of the Creative Ireland Programme’s Creative Youth Plan to enable the creative potential of children and young people.
Laura O'Connell, a driving force in Ireland's electronic music scene, brings her years of experience to this project. Her eclectic DJ sets have energized dance floors, radio stations, clubs, and major festivals across Ireland and the world.  A passionate advocate for inclusivity, Laura O’Connell is the co-founder of GASH Collective, which supports female, trans, queer, non-binary, and other underrepresented groups in the realms of music production and DJing. Laura is also the founder of Bounce, an accessible club night for people of all abilities.
How to Get Involved
Sign Up NOW!
No experience necessary!
Commit to 6 workshops (5pm – 7pm, May: 9, 16, 21, 30, June: 6, 11) and a showcase on June 15th at Nuns Island Theatre
Deadline for Expression of Interest: Monday, May 6th.
For further information, please contact: Adam Stoneman, Galway City Council Creative Communities Engagement Officer: adam.stoneman@galwaycity.ie 
About Cruinniú na nÓg
Cruinniú na nÓg is Ireland's national day of free creativity for everyone under 18.  Expect tons of cool events, workshops, and performances happening all across the country!
Did you know?
Galway City is one of 9 pilot cities and towns nationally leading in creating a night-time economy action plan.  These Cruinniú Lates events are designed especially for young people, offering a safe and exciting environment to socialise and enjoy diverse experiences. They are a direct result of young people’s voices being heard. Inspired by the Night-Time Economy Taskforce Report (2021) and youth-led workshops, these events demonstrate the power of young people in shaping the future of Ireland’s nightlife.
Cruinniú Lates is supported by Galway City Council, Creative Ireland, and funded by the Department of Tourism, Culture, Arts, Gaeltacht, Sports and Media.
Let's make this year's Cruinniú Lates unforgettable!
"""
url = "https://www.galwaycity.ie/news/3694/59/Unleash-Your-Creative-Energy-at-Cruinni%C3%BA-Lates-Galway-City-Celebrates-Irelands-National-Day-of-Youth-Creativity/d,NewsDetail"


entity_list = []
for entity in ner_pipe(content):
    entity_list.append(entity)

# print(entity_list)

cypher_query = """
MERGE (a:Article {url:$url})
ON CREATE SET a.headline = $headline, a.content = $cont, a.date=$date, a.tags=$tags
WITH a UNWIND $entityList as entity
MERGE(e:Entity { name:entity.word, type: entity.type })
MERGE (a)-[:references]->(e)

WITH e AS en
CALL apoc.create.addLabels( id(en), [ en.type ] )
YIELD node
REMOVE node.type
RETURN node;
"""

with driver.session(database="neo4j") as session:
    session.write_transaction(
        lambda tx: tx.run(cypher_query, url=url, headline=headline, cont=content, date=date, tags=tags,
                          entityList=[{"word": x["word"], "type": x["entity_group"]}
                                       for x in entity_list])
    )

driver.close()



"""
LOAD CSV WITH HEADERS
FROM 'https://raw.githubusercontent.com/akousis/Smart-city-kg/main/data/news.csv' AS row
FIELDTERMINATOR ';'
MERGE (n:News {newsid: toInteger(row.newsid)})
ON CREATE SET
n.headline = row.headline,
n.content = row.content,
n.date = row.date;
"""
