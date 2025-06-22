from fastapi import FastAPI
from app.services.search import search_google
from app.services.ai import generate_ai_response
from app.models import SearchRequest, AIRequest, AIResponse

app = FastAPI()

@app.post("/search", response_model=list[SearchResult])
async def search(request: SearchRequest):
    results = await search_google(request.query, request.max_results)
    return [SearchResult(**item) for item in results]

@app.post("/ask", response_model=AIResponse)
async def ask_ai(request: AIRequest):
    return await generate_ai_response(request)