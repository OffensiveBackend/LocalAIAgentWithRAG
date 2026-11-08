"""
markdown_loader.py

ROLE
----
Load Markdown files.

Contract
--------
Input:
    Markdown file

Output:
    List[Document]
"""

from pathlib import Path

from langchain_core.documents import Document


def load(file_path: str) -> list[Document]:

    with open(file_path, "r", encoding="utf-8") as file:

        text = file.read()

    return [

        Document(

            page_content=text,

            metadata={

                "source": file_path,

                "file_name": Path(file_path).name,

                "file_type": "md",

                "loader": "markdown_loader"

            },

            id=Path(file_path).stem

        )

    ]