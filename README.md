# ResearchPilot 🔬

**An AI-powered research assistant that searches the web, extracts evidence, and generates structured research reports with citations.**

ResearchPilot combines web search, large language models, and a multi-step research workflow to help users explore questions and turn online information into organized reports. It also saves completed research in a local SQLite database, allowing users to revisit previous reports without running the research process again.

## ✨ Features

- **AI-powered research:** Submit a research question and generate a structured report.
- **Web search:** Retrieve relevant web sources using Tavily.
- **Evidence extraction:** Extract key findings, supporting evidence, and caveats from retrieved sources.
- **Report generation:** Generate readable research reports using Groq-hosted language models.
- **Citation auditing:** Check citation references against the retrieved source list.
- **Research history:** Browse, reopen, and delete previously saved reports.
- **Persistent storage:** Store research reports, sources, and findings in SQLite.
- **Interactive frontend:** React-based interface with Markdown rendering and a history sidebar.
- **REST API:** FastAPI endpoints for research generation, history management, and health checks.

## 🛠️ Tech Stack

| Component | Technologies |
|---|---|
| Frontend | React, JavaScript, Vite |
| Styling | Tailwind CSS |
| Icons | Lucide React |
| Report rendering | React Markdown, remark-gfm |
| Backend | Python, FastAPI |
| AI workflow | LangGraph, LangChain |
| Language models | Groq |
| Web search | Tavily |
| Database | SQLite, SQLAlchemy |
| API documentation | FastAPI / Swagger UI |

## 🏗️ Architecture

```text
                    User
                     |
                     v
             React + Vite Frontend
                     |
                     v
              FastAPI REST API
                     |
                     v
             LangGraph Workflow
                     |
                     v
             Research Question
                     |
                     v
              Tavily Web Search
                     |
                     v
              Evidence Reader
                     |
                     v
              Report Writer
                     |
                     v
              Citation Audit
                     |
                     v
              Generated Report
                     |
                     v
              SQLite Database
              /       |       \
          Reports   Sources  Findings
                     |
                     v
            Research History UI
```

The workflow is designed as a sequence of research stages. The optional Critic stage is currently skipped to conserve model token usage.

## 📁 Project Structure

```text
ResearchPilot/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── planner.py
│   │   │   ├── reader.py
│   │   │   ├── critic.py
│   │   │   └── workflow.py
│   │   ├── routes/
│   │   │   └── research.py
│   │   ├── services/
│   │   │   ├── web_search.py
│   │   │   ├── report_writer.py
│   │   │   └── citation_checker.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

*The tree describes the intended layout; minor differences may exist in your local project.*

## ⚙️ Prerequisites

Before running ResearchPilot, install:

- Python 3.10 or later
- Node.js and npm
- Git
- A [Tavily API key](https://tavily.com/)
- A [Groq API key](https://console.groq.com/)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <(https://github.com/AbhikDey567/ResearchPilot)>
cd ResearchPilot
```

Replace the placeholder with your actual GitHub repository URL.

### 2. Configure the backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file inside the `backend` directory:

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Replace the example values with your own API credentials. Never commit your actual `.env` file or API keys to GitHub.

Start the backend from the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

The backend should be available at:

- API: `http://127.0.0.1:8000`
- API health check: `http://127.0.0.1:8000/api/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

The SQLite database and required tables are initialized when the backend starts.

### 3. Configure the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically:

`http://localhost:5173`

Keep both the frontend and backend running while using the application.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Check backend health |
| `POST` | `/api/research` | Generate a research report |
| `GET` | `/api/research/history` | List saved research reports |
| `GET` | `/api/research/history/{job_id}` | Retrieve a saved report |
| `DELETE` | `/api/research/history/{job_id}` | Delete a saved report |

### Example research request

**Endpoint:** `POST /api/research`

```json
{
  "question": "How is artificial intelligence changing healthcare?"
}
```

The response includes the research question, generated report, and retrieved sources.

You can explore request schemas and inspect complete responses through the interactive API documentation at `/docs`.

## 💾 Data Storage

ResearchPilot uses SQLite for local persistence.

The database stores:

- Research questions and generated reports
- Retrieved web sources
- Extracted findings, evidence, and caveats
- Report status and timestamps

The local database is created in the backend directory. It is intended for local development and should not be committed to the repository.

Deleting a saved report removes that report and its associated stored records.

## 🔐 Environment Variables

| Variable | Purpose |
|---|---|
| `TAVILY_API_KEY` | Authenticates web search requests |
| `GROQ_API_KEY` | Authenticates language-model requests |
| `GROQ_MODEL` | Selects the Groq model used by the application |

Keep secrets in `backend/.env`. Commit only a sanitized `.env.example` file containing placeholder values.

## ⚠️ Current Limitations

- Research quality depends on the relevance and reliability of retrieved web sources.
- Citation auditing checks citation references; it does not independently prove that every claim is supported by its cited source.
- The optional Critic stage is currently skipped to conserve Groq token usage.
- Groq rate limits and API availability can affect report generation.
- SQLite is configured for local persistence, not multi-instance production deployment.
- The application currently uses a local development setup and has not yet been configured for production deployment.

## 🗺️ Roadmap

- [ ] Improve source ranking and evidence verification
- [ ] Restore the Critic and report-revision stages with quota-aware execution
- [ ] Add automated backend and API tests
- [ ] Export reports to Markdown and PDF
- [ ] Add research filters, pagination, and improved history management
- [ ] Add configurable research depth and source limits
- [ ] Prepare production deployment and database configuration

## 🤝 Contributing

Suggestions, bug reports, and contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Submit a pull request describing the changes.

## 📄 License

No license as of now.

---

**ResearchPilot** — From research questions to structured, evidence-based reports.
