"""
code_loader.py

ROLE
----
Load source code files.

Supported
---------
.py
.js
.ts
.java
.cpp
.c
.cs
.html
.css
.json
.xml

Contract
--------
Input:
    Source code file

Output:
    List[Document]
"""

from pathlib import Path

from langchain_core.documents import Document


def load(file_path: str) -> list[Document]:

    with open(file_path, "r", encoding="utf-8") as file:

        code = file.read()

    extension = Path(file_path).suffix.replace(".", "").lower()

    return [

        Document(

            page_content=code,

            metadata={

                "source": file_path,

                "file_name": Path(file_path).name,

                "file_type": extension,

                "loader": "code_loader"

            },

            id=Path(file_path).stem

        )

    ]