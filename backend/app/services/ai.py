import openai
from app.config import settings
from app.models import AIRequest, AIResponse

openai.api_key = settings.openai_api_key

async def generate_ai_response(request: AIRequest) -> AIResponse:
    search_summary = "\n".join([f"- {item.title}: {item.snippet}" for item in request.search_results])

    prompt = f"""
    You are an AI reasoning assistant.
    Question: {request.query}
    Search Results:
    {search_summary}

    Analyze the search results carefully.
    Step-by-step, explain your reasoning and provide a final answer.
    """

    response = await openai.ChatCompletion.acreate(
        model=settings.model,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content.strip()

    return AIResponse(answer=answer, reasoning=answer)
