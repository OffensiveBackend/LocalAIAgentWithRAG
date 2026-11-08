from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# MAke an ollama object
model = OllamaLLM(
    model="llama3.2" # specify model in use
)

template = """
You are an expert assistant for answering questions about a pizza restaurant.

==============================
Retrieved Context
==============================

{reviews}

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

==============================
Instructions
==============================

Information priority:

1. Retrieved Context (highest priority)
2. Conversation History (reference resolution only)

When answering:

• Respond in the same language used in the questio by the user(always obey, highest priority).
• Base factual claims only on the retrieved context.
• Compare evidence from multiple retrieved documents whenever possible.
• Acknowledge conflicting evidence.
• Clearly distinguish supported facts from missing information.
• If the retrieved context does not contain enough information, explicitly say so.
• Never invent facts.
• Answer only the current question unless the user explicitly asks you to revisit earlier topics.
"""

# pass configurations into model.
# Define how the task is presented to the model.
prompt = ChatPromptTemplate.from_template(
    template
)

# Construct a chain. Invokes all concerned processes to make the model work
# In this chain we: submited question, model sends feedback
chain = prompt | model

# Current Architecture:
# LLM Configuration > Prompt > Chain