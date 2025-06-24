# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from fastapi import Request
from fastapi.responses import StreamingResponse
import json
import asyncio
from openai import OpenAI
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Union, List, Dict
import traceback

# Load environment variables FIRST
load_dotenv()

# Initialize OpenAI client AFTER loading environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
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
    searchResults: Optional[dict] = None
    prompt: Optional[str] = None

# Endpoints
@app.post("/api/search")
async def search(request: SearchRequest):
    try:
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

        params = {
            "q": request.q,
            "gl": request.gl,
            "hl": request.hl
        }

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

            return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rsearch")
async def rsearch(request: RSearchRequest):
    try:
        if not request.searchResults:
            search_request = SearchRequest(q=request.searchTerm, mode=request.mode)
            search_results = await search(search_request)
            request.searchResults = {
                "organic": search_results.get("organic", []),
                "knowledgeGraph": search_results.get("knowledgeGraph", None)
            }

        # 🛠 Extract the organic results properly:
        organic_results = request.searchResults.get("organic", [])

        prompt = f"""
        Question: {request.searchTerm}
        Search Results: {organic_results}

        Based on the above search results, please provide a comprehensive answer.
        """

        async def stream_openai():
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "stream": True
            }

            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[len("data: "):]
                            if data == "[DONE]":
                                break
                            chunk = json.loads(data)
                            content = chunk["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                yield content

        return StreamingResponse(stream_openai(), media_type="text/plain")

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/query")
async def query_refinement(request: SearchRequest):
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

@app.get("/")
async def root():
    return {"message": "API is running"}
