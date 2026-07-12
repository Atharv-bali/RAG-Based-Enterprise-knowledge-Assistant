<<<<<<< HEAD
# Enterprise Knowledge Assistant - Code Architecture

This repository contains an Advanced Enterprise Knowledge Assistant built using a multi-agent, self-correcting Retrieval-Augmented Generation (RAG) system. The application is powered by a **FastAPI** backend and a custom HTML5 dark-themed frontend dashboard.

---

## System Architecture & Connections

The following diagram illustrates how the frontend components, web server, and the core RAG system are connected:

```mermaid
graph TD
    %% Client
    subgraph Frontend Interface
        UI["frontend/index.html (Dark Dashboard)"]
    end

    %% Server
    subgraph FastAPI Stack
        App["app/main.py (FastAPI App)"]
        Routes["app/api/routes.py (Routes & Endpoints)"]
        Service["app/services/rag_service.py (Business Layer)"]
        Models["app/models/ (Pydantic Request/Response validation)"]
    end

    %% Core pipeline
    subgraph Core RAG Pipeline (Shared)
        RAG_Core["agents/self_correcting_rag.py"]
        Gen_Agent["agents/generator_agent.py"]
        Eval_Agent["agents/evaluator_agent.py"]
        Retrieval["retrieval/hybrid_retrieval.py"]
    end

    %% Connections
    UI -->|1. HTTP /query (Ask question)| App
    UI -->|2. HTTP /upload-pdf (Ingest document)| App
    UI -->|3. HTTP /health & /metrics| App
    
    App --> Routes
    Routes -->|Validates requests| Models
    Routes --> Service
    Service -->|Calls query()| RAG_Core

    %% RAG Pipeline internal flow
    RAG_Core -->|1. Search| Retrieval
    RAG_Core -->|2. Generate| Gen_Agent
    RAG_Core -->|3. Evaluate verdict| Eval_Agent
    Eval_Agent -.->|If FAIL: retry up to 3x with wider search| RAG_Core
```

---

## 1. FastAPI Web Server (`app/` folder)

The `app/` folder contains the FastAPI application structured around modern Python clean architecture practices (dependency separation, model validation, and custom middlewares).

### Folder Structure & Components

*   **[`app/main.py`](file:///c:/Users/LENOVO/Desktop/Rag2/app/main.py)**: The application entrypoint.
    *   Initializes the `FastAPI` instance.
    *   Registers a logging middleware (`LoggingMiddleware`) and global exception handlers.
    *   Serves the static file `frontend/index.html` directly at `/`.
    *   Includes routers from `app/api/routes.py`.
*   **[`app/api/routes.py`](file:///c:/Users/LENOVO/Desktop/Rag2/app/api/routes.py)**: Exposes API endpoints for client consumption:
    *   `POST /query`: Processes user questions. Uses Pydantic to validate input question length and checks against empty inputs.
    *   `POST /upload-pdf`: Accepts a uploaded PDF document, parses its text contents, writes them to `data/parsed_docs/`, and invokes the chunker ingestion script (`ingestion.chunker.main`) to automatically rebuild the database vector index.
    *   `GET /health`: Diagnoses if Ollama is running (`http://localhost:11434`) and checks if the vector store chunks (`output/child_chunks.json`) are accessible.
    *   `GET /metrics`: Serves application runtime performance metrics (Uptime, latency averages, total query counts).
*   **[`app/models/`](file:///c:/Users/LENOVO/Desktop/Rag2/app/models/)**:
    *   `request_models.py`: Validates that incoming queries are not empty/whitespace and fit size bounds (1–1000 characters).
    *   `response_models.py`: Enforces output structure formatting (`status` and `answer`).
*   **[`app/services/rag_service.py`](file:///c:/Users/LENOVO/Desktop/Rag2/app/services/rag_service.py)**: Acts as the service abstraction layer between API controllers and the core RAG logic.
*   **[`app/utils/`](file:///c:/Users/LENOVO/Desktop/Rag2/app/utils/)**:
    *   `exceptions.py`: Defines API errors and maps handlers to HTTP status codes.
    *   `logger.py`: Custom logging decorators, logging middleware, and log setups.
    *   `metrics.py`: Tracks query counts, latency averages, and error occurrence rates.

---

## 2. Frontend Client Dashboard (`frontend/` folder)

The `frontend/` folder contains the dark-themed user dashboard.

### Key Components

*   **[`frontend/index.html`](file:///c:/Users/LENOVO/Desktop/Rag2/frontend/index.html)**:
    *   **UI Layout**: Responsive grid containing:
        *   **Sidebar**: Houses Ollama/Vector health checks, real-time performance indicators (queries processed, average processing latency, success rate), and a PDF Upload area.
        *   **Main Chat Area**: Interactive interface with animated typing states for agent execution loops and structured chat message bubbles rendering quality evaluation check tags (`PASS` / `FAILED`).
    *   **Under the Hood**: Uses asynchronous browser `fetch` calls to communicate with the FastAPI server endpoints `/query`, `/upload-pdf`, `/health`, and `/metrics`.
=======
## Objective
The aim of this project is to create a system where users can upload documents and ask questions about them. The system provides relevant answers without requiring users to read the complete PDF files. It also tries to reduce hallucinations by generating answers only from the uploaded documents and verifying the response before showing it to the user.

## Architecture
<img width="997" height="716" alt="image" src="https://github.com/user-attachments/assets/2ae1c81d-45ad-4def-9f50-8252a1fb6327" />

## Future Works

1. Instead of doing chunking every time, the system can save the chunks and embeddings after the document is uploaded. The chunks will remain stored until the user deletes the document, making retrieval faster.

2. The system can support more file types such as Word documents, PowerPoint presentations, images, and scanned PDFs so that users can ask questions from different kinds of files.

3. The system can be improved to handle multiple documents at the same time and provide better answers by combining information from different documents.
>>>>>>> 77c6d84633b6d8d436013ee36a49d21ba840c336
