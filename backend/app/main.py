# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import openai
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Union, List, Dict

load_dotenv()

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class SearchRequest(BaseModel):
    q: str
    mode: str = "web"
    gl: Optional[str] = "us"
    hl: Optional[str] = "en"

class RSearchRequest(BaseModel):
    searchTerm: str
    mode: str
    searchResults: Optional[List[Dict]] = None

# Endpoints
@app.post("/api/search")
async def search(request: SearchRequest):
    """Handle all search types (web, images, videos, etc.)"""
    try:
        endpoint = "https://google.serper.dev/search"
        if request.mode == "images":
            endpoint = "https://google.serper.dev/images"
        elif request.mode == "videos":
            endpoint = "https://google.serper.dev/videos"
        # Add other modes as needed

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                headers={"X-API-KEY": os.getenv("SERPER_API_KEY")},
                json={
                    "q": request.q,
                    "gl": request.gl,
                    "hl": request.hl,
                    "num": 10  # Default number of results
                }
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rsearch")
async def rsearch(request: RSearchRequest):
    """Handle AI-enhanced search results"""
    try:
        # If search results aren't provided, fetch them first
        if not request.searchResults:
            search_request = SearchRequest(q=request.searchTerm, mode=request.mode)
            search_results = await search(search_request)
            request.searchResults = search_results.get("organic", [])

        # Generate AI response
        prompt = f"""
        Question: {request.searchTerm}
        Search Results: {request.searchResults}
        
        Based on the above search results, please provide a comprehensive answer.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {"aiResponse": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_refinement(request: SearchRequest):
    """Handle search query refinement"""
    try:
        prompt = f"""
        Original query: {request.q}
        Please refine this search query to be more effective.
        Return only the refined query without any additional text.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "refined_query": response.choices[0].message.content,
            "explanation": "The query was refined to improve search results"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))