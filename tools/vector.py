import streamlit as st
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain.chains import RetrievalQA

from llm import llm, embeddings


# Because the index already exists in the database,you can call the from_existing_index static method.
# The Neo4jVector class also holds static methods for creating a new index from a list of documents, or a list of embeddings.
neo4jvector = Neo4jVector.from_existing_index(
    embeddings, #used to embed the user input
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
    index_name="moviePlots",
    node_label="Movie", # the label of node used to populate the index
    text_node_property="plot", # the property that holds the original plain-text value
    embedding_node_property="plotEmbedding", # the property that holds the embedding of the original text,
    # retrieval_query, is an optional parameter that allows you to define
    # which information is returned by the Cypher statement,
    # loaded into each Document and subsequently passed to the LLM.
    retrieval_query="""
    RETURN
    node.plot AS text,
    score,
    {
        title: node.title,
        directors: [ (person)-[:DIRECTED]->(node) | person.name ],
        actors: [ (person)-[r:ACTED_IN]->(node) | [person.name, r.role] ],
        tmdbId: node.tmdbId,
        source: 'https://www.themoviedb.org/movie/'+ node.tmdbId
    } AS metadata
    """
)

retriever = neo4jvector.as_retriever() # Creates an instance configured to get documents from the store itself

kg_qa = RetrievalQA.from_chain_type(
    llm,                # The LLM that used to process the chain
    chain_type="stuff", # A Stuff chain is a relatively straightforward chain that stuffs, or inserts, documents into a prompt and passes that prompt to an LLM
    retriever=retriever,# The Chain should use the Neo4jVectorRetriever created in the previous step
)

"""
More Complex 'Stuff' Retrieval Chains
We have chosen to use the .from_llm() method here because the .plot properties in the database are relatively short. The function returns an instance with default prompts.
If you find that you hit token limits, can also define chains with custom prompts that summarize the content before sending the information to the LLM.
"""

