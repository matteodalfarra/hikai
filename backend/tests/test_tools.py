from app.agent.tools import search_trails_tool

def test_tool_returns_trails():
    result = search_trails_tool.invoke({"area": "Tre Cime"})
    assert "Tre Cime di Lavaredo loop" in result

def test_tool_says_when_nothing_found():
    result = search_trails_tool.invoke({"area": "Nowhere"})
    assert "No trails found" in result

def test_tool_adds_safety_note_for_beginner():
    result = search_trails_tool.invoke({"experience": "beginner", "max_difficulty": "EEA"})
    assert "Safety note" in result