from langchain_ollama import ChatOllama

from app.core import config

def get_llm() -> ChatOllama:
    return ChatOllama(
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL, 
        temperature=0,
        reasoning=False,
    )