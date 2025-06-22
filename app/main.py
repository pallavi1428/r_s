from fastapi import FastAPI
from app.services.search import search_google
from app.services.ai import generate_ai_response
from app.services.refine import refine_query
from app.models import SearchRequest, SearchResult, AIRequest, AIResponse, RefineRequest, RefineResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to rSearch FastAPI"}

@app.post("/search", response_model=list[SearchResult])
async def search(request: SearchRequest):
    results = await search_google(request.query, request.max_results)
    return [SearchResult(**item) for item in results]

@app.post("/refine", response_model=RefineResponse)
async def refine(request: RefineRequest):
    refined_query = await refine_query(request.query)
    return RefineResponse(refined_query=refined_query)

@app.post("/ask", response_model=AIResponse)
async def ask_ai(request: AIRequest):
    return await generate_ai_response(request)
