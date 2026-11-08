"""
docx_loader.py

ROLE
----
Load Microsoft Word (.docx) files and convert them into
LangChain Document objects.

Contract
--------
Input:
    DOCX file

Output:
    List[Document]

NOTE
----
The whole document becomes one Document.

The chunker will split it later.
"""

from pathlib import Path

from docx import Document as WordDocument
from langchain_core.documents import Document


def load(file_path: str) -> list[Document]:

    word_document = WordDocument(file_path)

    text = "\n".join(

        paragraph.text

        for paragraph in word_document.paragraphs

        if paragraph.text.strip()

    )

    return [

        Document(

            page_content=text,

            metadata={

                "source": file_path,

                "file_name": Path(file_path).name,

                "file_type": "docx",

                "loader": "docx_loader"

            },

            id=Path(file_path).stem

        )

    ]