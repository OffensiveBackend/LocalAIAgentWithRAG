from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

from knowledge.vector import retriever

model = OllamaLLM(
    model="llama3.2"
)

template="""
You are an expert on this pizza restaraunt.

Use ONLY the reviews below to answer.

Reviews:
{reviews}

Question:
{question}

If the reviews do not contain enough information, say so.
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

questions = [
    "Do customers generally recommend the gluten-free pizza?",
    "What do customers complain about the most?",
    "Would this restaurant be good for a vegan family?",
    "What evidence suggests good customer service?",
    "What are the restaurant's opening hours?"
]

for i, question in enumerate(questions, start=1):
    
    print("="*80)
    print(f"TEST {i}")
    print(f"QUESTION: {question}")
    
    docs = retriever.invoke(question)
    
    reviews = "\n\n".join(
        doc.page_content
        for doc in docs
    )
    
    answer = chain.invoke({
        "reviews": reviews,
        "question":question
    })
    
    print("\nRetrieved Documents:", len(docs))
    
    # Did the answer mention the expected concepts?
    print("\n\nRetrieved Context:")
    print("-"*80)
    print(reviews)
    
    # Did it admit uncertainty when appropriate?
    # Did hallucinate unsupported facts?
    print("\nLLM response:\n")
    print("-"*80)
    print(answer)
    print( )