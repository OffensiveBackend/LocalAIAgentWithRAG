"""
chunker.py

ROLE
----
Split LangChain Document objects into smaller, semantically meaningful
Document objects before embedding.

Pipeline
--------
1. Inspect metadata
2. Choose chunking strategy
3. Execute chunking strategy
4. Annotate metadata
5. Return chunked documents

DESIGN NOTES
------------
- The chunker knows nothing about loaders.
- The chunker knows nothing about embeddings or vector databases.
- It simply receives List[Document] and returns List[Document].
- Strategies are chosen from metadata attached by the loaders.
- Every returned chunk is self-describing via metadata.

Future strategies
-----------------
- semantic (txt, pdf, docx, md)
- recursive (generic fallback)
- code-aware (.py, .js, .java, ...)
- html-aware
- markdown-aware
"""

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# CHUNKING ENGINES

# 1st engine
# This engines attempts to split n' organise text based on context
SEMANTIC_CHUNKER = RecursiveCharacterTextSplitter(
    chunk_size = 300, 
    chunk_overlap = 100,
    # Indicators that enhance logic for context/semantic based chunking.
    separators = [
        "\n\n", # detect double spaces
        
        "\n", # detect single space
        
        # detect puncuation marks
        ".","?", "!",";",",",
        
        " ",""
        
        ]
)


# 2nd engine
# This engine splits text based on xter sive.
RECURSIVE_CHUNKER = RecursiveCharacterTextSplitter(
    chunk_size = 400, # Max no. of xters per chunk
    chunk_overlap=100 # with overlap amongst chunks in an attempt to retain semantic meaning
)


# Stage 1: Inspect metadata
# then return a lightweight dictionary used by the strategy selector
def inspect_metadata( document: Document) -> dict:
    
    # load metadata from documents
    metadata = document.metadata
    
    return {
        "file_type": metadata.get("file_type"," ").lower(),
        "source": metadata.get("source",""),
        "loader": metadata.get("loader","unknown_loader")
    }


# Stage 2: Choose strategy
# then decide the splitter.
def choose_strategy(file_type: str):
    
    # Catalogue of file types surported by the semantic-based chunking engine
    semantic_types = {
        "txt",
        "pdf",
        "docx",
        "md"
    }
    
    # Logic for decision making
    if file_type in semantic_types:
        return "sematic", SEMANTIC_CHUNKER
    
    return "recursive", RECURSIVE_CHUNKER # Incharge of handling .csv files


# Stage 3: Execute strategy
# by excuting the selected splitter n' return list of chunked Documents
# Where the actual chunking occurs
def execute_strategy(
    document: Document,
    splitter: RecursiveCharacterTextSplitter # abstraction layer from LangChain package to execute selected splitter
) -> list[Document]:
    
    return splitter.split_documents([document])


# Step 4: Annotate metadata
# on every chunk
# to enhance traceability and answer attribution.
def annotate_metadata(
    chunks: list[Document],
    original_document: Document,
    strategy_name: str
) -> list[Document]:
    
    # Original file type n' name
    original_metadata = original_document.metadata.copy()
    
    # directory path to file
    source = original_metadata.get("source","unknown")
    
    # unique identifier for every chunk
    document_id = Path(source).stem
    
    # Number of make chunks
    total_chunks = len(chunks)
    
    for index, chunk in enumerate(chunks):
        
        # leverage in-built append feature to update the LangChain objects metadata
        # permanent hence forth
        chunk.metadata.update(original_metadata)
        chunk.metadata.update({
            
            "document_id": document_id,
            
            "chunk_strategy": strategy_name,
            
            "chunk_index" : index, # 0-based
            
            "total_chunks" : total_chunks
            
        })
        
    return chunks

# Step 5: Orchestrator
# where all LangChain Documents from multiple loaders r received.
# where the chunking  pipeline gets coordination
# and returns unified  chunk stream
def chunk(
    # Original list of LangChain Documents from all loaders
    documents: list[Document]
          ) -> list[Document]:
    
    # list for unified chunk stream
    chunked_documents = []
    
    # loop to itterate list of LangChain Documents and effect changes
    for document in documents:
        
        # STEP 1: get metadata
        metadata = inspect_metadata(document)
        
        # STEP 2: choose chunking strategy using info from metadata
        strategy_name, splitter = choose_strategy(
            metadata["file_type"]
        )
        
        # STEP 3: execute selected strategy
        chunks = execute_strategy(
            document,
            splitter
        )
        
        # STEP 4: annotate metadata
        chunks = annotate_metadata(
            chunks,
            document,
            strategy_name
        )
        
        # FINALLY: list of chunked documents ready for vector.py embedding
        chunked_documents.extend(chunks)
        
    return chunked_documents