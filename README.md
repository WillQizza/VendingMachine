# Vending Machine

Vending Machine is a full-stack application based off of [Project Vend](https://www.anthropic.com/research/project-vend-1) by Anthropic. It allows for purchasing virtual items offered on the vending machine through an AI Agent, where item selection and restocking is also orchestrated through other AI Agents.

## Stack

- Backend: Python, FastAPI, LangGraph, LangChain, and OpenAI
- Frontend: Angular, TypeScript, and Vitest

## Repository Layout

```text
.
|-- backend/     FastAPI service, agent graph, prompts, and backend tests
|-- frontend/    Angular application and frontend tests
```

## Prerequisites

- Python 3.10 or newer
- Node.js with npm
- An OpenAI API key for the backend

## Backend Setup

From the repository root, run:

```cmd
cd backend
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

Set the backend values in `backend/.env`. The supported settings are:

- `AI_PROVIDER`
- `AI_API_KEY`
- `AI_MODEL`
- `AI_TEMPERATURE`
- `AI_MAX_TOKENS`
- `VENDING_CURRENCY`

Start the backend from the `backend` directory:

```cmd
set PYTHONPATH=src
venv\Scripts\python.exe -m uvicorn vending_machine.main:app --reload
```

The service runs at `http://localhost:8000`. FastAPI's interactive API documentation is available at `http://localhost:8000/docs`.

## Frontend Setup

From the repository root, run:

```cmd
cd frontend
npm install
npm start
```

The Angular development server runs at `http://localhost:4200`.

Run the backend and frontend in separate terminals during development.

## API Overview

- `GET /` returns a service health response.
- `POST /conversations` creates a conversation.
- `POST /conversations/{conversation_id}/messages` streams assistant output as server-sent events.

## Testing And Builds

Run backend tests from `backend`:

```cmd
set PYTHONPATH=src
venv\Scripts\python.exe -m unittest discover -s tests
```

Run frontend tests and a production build from `frontend`:

```cmd
npm test
npm run build
```

Do not commit `backend/.env` or any other secret values.
