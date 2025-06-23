# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from openai import OpenAI
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
    """Handle all search types with proper formatting"""
    try:
        # Determine the endpoint based on search mode
        endpoint_map = {
            "images": "https://google.serper.dev/images",
            "videos": "https://google.serper.dev/videos",
            "places": "https://google.serper.dev/places",
            "news": "https://google.serper.dev/news",
            "shopping": "https://google.serper.dev/shopping",
            "scholar": "https://google.serper.dev/search",
            "patents": "https://google.serper.dev/search",
            "web": "https://google.serper.dev/search",
            "search": "https://google.serper.dev/search"
        }
        
        endpoint = endpoint_map.get(request.mode, "https://google.serper.dev/search")
        
        # Prepare request parameters
        params = {
            "q": request.q,
            "gl": request.gl,
            "hl": request.hl
        }
        
        # Add special parameters for scholar and patents
        if request.mode == "scholar":
            params["type"] = "scholar"
            params["engine"] = "google_scholar"
        elif request.mode == "patents":
            params["type"] = "patents"
            params["engine"] = "google"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                headers={"X-API-KEY": os.getenv("SERPER_API_KEY")},
                json=params
            )
            
            # Return raw data - let frontend handle formatting
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
        
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o",
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
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "refined_query": response.choices[0].message.content,
            "explanation": "The query was refined to improve search results"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Add this to your FastAPI app
@app.get("/")
async def root():
    return {"message": "API is running"}