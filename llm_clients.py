import httpx
import google.generativeai as genai

async def call_llm(provider: str, api_key: str, prompt: str) -> str:
    provider = provider.lower().strip()

    if provider == "openai":
        return await _call_openai(api_key, prompt)
    elif provider == "anthropic":
        return await _call_anthropic(api_key, prompt)
    elif provider == "gemini":
        return await _call_gemini(api_key, prompt)
    elif provider == "openrouter":
        return await _call_openrouter(api_key, prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


async def _call_openai(api_key: str, prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1200
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


async def _call_anthropic(api_key: str, prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    body = {
        "model": "claude-opus-4-20250514",
        "max_tokens": 1200,
        "messages": [{"role": "user", "content": prompt}]
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        return r.json()["content"][0]["text"]


async def _call_gemini(api_key: str, prompt: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = await model.generate_content_async(prompt)
    return response.text


async def _call_openrouter(api_key: str, prompt: str) -> str:
    url = "https://aipipe.org/openrouter/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openai/gpt-4o",  # You can change to any model supported by OpenRouter
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1200
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
