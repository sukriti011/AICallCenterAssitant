# Call Center AI Analysis Platform

Standalone multi-agent call center analysis system that converts conversations into structured summaries, quality scores, and routing decisions.

## What This Project Includes
- Multi-agent call analysis pipeline: Intake -> Transcription -> Summarization -> Quality Scoring -> Routing
- Transcript and audio upload support
- FastAPI service with structured response schemas
- Streamlit UI for interactive analysis and scenario demos
- Test suite for agents and API routes

## Tech Stack
- LangChain + LangGraph for orchestration
- OpenAI for chat, summarization, quality scoring, and transcription
- FastAPI for REST APIs
- Streamlit for demo UI

## Project Structure
```text
app/
  agents/
    call_center/
  api/routes/
    call_center.py
  core/
  ui/
tests/
infra/
```

## Quick Start
```bash
cp .env.example .env
# Set OPENAI_API_KEY in .env

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Optional UI (second terminal):
```bash
streamlit run app/ui/streamlit_app.py
```

Docker:
```bash
docker-compose up --build
```

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/call-center/chat | Conversational assistant endpoint |
| POST | /api/v1/call-center/analyze | Full analysis from transcript |
| POST | /api/v1/call-center/analyze/upload | Full analysis from uploaded audio |
| DELETE | /api/v1/call-center/session/{session_id} | Clear chat session memory |
| GET | /health | Health check |

## Notes
- This repository is scoped only to call center workflows.
- Document research / RAG modules were intentionally removed during migration.
