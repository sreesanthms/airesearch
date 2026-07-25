# ResearchPilot

> AI-powered research paper analysis using Retrieval-Augmented Generation (RAG).

Upload a research paper (PDF), ask questions about it, and receive grounded answers with source citations — powered by Google Gemini 2.5 Flash.

---

## Tech Stack

| Layer      | Technology                                          |
|-----------|-----------------------------------------------------|
| Frontend  | React 18, Vite, TypeScript, Tailwind CSS v4          |
| Backend   | Python 3.12, FastAPI, Uvicorn                        |
| AI        | Google Gemini 2.5 Flash                              |
| RAG       | PyMuPDF, Sentence Transformers, FAISS                |
| Deployment| Docker, AWS App Runner                               |

---

## Project Structure

```
researchpilot/
├── frontend/          # React + Vite + TypeScript frontend
├── backend/           # FastAPI + Python backend
├── .env.example       # Environment variable template
├── .gitignore         # Git ignore rules
├── docker-compose.yml # Multi-container orchestration
└── README.md          # This file
```

---

## Prerequisites

- **Node.js** >= 18.x and **npm** >= 9.x
- **Python** >= 3.12
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/apikey))

---

## Quick Start

### 1. Clone & Configure

```bash
git clone <repository-url>
cd researchpilot
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
API docs: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## API Endpoints

| Method | Endpoint         | Description                  |
|--------|-----------------|------------------------------|
| GET    | `/`             | API welcome message          |
| GET    | `/health`       | Health check                 |
| POST   | `/upload`       | Upload a research paper (PDF)|
| POST   | `/chat`         | Ask a question about a paper |
| POST   | `/summary`      | Generate paper summary       |

---

## Development

### Backend

```bash
cd backend

# Lint
ruff check .

# Format
ruff format .

# Type check
mypy app/

# Run tests
pytest
```

### Frontend

```bash
cd frontend

# Lint
npm run lint

# Type check
npx tsc --noEmit

# Build
npm run build
```

---

## Docker

```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the required values.

| Variable              | Required | Description                        |
|----------------------|----------|------------------------------------|
| `GEMINI_API_KEY`     | ✅       | Google Gemini API key              |
| `VITE_API_BASE_URL`  | ❌       | Frontend API base URL              |
| `BACKEND_PORT`       | ❌       | Backend server port (default: 8000)|
| `RAG_CHUNK_SIZE`     | ❌       | Text chunk size (default: 512)     |
| `UPLOAD_MAX_SIZE_MB` | ❌       | Max upload size (default: 20 MB)   |

See `.env.example` for the complete list.

---

## License

MIT
