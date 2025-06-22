from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str

class AIRequest(BaseModel):
    query: str
    search_results: list[SearchResult]

class AIResponse(BaseModel):
    answer: str
    reasoning: str  # Chain-of-Thought