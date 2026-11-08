from knowledge.vector import retriever

# Tomorrow knowledge_services.py could search Chroma, Qdrant, PostgreSQL, Elasticsearch, or even the web without changing the Chat Engine.
# manages multiple document collections, caches, reranking, or different vector databases, ChatEngine will still be unchanged.
# ROLE: Provide knowledge from vector search. Knowledge interface. 
"""
The knowledge API
"""
def search(query_from_user):
    return retriever.invoke(query_from_user)