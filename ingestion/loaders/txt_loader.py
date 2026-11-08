"""
ROLE:
    Convert a plain text file into LangChain Documents
"""

from pathlib import Path  # Framework to read plain text

from langchain_core.documents import Document


# Logic to output list of LangChain objects
def load(file_path: str):
    
    # Instructions on how  to work
    text = Path(file_path).read_text(
        encoding="utf-8",
        errors="ignore"
    )
    
    # Logic that actually converts plain files into LangChain Documents
    document = Document(
        # main content
        page_content = text, 
        metadata = {
            "source": file_path,
            "loader":"txt_loader",
            "file_type": "txt"
        },
        
        # Unique identifier trait for traceability and answer attribution.
        id=file_path
    )
    
    return [document]