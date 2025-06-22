from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from app.services import search, ai, refine

app = FastAPI()

# Add error handling
@app.post("/search")
async def search_api(request: SearchRequest):
    try:
        results = await search.search_google(request.query, request.max_results)
        return [SearchResult(**item) for item in results]
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")

# Add streaming for AI responses
@app.post("/ask")
async def ask_ai_streaming(request: AIRequest):
    async def generate():
        async for chunk in ai.generate_ai_response_stream(request):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# Auto-refine queries before search
@app.post("/smart-search")
async def smart_search(request: SearchRequest):
    refined = await refine.refine_query(request.query)
    results = await search.search_google(refined, request.max_results)
    return {
        "refined_query": refined,
        "results": [SearchResult(**item) for item in results]
    }