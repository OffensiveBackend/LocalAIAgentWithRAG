from chat.llm import chain
from knowledge.knowledge_services import search  # For semantic search.

# Series of TEST questions
questions = [
    "What is the restaurant's name?",
    "What are the opening hours?",
    "Which payment methods are accepted?",
    "Does the restaurant have parking?",
    "Is the restaurant wheelchair accessible?",
    "What do customers complain about the most?",
    "When can I visit the restaurant if I also want to know what customers think about the delivery service?",
    "What sustainability practices does the restaurant follow, and do customer reviews mention them?",
    "If I want to host a birthday party there, what do customer reviews suggest I should expect?"
]

def test_run002():
    for question in questions:
        print("\n\n"+"_"*156)
        print(f"Question: {question}")
        print("\n\n")
        
        reviews = search(question)
        
        answer = chain.invoke({
            "reviews": reviews,
            "query_from_user":question
            })
        
        print(answer)

# Run the Test002
test_run002()