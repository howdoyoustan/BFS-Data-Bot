from langchain_core.prompts import ChatPromptTemplate

hallucination_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a hallucination detector for a Banking & Financial Services
Apache Spark incident analysis assistant.

RULES:
- Mark NO if the answer includes ANY claim not directly supported
  by the provided documents.
- Mark NO if the answer infers causes, configurations, or fixes
  not explicitly stated in the logs or docs.
- Mark YES only if EVERY statement can be traced to the documents.

IMPORTANT:
- Summarization is allowed
- Rephrasing is allowed
- Logical deduction WITHOUT evidence is NOT allowed

Return ONLY 'yes' or 'no'."""),
    ("human",
     "Documents:\n{documents}\n\nAnswer:\n{generation}")
])

RE_WRITE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a technical query optimizer for Spark and BFS data pipelines. "
               "Your goal is to take a failing user query and rewrite it into a specific, "
               "technical search term optimized for logs and documentation."),
    ("human", "Original Query: {question}\n"
              "The current results were insufficient. Formulate an improved, "
              "highly specific technical search query.")
])

RETRY_SYSTEM_PROMPT = """
You are re-generating an answer after a hallucination was detected.

STRICT RULES:
1. Remove ANY claim not explicitly supported by the provided context.
2. Do NOT infer causes, fixes, or configurations.
3. If evidence is incomplete, respond exactly with:
   "I don't know - The current knowledge base is insufficient to answer this."
4. Prefer quoting logs or documents over explanation.
5. Do NOT repeat the previous answer if unsure.
"""


