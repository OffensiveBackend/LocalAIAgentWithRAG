from langchain_ollama.llms import OllamaLLM

model = OllamaLLM(
    model="llama3.2"
)

while True:
    query_from_user = input("Ask your question: ")
    
    # talk to an LLM    
    response_from_ai = model.invoke(query_from_user)
    
    print(response_from_ai)
    
# ARCHITECTURE:
# user -> prompt -> langChain -> Ollama -> llama(model) -> response.