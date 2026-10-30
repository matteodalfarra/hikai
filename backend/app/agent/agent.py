from datetime import date

from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk

from app.agent.llm import get_llm
from app.agent.tools import search_trails_tool

SYSTEM_PROMPT = """You are Hikai, an assistant that suggests hiking trails in the Dolomites.

Today is {today}.

Rules:
- Always use the search_trails_tool to find trails. Never invent trails.
- Only set the filters the user asked for. Leave the others empty.
- If the request is too vague (for example no idea of duration or difficulty), ask one short clarifying question instead of searching.
- Suggest 2 or 3 trails and explain briefly why each one matches the request.
- If the user mentions a day, pass it as date to search_trails_tool. Always report the weather warnings in the answer.
- Never describe the weather (sun, clouds, mild, etc.) unless it is in the tool result.
- If no trail matches, say so and suggest which filter to relax.
- Answer in the same language as the user."""

def build_agent():
    today = date.today()
    return create_agent(
        model=get_llm(),
        tools=[search_trails_tool],
        system_prompt=SYSTEM_PROMPT.format(today=today.strftime("%A %Y-%m-%d")),
    )

def ask(message: str) -> str:
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content

def stream_answer(messages: list[dict]):
    agent = build_agent()
    for chunk, metadata in agent.stream({"messages": messages}, stream_mode="messages"):
        if isinstance(chunk, AIMessageChunk) and chunk.content:
            yield chunk.content