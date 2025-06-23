import openai
from app.config import settings

openai.api_key = settings.openai_api_key

async def refine_query(query: str) -> str:
    prompt = f"Improve and make this search query more specific: {query}"

    response = await openai.ChatCompletion.acreate(
        model=settings.model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
