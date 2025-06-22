import openai
from app.config import settings
from app.models import AIRequest, AIResponse

openai.api_key = settings.openai_api_key

async def generate_ai_response(request: AIRequest) -> AIResponse:
    prompt = f"""
    Question: {request.query}
    Search Results: {request.search_results}
    Analyze the results and provide a detailed answer with reasoning (Chain-of-Thought).
    """
    
    response = await openai.ChatCompletion.acreate(
        model=settings.model,
        messages=[{"role": "user", "content": prompt}],
    )
    
    answer = response.choices[0].message.content
    return AIResponse(answer=answer, reasoning=answer)  # Simplified