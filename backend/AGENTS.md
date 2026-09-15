# Vending Machine Backend

This directory contains the Python backend for the VendingMachine project. It uses a `src/` layout, LangGraph for orchestration, and OpenAI through LangChain.

## Project Structure

```text
.
|-- requirements.txt              Runtime dependencies
|-- README.md                     Setup and run commands
|-- .env.example                  Environment variable template
|-- prompts/
|   `-- VENDING_MACHINE.md        Customer-facing vending agent prompt
|-- tests/
|   |-- test_ai_config.py         AI configuration and provider tests
|   |-- test_conversations.py     Conversation manager tests
|   |-- test_conversation_api.py  FastAPI conversation API tests
|   |-- test_tools.py             Vending tool tests
|   `-- test_tool_agent.py        Tool-agent graph tests
|-- src/vending_machine/
|   |-- main.py                   FastAPI application entry point
|   |-- conversations.py          In-memory streaming conversation management
|   |-- prompts.py                Prompt file loading and template rendering
|   |-- tools.py                  Vending inventory and purchase tools
|   |-- api/
|   |   |-- conversations.py       Streaming conversation routes
|   |   |-- router.py              Top-level HTTP router
|   |   `-- schemas.py             HTTP request and response schemas
|   |-- ai/
|   |   |-- config.py              Environment-backed model settings
|   |   `-- providers.py           Provider adapters, currently OpenAI
|   |-- agents/
|   |   |-- base.py                Provider-neutral AgentDefinition
|   |   `-- vending_machine.py     Vending agent definition and graph factory
|   `-- graphs/
|       `-- tool_agent.py          Reusable assistant-to-tools LangGraph loop
```

## Where To Make Changes

- Add or change an AI provider in `src/vending_machine/ai/providers.py`.
- Add or change HTTP routes in `src/vending_machine/api/`.
- Add a new domain agent under `src/vending_machine/agents/`.
- Reuse `build_tool_agent_graph` for agents that follow the assistant-to-tools pattern.
- Keep provider SDK imports out of domain agent modules.
- Add agent-specific prompt templates under `prompts/` and load them through `prompts.py`.
- Use `AI_*` variables for provider-neutral model settings and credentials.
- Keep conversations server-local and use `VENDING_CURRENCY` for their configured currency.
- Do not expose conversation history or LangGraph state through the API.
- Keep conversation API tests offline by mocking graph construction and streamed output.

The real `.env` contains secrets and is ignored by Git. Use `.env.example` for the supported variable names. Do not print or commit secret values.

## Common Commands

### Starting The Dev Server

From this directory:

```cmd
set PYTHONPATH=src
venv\Scripts\python.exe -m uvicorn vending_machine.main:app --reload
```
