from neo4j import GraphDatabase
from transformers import pipeline
import pandas as pd
import ast

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


news_df = pd.read_csv('https://raw.githubusercontent.com/akousis/Smart-city-kg/main/data/news.csv', sep=';')

for index, row in news_df.iterrows():
    newsid = row['newsid']
    headline = row['headline']
    content = row['content']
    date = row['date']
    url = row['url']
    tags_string = row['tags']
    tags = ast.literal_eval(tags_string)  # turns string into list

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
    """

    with driver.session(database="neo4j") as session:
        session.write_transaction(
            lambda tx: tx.run(cypher_query, url=url, headline=headline, cont=content, date=date, tags=tags,
                              entityList=[{"word": x["word"], "type": x["entity_group"]}
                                           for x in entity_list])
        )

    driver.close()
