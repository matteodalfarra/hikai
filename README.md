# Hikai

Hikai (hike + AI) suggests hiking trails in the Dolomites from a plain description.

> "Domani vorrei fare un giro ad anello con rifugio, mezza giornata"

The agent turns the request into filters, searches a small trail catalog, checks the weather for that day and suggests two or three trails, explaining why they fit. If the request is too vague, it asks a question first.

Everything runs locally: the model runs on [Ollama](https://ollama.com), and no data leaves the machine except the weather request.

## How it works

```
user request
   │
   ▼
LLM (qwen3:14b) ──► search_trails_tool(filters, date)
                        │
                        ├─ filter the catalog        (plain Python)
                        ├─ apply the safety rules    (plain Python)
                        └─ add weather and warnings  (Open-Meteo + plain Python)
   │
   ▼
LLM writes the answer ──► streamed to the browser (SSE)
```

The LLM does two things: it understands the request and it explains the results. Everything else is normal, testable code.

## Design decisions

**Safety lives in code, not in the prompt.** A beginner never gets EE trails or via ferratas, even if they ask for one, because the difficulty limit is applied by `search_trails`, not by the model. If the experience is unknown, the code assumes beginner. When the limit kicks in, the tool tells the model why, so it can explain it to the user instead of just saying "no results".

**Warnings come from code too.** The code decides when there is a thunderstorm risk (thunderstorm codes or rain ≥ 50% between 12:00 and 18:00) or freezing temperatures. In early tests the model read "-4.5°C to 2.1°C" and wrote "mild temperatures", so now it gets a clear warning, not just numbers.

**The schema should make mistakes harmless.** The model kept inventing a filter `is_loop: false` ("only trails that are not loops"), which nobody ever asks for and which hid every easy trail. I replaced it with `loop_only: true/false`: a wrong `false` now does nothing. Changing the schema worked better than another prompt rule.

**One tool instead of two.** Weather used to be a separate tool, but the smaller model often skipped it and made up a forecast. Now the search tool adds the weather when a date is given, so it can't be forgotten.

**Stateless backend, streamed answers.** The frontend sends the whole conversation on every request, so the backend needs no database. Answers take 15-30 seconds on my machine, so they are streamed with Server-Sent Events.

## Evaluation

`backend/evals` runs the agent on a fixed set of requests and checks each answer with plain code, not with an LLM judge:

- **Correct answer:** the expected trails are in the answer, no forbidden trails, and a question when the request is vague
- **Clean filters:** the model only uses filters that the request asks for
- **Safety:** no EE or EEA trails for beginners
- **Latency** and **tokens**

Latest run, 10 requests:

| Model | Correct answers | Clean filters | Unsafe answers | Avg latency |
|---|---|---|---|---|
| qwen3:14b | 10/10 | 9/10 | 0 | 18.1 s |

Comparing models on the weather feature, with the same request and the real forecast:

| Model | Passes the date to the tool | Answer |
|---|---|---|
| qwen3:8b (3 runs) | never | made up "sunny, mild temperatures" 3/3 |
| qwen3:14b (2 runs) | always | reported the ice warning 2/2 |

That is why the default model is qwen3:14b, even though it is about 50% slower than qwen3:8b.

What these numbers can't tell you yet: 10 requests and one run per request are not enough. Results changed by one or two cases between identical runs, so small differences don't mean much. Growing the dataset is the next step.

Every result is saved in `backend/evals/results/`.

## Running it locally

You need [Docker](https://www.docker.com/), [Ollama](https://ollama.com), [uv](https://docs.astral.sh/uv/) and Node.js 22.

```bash
ollama pull qwen3:14b
make up
```

Open http://localhost:5173.

Ollama runs on the host, not in Docker: on a Mac, Docker can't use the GPU, so the model would be very slow inside a container. The backend reaches it at `host.docker.internal:11434`.

Other commands:

```bash
make test                   # backend tests
make lint                   # frontend lint and build
make eval                   # run the evals with qwen3:14b
make eval MODEL=qwen3:8b    # ... or with another model
make help                   # all commands
```

## Project structure

```
backend/
  app/
    agent/      LangChain agent, prompt and tools
    api/        FastAPI endpoints
    schemas/    Pydantic models
    services/   filters, safety rules, weather
  data/         trail catalog (JSON)
  evals/        eval dataset, script and results
  tests/
frontend/       React + TypeScript (Vite)
```

## Tests and CI

Every pull request runs the backend tests and the frontend lint and build on GitHub Actions. The tests never call the model or the network (the LLM and HTTP calls are replaced with fakes), so they run in under a second. The evals are different: they need Ollama and a real model, so I run them locally.

## Stack

Python, FastAPI, LangChain, Ollama (qwen3), Pydantic, pytest, React, TypeScript, Vite, Docker, GitHub Actions.

## Known limitations

- The catalog has only 8 trails, and durations, elevations and coordinates are approximate.
- The agent suggests mountain huts even when they are closed (most close from October to June).
- The check for clarifying questions looks for a "?", so it can miss a question written without one.
- Weather forecasts are available only up to 16 days ahead.

## Next steps

- More trails with verified data, and hut opening months
- A larger eval dataset, with several runs per request
- Remembering user preferences across conversations

## Data

Weather data by [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0).
