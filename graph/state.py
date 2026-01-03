from typing import TypedDict, Annotated, List
import operator

class GraphState(TypedDict):
    question: str
    documents: Annotated[List, operator.add]
    generation: str

    is_relevant: str
    is_grounded: str

    retry_generation_count: int
    kb_retry_count: int
    kb_enriched: bool

    steps: Annotated[List[str], operator.add]
