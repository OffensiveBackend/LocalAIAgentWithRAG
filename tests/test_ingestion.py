from ingestion.ingestion_pipeline import ingest

# Test the loader if txt files r being converted into langchain documents
documents = ingest([
    "data/realistic_restaurant_reviews.csv",
    "data/restaurant_information.txt"
])

# Number of ingested documents
number_of_made_langchain_documents = len(documents)
print(number_of_made_langchain_documents)

for doc in documents:
    print(
        doc.page_content
    )