from langchain.agents import create_agent

from app.agent.llm import get_llm
from app.agent.tools import search_trails_tool

SYSTEM_PROMPT = """You are Hikai, an assistant that suggests hiking trails in the Dolomites.

Rules:
- Always use the search_trails_tool to find trails. Never invent trails.
- If the request is too vague (for example no idea of duration or difficulty), ask one short clarifying question instead of searching.
- Suggest 2 or 3 trails and explain briefly why each one matches the request.
- If no trail matches, say so and suggest which filter to relax.
- Answer in the same language as the user.
- Only set the filters the user asked for. Leave the others empty."""

def build_agent():
    return create_agent(
        model=get_llm(),
        tools=[search_trails_tool],
        system_prompt=SYSTEM_PROMPT,
    )

def ask(message: str) -> str:
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content