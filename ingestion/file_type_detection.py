""""
ROLE:
    This file detects the file extension the decides which loader should process a  file.
"""

from pathlib import Path

from ingestion.loaders import (
    code_loader,
    csv_loader,
    docx_loader,
    markdown_loader,
    pdf_loader,
    txt_loader,
)

# Catalogue of available loaders.
LOADER_MAP = {

    ".csv": csv_loader,

    ".txt": txt_loader,

    ".pdf": pdf_loader,

    ".docx": docx_loader,

    ".md": markdown_loader,

    ".py": code_loader,
    ".js": code_loader,
    ".ts": code_loader,
    ".java": code_loader,
    ".cpp": code_loader,
    ".c": code_loader,
    ".cs": code_loader,
    ".html": code_loader,
    ".css": code_loader,
    ".json": code_loader,
    ".xml": code_loader

}


# Logic for deciding btwn loaders
def choose_loader(file_path: str):
    
    # Detect the file extension
    extension = Path(file_path).suffix.lower()
    
    # Logic to actually decide on exact file extension
    loader = LOADER_MAP.get(extension)
    
    # Edgecase handling
    if loader is None:
        raise ValueError(
            f"Unsurpported file type: {extension}"
        )
    return loader