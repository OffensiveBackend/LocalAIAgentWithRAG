"""
formatter.py

ROLE:
    Convert retrieved LangChain Document objects into a clean,
    human-readable context string for the LLM.

WHY THIS MODULE EXISTS
----------------------
The retriever returns a list[Document].

Those Document objects contain Python-specific information
(Document(...), metadata dictionaries, ids, etc.) that is useful for
developers but not ideal for an LLM prompt.

This formatter acts as the translation layer between the Retriever and
the Prompt.

Architecture:

Retriever
    ↓
List[Document]
    ↓
formatter.py
    ↓
Formatted Context (str)
    ↓
Prompt
    ↓
LLM
"""

from langchain_core.documents import Document


def format_documents(documents: list[Document]) -> str:
    """
    Convert retrieved LangChain Documents into a prompt-friendly string.

    Parameters
    ----------
    documents : list[Document]
        Retrieved documents from the vector store.

    Returns
    -------
    str
        Nicely formatted context for the prompt.
    """

    if not documents:
        return "No relevant context was retrieved."

    formatted_documents = []

    total_documents = len(documents)

    for i, document in enumerate(documents, start=1):

        metadata = document.metadata or {}

        source = metadata.get("source", "Unknown")
        chunk_id = metadata.get("chunk_id")
        total_chunks = metadata.get("total_chunks")
        chunking_strategy = metadata.get("chunking_strategy")

        header = [
            "=" * 80,
            f"DOCUMENT {i} OF {total_documents}",
            "=" * 80,
            f"Source: {source}",
        ]

        # Optional metadata
        if chunk_id is not None and total_chunks is not None:
            header.append(
                f"Chunk: {chunk_id + 1}/{total_chunks}"
            )

        if chunking_strategy:
            header.append(
                f"Chunking Strategy: {chunking_strategy}"
            )

        # Preserve any other metadata without hardcoding keys.
        ignored_keys = {
            "source",
            "chunk_id",
            "total_chunks",
            "chunking_strategy",
        }

        for key, value in metadata.items():

            if key not in ignored_keys:
                header.append(
                    f"{key.capitalize()}: {value}"
                )

        header.append("")
        header.append("Content:")
        header.append(document.page_content.strip())

        formatted_documents.append(
            "\n".join(header)
        )

    return "\n\n".join(formatted_documents)