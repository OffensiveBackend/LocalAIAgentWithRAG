"""
pdf_loader.py

ROLE
----
Load PDF files and convert them into LangChain Document objects.

Contract
--------
Input:
    PDF file path

Output:
    List[Document]

NOTE
----
Each PDF page becomes one Document.

The chunker will later split pages into smaller chunks.
"""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load(file_path: str) -> list[Document]:

    loader = PyPDFLoader(file_path)

    pages = loader.load()

    documents = []

    for page_number, page in enumerate(pages):

        document = Document(

            page_content=page.page_content,

            metadata={

                "source": file_path,

                "file_name": Path(file_path).name,

                "file_type": "pdf",

                "loader": "pdf_loader",

                "page": page_number + 1

            },

            id=f"{Path(file_path).stem}_page_{page_number + 1}"

        )

        documents.append(document)

    return documents