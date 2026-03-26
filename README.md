# 🧠 DocuQuery AI

> RAG-powered document Q&A application with intelligent semantic search, automatic document classification, and AI-powered answers with source citations.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://reactjs.org)
[![LangChain](https://img.shields.io/badge/LangChain-🦜-green)](https://langchain.com)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-000?logo=pinecone)](https://pinecone.io)

---

## ✨ Features

- **RAG Document Q&A** — Upload PDFs and ask questions with AI-generated answers backed by source citations
- **Dual Embedding Support** — HuggingFace sentence-transformers (free) + OpenAI text-embedding-ada-002 (optional)
- **Dual LLM Support** — Google Gemini (free) + OpenAI GPT-3.5-turbo (optional)
- **Document Classification** — Auto-categorize PDFs (legal, medical, technical, financial, general) using scikit-learn TF-IDF + Naive Bayes
- **Smart Retrieval Routing** — Queries routed to relevant Pinecone namespaces by document category
- **Redis Caching** — Cached responses for repeated queries, reducing API costs and response time by ~60%
- **Streaming Responses** — Real-time SSE streaming for chat answers
- **Supabase Auth** — Secure email/password authentication
- **Beautiful UI** — Glassmorphism design with dark mode, animations, and drag-and-drop uploads

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Login   │  │  Upload  │  │   Chat   │  │   Documents   │  │
│  │  Page    │  │  Page    │  │   Page   │  │   Page        │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       └──────────────┴─────────────┴────────────────┘          │
│                         Supabase Auth                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API + SSE
┌────────────────────────────┴────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                                                                 │
│  ┌─────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐  │
│  │  Auth   │  │  Documents   │  │   Query   │  │ Classify  │  │
│  │ Router  │  │   Router     │  │  Router   │  │  Router   │  │
│  └────┬────┘  └──────┬───────┘  └─────┬─────┘  └─────┬─────┘  │
│       │              │                │               │         │
│  ┌────┴──────────────┴────────────────┴───────────────┴────┐   │
│  │                    SERVICES LAYER                        │   │
│  │  ┌────────────┐ ┌──────────┐ ┌───────┐ ┌────────────┐  │   │
│  │  │ Embeddings │ │   LLM    │ │ Redis │ │ Classifier │  │   │
│  │  │ HF/OpenAI  │ │Gem/GPT   │ │ Cache │ │ TF-IDF+NB  │  │   │
│  │  └─────┬──────┘ └────┬─────┘ └───┬───┘ └────────────┘  │   │
│  └────────┼──────────────┼───────────┼─────────────────────┘   │
│           │              │           │                          │
└───────────┼──────────────┼───────────┼──────────────────────────┘
            │              │           │
   ┌────────┴───┐  ┌───────┴──┐  ┌────┴────┐  ┌──────────────┐
   │  Pinecone  │  │  Gemini  │  │  Redis  │  │   Supabase   │
   │ Vector DB  │  │   API    │  │  Cache  │  │  Auth+DB+S3  │
   └────────────┘  └──────────┘  └─────────┘  └──────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python, FastAPI | Async REST API server |
| **PDF Processing** | PyPDF2 | PDF text extraction |
| **Text Splitting** | LangChain | Recursive character text chunking |
| **Embeddings** | HuggingFace sentence-transformers | Semantic vector embeddings (free) |
| **Embeddings (alt)** | OpenAI text-embedding-ada-002 | Premium embeddings (optional) |
| **LLM** | Google Gemini API | Answer generation (free) |
| **LLM (alt)** | OpenAI GPT-3.5-turbo | Premium LLM (optional) |
| **Vector DB** | Pinecone | Similarity search & vector storage |
| **Classification** | scikit-learn (TF-IDF + MultinomialNB) | Document categorization |
| **Caching** | Redis | Query response caching |
| **Auth & DB** | Supabase | Authentication, PostgreSQL, file storage |
| **Frontend** | React, Tailwind CSS | User interface |
| **Deployment** | Docker, Render, Vercel | Containerization & hosting |

---

## 📁 Project Structure

```
docuquery-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Environment configuration
│   │   ├── routers/
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   ├── documents.py        # PDF upload & processing
│   │   │   ├── query.py            # RAG query pipeline
│   │   │   └── classify.py         # Document classification
│   │   └── services/
│   │       ├── embeddings.py       # HuggingFace + OpenAI embeddings
│   │       ├── llm_service.py      # Gemini + OpenAI LLM
│   │       ├── pinecone_service.py # Vector database operations
│   │       ├── redis_cache.py      # Query caching (60% cost reduction)
│   │       ├── supabase_service.py # Auth, DB, storage operations
│   │       └── classifier.py       # TF-IDF + Naive Bayes classifier
│   ├── supabase_schema.sql         # Database schema with RLS
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── ChatMessage.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── UploadPage.jsx
│   │   │   └── DocumentsPage.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── supabase.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional, for local Redis)

### 1. Clone the Repository

```bash
git clone https://github.com/Kushyanth04/docuquery-ai.git
cd docuquery-ai
```

### 2. Create Free Accounts

| Service | URL | Free Tier |
|---------|-----|-----------|
| HuggingFace | [huggingface.co](https://huggingface.co) | Unlimited embeddings |
| Google Gemini | [ai.google.dev](https://ai.google.dev) | 15 req/min |
| Pinecone | [pinecone.io](https://pinecone.io) | 1 serverless index |
| Supabase | [supabase.com](https://supabase.com) | 500MB DB, 1GB storage |

### 3. Set Up Supabase Database

1. Create a new Supabase project
2. Go to **SQL Editor** and run the contents of `backend/supabase_schema.sql`
3. Copy your project URL and keys from **Settings → API**

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn app.main:app --reload --port 8000
```

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your Supabase URL and key

# Run the dev server
npm run dev
```

### 6. Docker Compose (Alternative)

```bash
# Start all services (backend + Redis + frontend)
docker-compose up --build
```

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `LLM_PROVIDER` | `gemini` or `openai` | ✅ |
| `GOOGLE_API_KEY` | Gemini API key | If using Gemini |
| `OPENAI_API_KEY` | OpenAI API key | If using OpenAI |
| `EMBEDDING_PROVIDER` | `huggingface` or `openai` | ✅ |
| `HUGGINGFACE_API_KEY` | HF API token | If using HF API |
| `PINECONE_API_KEY` | Pinecone API key | ✅ |
| `PINECONE_INDEX` | Index name | ✅ |
| `SUPABASE_URL` | Supabase project URL | ✅ |
| `SUPABASE_KEY` | Supabase anon key | ✅ |
| `REDIS_URL` | Redis connection URL | ✅ |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key |
| `VITE_API_URL` | Backend API URL |

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Register new user |
| `POST` | `/auth/login` | Login user |
| `GET` | `/auth/me` | Get current user |
| `POST` | `/documents/upload` | Upload & process PDF |
| `GET` | `/documents/history` | Get upload history |
| `DELETE` | `/documents/{id}` | Delete document |
| `POST` | `/query/` | Ask question (JSON response) |
| `POST` | `/query/stream` | Ask question (SSE stream) |
| `GET` | `/query/history` | Get chat history |
| `POST` | `/classify/` | Classify text |
| `GET` | `/health` | Health check |

---

## 🌐 Deployment

### Backend → Render

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repo
3. Set **Root Directory** to `backend`
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add all environment variables from `.env.example`

### Frontend → Vercel

1. Import project on [Vercel](https://vercel.com)
2. Set **Root Directory** to `frontend`
3. Set **Framework Preset** to Vite
4. Add environment variables (`VITE_API_URL` = your Render URL)

---

## 📸 Screenshots

*Screenshots will be added once the application is deployed.*

---

## 📄 License

MIT License — feel free to use this project for learning and portfolio purposes.

---

<p align="center">
  Built with ❤️ using Python, FastAPI, LangChain, Pinecone, and React
</p>
