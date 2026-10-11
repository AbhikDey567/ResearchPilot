# ResearchPilot 🔬

**An AI-powered research assistant that searches the web, extracts information from webpages, identifies evidence, and generates structured research reports with citations.**

ResearchPilot combines web search, webpage extraction, large language models, and a multi-step AI workflow to transform research questions into organized reports. Completed research can be stored in a local SQLite database and revisited through the application.

## ✨ Features

- **AI-powered research:** Submit a research question and generate a structured report.
- **Web search:** Discover relevant sources using Tavily.
- **Advanced web extraction:** Retrieve webpage content using multiple extraction strategies.
- **HTML parsing:** Use Beautiful Soup to parse webpage structure, including headings, paragraphs, lists, and tables.
- **Article extraction:** Use Trafilatura to extract readable article text and metadata.
- **Browser-based extraction:** Optionally use Crawl4AI and Playwright for JavaScript-rendered websites.
- **Evidence extraction:** Identify key findings, supporting evidence, and caveats using Groq-hosted language models.
- **Report generation:** Generate structured research reports from retrieved sources and extracted findings.
- **Citation auditing:** Check citation references against the retrieved source list.
- **Research history:** Browse, reopen, and delete previously saved reports.
- **Persistent storage:** Store research reports, sources, and findings in SQLite using SQLAlchemy.
- **Interactive frontend:** React-based interface with Markdown rendering and a research history sidebar.
- **REST API:** FastAPI endpoints for research generation, history management, and health checks.

> Web extraction is best-effort. Some websites restrict automated access, require authentication, or rely on JavaScript to display content. ResearchPilot cannot guarantee that every page or section will be accessible.

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
| Article extraction | Trafilatura |
| Browser-based extraction | Crawl4AI, Playwright |
| Database | SQLite, SQLAlchemy |
| API documentation | FastAPI / Swagger UI |

## 🏗️ Architecture

<img width="1536" height="1024" alt="71387797-0129-4066-9d47-bc1e2f3acc62" src="https://github.com/user-attachments/assets/0433ea0b-abf9-4056-84f8-974f6dc68f65" />


The research workflow discovers relevant sources, retrieves webpage content, extracts readable text, identifies evidence, generates a report, and checks citation references.

The extraction service attempts ordinary HTTP retrieval first. If retrieval fails or the extracted content is too short, it can attempt browser-based extraction when the optional dependencies and browser runtime are available.

The optional Critic stage is currently skipped to conserve model token usage.


## Application screenshots
<img width="1900" height="925" alt="Screenshot 2026-10-11 143332" src="https://github.com/user-attachments/assets/9e3d563b-87a4-4573-a960-8af966c6acde" />

<img width="1892" height="926" alt="Screenshot 2026-10-11 153439" src="https://github.com/user-attachments/assets/3e26f64e-482c-45cd-bd8b-0a0a76a5b757" />

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

The tree represents the intended project layout. Minor differences may exist in the local repository.

## ⚙️ Prerequisites

Before running ResearchPilot, install:

- Python 3.12 (recommended for the current dependency setup)
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

### 2. Set up the backend

Navigate to the backend directory:

```powershell
cd backend
```

Create a Python virtual environment:

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip and install the project dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install the web extraction dependencies:

```powershell
python -m pip install -r requirements-web-extraction.txt
```

### 3. Configure environment variables

Create a `.env` file inside the `backend/` directory:

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Replace the placeholder values with your actual API credentials.

**Never commit your `.env` file or expose API keys in your source code or public repository.**

### 4. Start the backend

From the `backend/` directory, run:

```powershell
python -m uvicorn app.main:app --reload
```

The backend should be available at:

- **API:** http://127.0.0.1:8000
- **Health check:** http://127.0.0.1:8000/api/health
- **Interactive API documentation:** http://127.0.0.1:8000/docs

The application initializes the database according to its startup implementation.

### 5. Enable browser-based extraction (optional)

The basic extraction pipeline uses HTTP retrieval, Trafilatura, and Beautiful Soup. Browser-based fallbacks can help with websites that rely on JavaScript.

Install the Playwright Chromium browser:

```powershell
python -m playwright install chromium
```

