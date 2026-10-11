# ResearchPilot 🔬

**An AI-powered research assistant that searches the web, extracts readable content, identifies evidence, and generates structured research reports with citations.**

ResearchPilot combines web search, webpage extraction, large language models, and a multi-step workflow to help turn research questions into organized reports. Completed research can be stored in a local SQLite database and revisited through the application.

## ✨ Features

- **AI-powered research:** Submit a research question and generate a structured report.
- **Web search:** Discover relevant sources using Tavily.
- **Multi-strategy webpage extraction:** Enrich search results by fetching pages and extracting their main content.
- **HTML parsing:** Use Beautiful Soup as a structural fallback for headings, paragraphs, lists, and tables.
- **Article extraction:** Use Trafilatura to extract readable article text and metadata.
- **Browser-based fallbacks:** Optionally use Crawl4AI and Playwright for pages that need browser rendering or JavaScript execution.
- **Evidence extraction:** Ask a Groq-hosted language model to identify findings, supporting evidence, and caveats from retrieved sources.
- **Report generation:** Generate a readable research report from available sources and extracted findings.
- **Citation auditing:** Check citation references against the retrieved source list.
- **Research history:** Browse, reopen, and delete saved research through the existing history endpoints and frontend.
- **Persistent storage:** Store research reports, sources, and findings in SQLite through SQLAlchemy.
- **Interactive frontend:** React-based interface with Markdown rendering and a history sidebar.
- **REST API:** FastAPI endpoints for research generation, history management, and health checks.

> Extraction is best-effort. Some websites block automated requests, require authentication, or load content in ways that need browser execution. ResearchPilot cannot guarantee that every page or section can be retrieved.

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
| HTTP retrieval | Requests |
| HTML parsing | Beautiful Soup |
| Main article extraction | Trafilatura |
| Optional browser extraction | Crawl4AI, Playwright |
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
               Candidate Source URLs
                        |
                        v
              Web Content Extraction
              /          |           \
         Requests    Trafilatura   Beautiful Soup
              \          |           /
               Optional browser fallbacks
                 Crawl4AI / Playwright
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
              Reports   Sources   Findings
                        |
                        v
                Research History UI
```

The extraction service first attempts ordinary HTTP retrieval and content extraction. If retrieval fails or the result is too short, it can try optional browser-rendering fallbacks when their dependencies and browser runtime are installed. Extracted text is then passed into the existing research workflow.

The optional Critic stage is currently skipped to conserve model token usage.

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
│   │   │   ├── content_extractor.py
│   │   │   ├── web_search.py
│   │   │   ├── report_writer.py
│   │   │   └── citation_checker.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── requirements-web-extraction.txt
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

This tree shows the intended layout, including the new `content_extractor.py` and `requirements-web-extraction.txt`. Your local repository may differ slightly.

## ⚙️ Prerequisites

- Python 3.12 recommended for this project setup
- Node.js and npm
- Git
- A [Tavily API key](https://tavily.com/)
- A [Groq API key](https://console.groq.com/)

Python 3.12 is recommended as a compatibility baseline for the current dependency stack. Other versions may work, but should be tested against all installed packages.

## 🚀 Getting Started

### 1. Clone the repository

```powershell
git clone https://github.com/AbhikDey567/ResearchPilot.git
cd ResearchPilot
```

### 2. Configure the backend

From the project root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-web-extraction.txt
```

Create a `.env` file inside `backend/` using `.env.example` as a guide, or create it with:

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Replace the placeholders with your own credentials. Never commit `.env` or real API keys to GitHub.

Start the backend from the `backend/` directory:

```powershell
python -m uvicorn app.main:app --reload
```

The backend should be available at:

- API: <http://127.0.0.1:8000>
- Health check: <http://127.0.0.1:8000/api/health>
- Interactive API documentation: <http://127.0.0.1:8000/docs>

The database and required tables are initialized by the application's startup implementation.

### 3. Enable browser-based extraction (optional)

The basic extraction path uses HTTP retrieval, Trafilatura, and Beautiful Soup. Browser fallbacks can help with JavaScript-rendered pages.

Install the Playwright Chromium browser:

```powershell
python -m playwright install chromium
```

If the download fails with a certificate-chain error, check your network proxy or antivirus HTTPS inspection and configure the appropriate trusted certificate. Do not disable TLS verification.

