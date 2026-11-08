"""
ROLE:
    Orchastrate the entire ingestion process. It's the platform where documents r inputed into a unified stream b4 being chunkered whom doors is here burt actual engine in chunker.py, not embedding/vector search.
Meaning:
    choose files -> choose loader -> convert into document objects -> unified stream of document objects -> chunk documents -> Return List[Document]
"""

# Used to create the unified stream of document objects
from langchain_core.documents import Document

# Door to the chunking engine
from ingestion.chunker import chunk

# Door to the file extension detecting engine
from ingestion.file_type_detection import choose_loader


def ingest(file_paths: list[str]) -> list[Document]:
    """
    Parameters
    ----------
    file_paths
        List of file paths selected by the user.

    Returns
    -------
    List[Document]
        Chunked LangChain Document objects.
    """
    
    # Unified list of document objects
    all_documents = []
    
    # Loop to iterate through all selected files.
    for file_path in file_paths:
        
            # Choose appropriate loader
            loader = choose_loader(file_path)
            
            # Invoke all loaders to convert arbitraries files into LangChain Documents.
            documents = loader.load(file_path)
            
            # Now collect all document objects into one unified stream.
            all_documents.extend(documents)
            
    # now direct the unified stream into the chunker.py
    chunked_documents = chunk(all_documents)
    
    return chunked_documents