Crawl4AI may require additional browser setup depending on its installed version. Refer to the [Crawl4AI documentation](https://docs.crawl4ai.com/).

If browser installation fails, the basic extraction pipeline can still work, but JavaScript-heavy websites may return incomplete content.

### 6. Set up the frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically:

http://localhost:5173

Keep the frontend and backend running while using ResearchPilot.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Check backend health |
| `POST` | `/api/research` | Generate a research report |
| `GET` | `/api/research/history` | List saved research reports |
| `GET` | `/api/research/history/{job_id}` | Retrieve a saved report |
| `DELETE` | `/api/research/history/{job_id}` | Delete a saved report |

Explore the API using the interactive documentation at http://127.0.0.1:8000/docs.

### Example research request

**Endpoint:** `POST /api/research`

```json
{
  "question": "How is artificial intelligence changing healthcare?"
}
```

The exact response structure is determined by the application's API schemas.

## 🧠 Web Extraction Pipeline

ResearchPilot combines several tools to improve webpage retrieval and content quality.

1. **Tavily:** Discovers relevant sources and provides search-result content.
2. **Requests:** Attempts to retrieve webpages using HTTP.
3. **Trafilatura:** Extracts readable article text and metadata.
4. **Beautiful Soup:** Provides a structural fallback for HTML content, including headings, paragraphs, lists, and tables.
5. **Crawl4AI:** Provides an optional browser-based extraction fallback.
6. **Playwright:** Renders JavaScript-driven pages when the browser is installed.
7. **Reader agent:** Extracts findings, supporting evidence, and caveats from available source content.

### Extraction limitations

- No single scraper can reliably extract every website.
- Authentication requirements, CAPTCHAs, access restrictions, and rate limits may prevent retrieval.
- JavaScript-rendered pages may require browser-based extraction.
- A short extraction does not necessarily mean failure, and a long extraction does not guarantee completeness.
- The original source should remain available for verification.
- Extracted webpage content must be treated as untrusted input rather than instructions to the AI.
- Website terms, access controls, and applicable copyright requirements should be respected.

## 💾 Data Storage

ResearchPilot uses SQLite for local persistence through SQLAlchemy.

The database stores research data according to the application's models, including reports and related sources or findings.

The local database file is created in the backend directory and should not be committed to the repository.

## 🔐 Environment Variables

| Variable | Purpose |
|---|---|
| `TAVILY_API_KEY` | Authenticates web search requests |
| `GROQ_API_KEY` | Authenticates language-model requests |
| `GROQ_MODEL` | Selects the Groq-hosted model |

Keep credentials in `backend/.env`. Commit only a sanitized `.env.example` containing placeholder values.

## 🧪 Troubleshooting

### Missing Python modules

Activate the virtual environment and install both dependency lists:

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-web-extraction.txt
```

### Playwright browser installation fails

A `SELF_SIGNED_CERT_IN_CHAIN` error can indicate HTTPS inspection or an untrusted proxy certificate. Resolve the certificate trust issue rather than disabling TLS verification.

### Groq rate limit (`429`)

Wait for the applicable rate-limit window to reset. Reduce the amount of source content or the number of sources sent to the model, and avoid repeatedly resubmitting the same request.

### Groq connection errors

Check internet connectivity, proxy or VPN configuration, and API availability. A successful API test confirms connectivity at that moment but does not rule out later connection failures or rate limits.

### Empty model responses

Reasoning models may consume completion tokens on reasoning before returning visible text. Check the response content, completion-token limit, and finish reason. Empty responses should be handled explicitly rather than treated as valid reports.

## ⚠️ Current Limitations

- Research quality depends on the relevance and reliability of retrieved sources.
- Citation auditing checks citation references but does not independently prove that every claim is supported by its cited source.
- The optional Critic stage is currently skipped to conserve model token usage.
- Groq rate limits and transient API failures can affect report generation.
- Browser-based extraction requires additional dependencies and browser installation.
- SQLite is intended for local persistence rather than multi-instance production deployment.
- The project is configured for local development and has not been verified as production-ready.

## 🗺️ Roadmap

- [ ] Improve source ranking and evidence verification
- [ ] Add extraction-quality scoring and incomplete-content warnings
- [ ] Improve structured extraction of tables and long documents
- [ ] Add quota-aware retries and model-call budgeting
- [ ] Restore the Critic and report-revision stages
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

No license has been specified yet. Until a license is added, the repository should not be assumed to grant permission to reuse, modify, or redistribute the code.

---

**ResearchPilot** — From research questions to structured, evidence-based reports.
