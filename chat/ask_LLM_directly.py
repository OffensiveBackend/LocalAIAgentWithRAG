from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
        
model = OllamaLLM(model="llama3.2")
        
template = """
==============================
Conversation History
==============================
{conversation_history}

Use the conversation history ONLY to understand follow-up questions and
references such as:
- it
- they
- those
- earlier
- previous answer

Do NOT use conversation history as factual evidence.

==============================
Current Question
==============================
{query_from_user}
"""


prompt = ChatPromptTemplate.from_template(template)

chain = prompt | model