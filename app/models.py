from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str

class RefineRequest(BaseModel):
    query: str

class RefineResponse(BaseModel):
    refined_query: str

class AIRequest(BaseModel):
    query: str
    search_results: List[SearchResult]

class AIResponse(BaseModel):
    answer: str
    reasoning: str
