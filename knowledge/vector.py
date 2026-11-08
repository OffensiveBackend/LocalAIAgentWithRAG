"""
ROLE:
    Build and expose the vector database

Responsibilities:
    1. Receive chunked Documents
    2. Embed them
    3. Store them inside Chroma
    4. Expose a Retriever
"""
# Always for file handling.
import os

# Our vector database/storage
from langchain_chroma import Chroma

# Creates documents that will be passed to our vector database
from langchain_ollama import OllamaEmbeddings

from ingestion.ingestion_pipeline import ingest

# Embedding model: converts text into vectors for semantic-search(vector-search)
# Define our embedding model.
# model="mxbai-embed-large"
embeddings = OllamaEmbeddings(
    model="mxbai-embed-large" # Define our embedding model.
)


# List of selected files
documents = ingest([
        "data/realistic_restaurant_reviews.csv",
        "data/restaurant_information.txt"
    ])

# Folder where we can store our database.
db_location = "cache/chrome_langchain_db"
# Check is the database folder already exits. For one-time vectorisation of our data. Creates the actual databases in the folder.
add_documents = not os.path.exists(db_location) # Condition_set: If the above condition doesn't exist.


# Logic for:
# => automatically embeds all of the documents for us then/and add it to our vector store. 
# => grouping created documents b4 storage in a vector store.
# Create vector store. Info is being looked-up using a similarity search algorithm
# Initialise our vector database, if the above defined location already exists.
vector_store = Chroma(
    collection_name = "restaurant_reviews", # Under which category should the embeddings be classified?
    persist_directory = db_location, # stored persistently rather than in memory.
    embedding_function = embeddings # pass the embedding document.
)

# Logic to add created documents into our vector store, if the above defined vector database doesn't exist.
if add_documents:
    
    ids = [doc.id for doc in documents]
    
    vector_store.add_documents(
        documents = documents, # Specify the documents u were add
        ids = ids # Specify the corresponding id
    )
    
# Capability_unlocked: (Semantic query search) instead of (advanced keyword matching).
# Make this vector search usable by our LLM for semantic meaning.
retriever = vector_store.as_retriever( #kwargs => key word arguments
    search_kwargs = {
        "k": 5, # gonna lookup 5 relevant reviews then pass then to the llm.
        # Allows us to look for relevant arguments which we will pass unto our llm
    }
)

# print(vector_store._collection.count()) # Test whether vector store is empty
# Architecture:
# embedding -> indexing -> retrial.