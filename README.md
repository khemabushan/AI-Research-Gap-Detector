# 🔬 AI Research Gap Detector

> AI-powered platform that discovers unexplored research opportunities by analyzing scientific literature from multiple academic databases using Large Language Models.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Build](https://img.shields.io/badge/CI-Passing-brightgreen)

---

## 🚀 Overview

AI Research Gap Detector is an intelligent research assistant that helps researchers, students, and innovators identify promising research opportunities automatically.

Instead of manually reviewing hundreds of research papers, the platform:

- Collects papers from multiple academic sources
- Cleans and normalizes research data
- Detects overlapping ideas
- Finds missing research directions
- Generates research gap reports using LLMs

The goal is to reduce literature review time from several days to just a few minutes.

---

## 🌐 Live Demo

🚀 **Frontend:** https://research-gap-detector-frontend.onrender.com/

⚙️ **Backend API:** https://research-gap-detector-backend.onrender.com/

📚 **API Documentation:** https://research-gap-detector-backend.onrender.com/docs

# ✨ Features

✅ Multi-source paper collection

- arXiv
- Semantic Scholar

✅ AI Research Gap Analysis

- Novel research opportunities
- Missing datasets
- Underexplored topics
- Future work suggestions

✅ Smart Paper Processing

- Duplicate removal
- Metadata normalization
- Citation extraction
- Text cleaning

✅ Modern Web Interface

- Next.js
- Responsive UI
- Real-time analysis
- Progress tracking

---

# 🏗 Architecture

```
                    User
                      │
                      ▼
             Next.js Frontend
                      │
                      ▼
               FastAPI Backend
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
    arXiv API              Semantic Scholar API
        │                           │
        └─────────────┬─────────────┘
                      ▼
            Paper Collection Engine
                      │
                      ▼
          Data Cleaning & Deduplication
                      │
                      ▼
              AI Gap Detection Engine
                      │
                      ▼
          Structured Research Report
```

---

# 🛠 Tech Stack

## Frontend

- Next.js 14
- React
- TypeScript
- Tailwind CSS
- React Query

## Backend

- FastAPI
- Python
- SQLAlchemy
- Pydantic
- httpx

## AI

- OpenAI GPT
- Semantic Scholar API
- arXiv API

## Testing

- Pytest
- Respx

---

# 📂 Project Structure

```
backend/
    app/
        api/
        services/
        models/
        database/
        utils/

frontend/
    app/
    components/
    hooks/
    lib/

.github/
    workflows/

docker-compose.yml
README.md
```

---

# ⚙ Installation

Clone repository

```bash
git clone https://github.com/yourusername/AI-Research-Gap-Detector.git
```

Backend

```bash
cd backend

python -m venv .venv

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 🔑 Environment Variables

Backend

```
OPENAI_API_KEY=

SEMANTIC_SCHOLAR_API_KEY=

DATABASE_URL=

SECRET_KEY=
```

---

# 📊 Example Workflow

```
User enters topic

↓

Paper Collection

↓

Duplicate Removal

↓

Metadata Extraction

↓

LLM Analysis

↓

Research Gap Report
```

---

# 📸 Screenshots

## Home Page

(Add screenshot)

---

## Analysis Dashboard

(Add screenshot)

---

## Generated Research Gap Report

(Add screenshot)

---

# 🧪 Testing

Backend

```bash
pytest tests -v
```

Frontend

```bash
npm run lint

npm run build
```

---

# 📈 Future Improvements

- PDF upload support
- Research trend visualization
- Citation graph
- Automatic paper summarization
- Multi-agent research assistant
- RAG-powered literature review
- Vector database integration

---

# 🤝 Contributing

Contributions are welcome.

Please open an issue first to discuss major changes.

---

# 📜 License

MIT License

---

# 👨‍💻 Author

**Hemabushan K**

B.Tech CSE (AI & ML)

Passionate about Artificial Intelligence, Machine Learning, and Research Automation.

GitHub:
https://github.com/khemabushan