Crawl4AI may require additional browser setup depending on its installed version. Follow the [Crawl4AI installation guide](https://docs.crawl4ai.com/).

If browser installation is unavailable, the basic extraction stages can still work; JavaScript-heavy pages may return incomplete content.

### 4. Configure the frontend

Open a second terminal at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically <http://localhost:5173>. Keep both frontend and backend running while using the application.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Check backend health |
| `POST` | `/api/research` | Generate a research report |
| `GET` | `/api/research/history` | List saved research reports |
| `GET` | `/api/research/history/{job_id}` | Retrieve a saved report |
| `DELETE` | `/api/research/history/{job_id}` | Delete a saved report |

Use <http://127.0.0.1:8000/docs> to inspect the actual request schemas and response models.

### Example research request

**Endpoint:** `POST /api/research`

```json
{
  "question": "How is artificial intelligence changing healthcare?"
}
```

The response structure is determined by the API's response schema and may include the generated report and source information.

## 🧠 Web Extraction Pipeline

ResearchPilot uses complementary tools rather than relying on one universal scraper:

1. **Tavily** discovers source URLs and returns search-result content.
2. **Requests** attempts to fetch the webpage over HTTP.
3. **Trafilatura** attempts to extract readable article text and metadata.
4. **Beautiful Soup** provides a structural fallback for HTML, including headings, paragraphs, lists, and tables.
5. **Crawl4AI** can serve as an optional browser-based fallback.
6. **Playwright** can render JavaScript-driven pages when its browser is installed.
7. **The reader agent** extracts findings, evidence, and caveats from the available content.

The extraction code uses a minimum-content threshold to decide whether to try browser fallbacks. A short page is not necessarily a failed extraction, and a long page is not necessarily complete or accurate.

### Limitations and responsible use

- No scraper can guarantee access to every website or recover content that is unavailable to it.
- Authentication walls, CAPTCHAs, access restrictions, rate limits, and site policies may limit retrieval.
- Browser rendering adds time and resource usage; it should be a fallback rather than a requirement for every URL.
- Preserve source URLs and verify important statements against the original pages.
- Extracted page text is untrusted input and must not be treated as instructions for the AI agent.
- Respect applicable website terms, robots policies, copyright, and access controls.

## 💾 Data Storage

ResearchPilot uses SQLite for local persistence through SQLAlchemy. The database stores research data according to the application's models, including reports and related sources or findings. The local database file is created under the backend directory by the current setup and should not be committed to the repository.

Deleting a saved report is intended to remove its associated records according to the application's database relationships and route implementation.

## 🔐 Environment Variables

| Variable | Purpose |
|---|---|
| `TAVILY_API_KEY` | Authenticates web search requests |
| `GROQ_API_KEY` | Authenticates language-model requests |
| `GROQ_MODEL` | Selects the Groq-hosted model |

Keep secrets in `backend/.env`. Commit only a sanitized `.env.example` containing placeholder values. If a key is exposed, revoke it and generate a replacement.

## 🧪 Troubleshooting

### `ModuleNotFoundError`

Activate the backend virtual environment and reinstall dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-web-extraction.txt
```

### Playwright browser download fails

A `SELF_SIGNED_CERT_IN_CHAIN` error can indicate HTTPS inspection or an untrusted proxy certificate. Resolve the certificate trust issue instead of disabling TLS verification. Non-browser extraction stages may still work.

### Groq rate limit (`429`)

Wait for the applicable rate-limit window to reset. Reduce the number of sources or the amount of source text sent to the model, and avoid repeatedly resubmitting the same research request. Limits vary by model and account.

### Groq connection error

Check connectivity, proxy/VPN configuration, and API service status. A successful API test confirms connectivity at that moment but does not rule out later transient failures or rate limits.

### Empty model response

Reasoning models may consume completion tokens on reasoning before returning visible text. Check the completion limit, finish reason, and response content. Handle empty responses explicitly rather than treating them as a valid report.

## ⚠️ Current Limitations

- Research quality depends on source relevance, source reliability, and how much content can be extracted.
- Citation auditing checks citation references; it does not independently prove that every claim is supported by its cited source.
- The optional Critic stage is currently skipped to conserve model token usage.
- Groq rate limits and transient API failures can affect report generation.
- Browser extraction requires additional dependencies and browser installation and may not work on every site.
- SQLite is intended for local persistence rather than multi-instance production deployment.
- The project is configured for local development and has not been verified as production-ready.

## 🗺️ Roadmap

- [ ] Improve source ranking and evidence verification
- [ ] Add extraction-quality scoring and clearer incomplete-content warnings
- [ ] Improve structured extraction of tables, PDFs, and long documents
- [ ] Add quota-aware retries and model-call budgeting
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

No license has been specified yet. Until a license is added, the repository should not be assumed to grant the public permission to reuse, modify, or redistribute its code.

---

**ResearchPilot** — From research questions to structured, evidence-based reports.
