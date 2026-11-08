import pandas as pd
from langchain_core.documents import Document


# Outputs a list of LangChain Documents. List[Document]
def load( file_path: str):
    """Returns:
            List[Documents]
    """
    # Converts each row into a document.
    df = pd.read_csv(file_path)
    
    # List to contain the LangChain objects
    documents = []
    
    for i, row in df.iterrows():
        document = Document(
            
            page_content = row["Title"] + " " + row["Review"],
            
            metadata = {
                "rating": row["Rating"],
                "date":row["Date"],
                "loader": "csv_loader",
                "source": file_path,
                "file_type":"csv"
            },
            
            # Unique identifier for traceability and answer attribution.
            id = f"{file_path}_{i}"
        )
        
        documents.append(document)
    
    return documents