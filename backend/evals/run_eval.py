import json
import time
from datetime import datetime
from pathlib import Path

from langchain_core.messages import AIMessage

from app.agent.agent import build_agent
from app.core import config

EVALS_DIR = Path(__file__).parent
DATASET_PATH = EVALS_DIR / "dataset.json"
RESULTS_DIR = EVALS_DIR / "results"

TRAIL_KEYWORDS = {
    "tre-cime-loop": "tre cime",
    "lago-di-braies-loop": "braies",
    "lago-di-carezza": "carezza",
    "seceda-col-raiser": "seceda",
    "lago-di-sorapis": "sorapis",
    "cinque-torri-loop": "cinque torri",
    "piz-boe-sass-pordoi": "piz bo",
    "ferrata-brigata-tridentina": "tridentina",
}

def find_mentioned_trails(answer: str) -> list[str]:
    answer = answer.lower()
    return [trail_id for trail_id, keyword in TRAIL_KEYWORDS.items() if keyword in answer]

def get_used_filters(messages: list) -> set[str]:
    used = set()
    for message in messages:
        if not isinstance(message, AIMessage):
            continue
        for call in message.tool_calls:
            for key, value in call["args"].items():
                if value is None or (key == "needs_hut" and value is False):
                    continue
                used.add(key)
    return used

def count_tokens(messages: list) -> tuple[int, int]:
    input_tokens = 0
    output_tokens = 0
    for message in messages:
        if isinstance(message, AIMessage) and message.usage_metadata:
            input_tokens += message.usage_metadata["input_tokens"]
            output_tokens += message.usage_metadata["output_tokens"]
    return input_tokens, output_tokens

def run_case(agent, case: dict) -> dict:
    start = time.perf_counter()
    result = agent.invoke({"messages": [{"role": "user", "content": case["request"]}]})
    latency = time.perf_counter() - start

    messages = result["messages"]
    answer = messages[-1].content
    mentioned = find_mentioned_trails(answer)
    invented = sorted(get_used_filters(messages) - set(case["allowed_filters"]))
    input_tokens, output_tokens = count_tokens(messages)

    trails_ok = all(trail in mentioned for trail in case["expected_trails"])
    safe = not any(trail in mentioned for trail in case["forbidden_trails"])
    question_ok = "?" in answer if case["expect_question"] else True

    return {
        "id": case["id"],
        "answer_ok": trails_ok and safe and question_ok,
        "filters_ok": not invented,
        "passed": trails_ok and safe and question_ok and not invented,
        "trails_ok": trails_ok,
        "safe": safe,
        "question_ok": question_ok,
        "invented_filters": invented,
        "mentioned_trails": mentioned,
        "latency_s": round(latency, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "answer": answer,
    }

def main():
    cases = json.loads(DATASET_PATH.read_text())
    agent = build_agent()
    results = []

    print(f"Model: {config.OLLAMA_MODEL}\n")
    for case in cases:
        result = run_case(agent, case)
        results.append(result)
        answer = "OK " if result["answer_ok"] else "BAD"
        filters = "OK " if result["filters_ok"] else "BAD"
        print(f"answer={answer} filters={filters}  {case['id']:<28} {result['latency_s']}s  invented={result['invented_filters']}")

    total = len(results)
    passed = sum(r["passed"] for r in results)
    unsafe = sum(not r["safe"] for r in results)
    with_invented = sum(bool(r["invented_filters"]) for r in results)
    avg_latency = sum(r["latency_s"] for r in results) / total
    
    answers_ok = sum(r["answer_ok"] for r in results)
    filters_ok = sum(r["filters_ok"] for r in results)
    print(f"\nCorrect answers: {answers_ok}/{total}")
    print(f"Clean filters: {filters_ok}/{total}")
    print(f"Unsafe answers: {unsafe}")
    print(f"Cases with invented filters: {with_invented}")
    print(f"Avg latency: {avg_latency:.2f}s")

    RESULTS_DIR.mkdir(exist_ok=True)
    model_name = config.OLLAMA_MODEL.replace(":", "-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    output_path = RESULTS_DIR / f"{model_name}-{timestamp}.json"
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved to {output_path}")

if __name__ == "__main__":
    main()