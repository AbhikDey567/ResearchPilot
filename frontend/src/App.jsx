
import { useCallback, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  ArrowRight,
  Atom,
  BookOpen,
  ChevronDown,
  Clock3,
  FileText,
  Globe2,
  Layers3,
  LoaderCircle,
  Plus,
  Search,
  ShieldCheck,
  Sparkles,
  Trash2,
  Zap,
} from "lucide-react";
import "./index.css";

const API_BASE = "http://127.0.0.1:8000/api";

const suggestions = [
  {
    icon: Globe2,
    title: "Explore a technology",
    prompt:
      "Compare the latest AI models, their capabilities, limitations, and costs.",
  },
  {
    icon: BookOpen,
    title: "Understand a complex topic",
    prompt:
      "Explain how retrieval-augmented generation works and compare it with fine-tuning.",
  },
  {
    icon: Layers3,
    title: "Compare different approaches",
    prompt:
      "Compare React, Vue, and Svelte for building modern web applications.",
  },
];

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState("");
  const [activeJobId, setActiveJobId] = useState(null);
  const [openingJobId, setOpeningJobId] = useState(null);
  const [deletingJobId, setDeletingJobId] = useState(null);

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError("");

    try {
      const response = await fetch(`${API_BASE}/research/history`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not load research history.");
      }

      setHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      setHistoryError(
        err.message || "Could not connect to the research history API."
      );
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const markdownComponents = {
    p: ({ children }) => <p>{renderCitations(children, result?.sources)}</p>,
    li: ({ children }) => <li>{renderCitations(children, result?.sources)}</li>,
    td: ({ children }) => <td>{renderCitations(children, result?.sources)}</td>,
    th: ({ children }) => <th>{renderCitations(children, result?.sources)}</th>,
    blockquote: ({ children }) => (
      <blockquote>{renderCitations(children, result?.sources)}</blockquote>
    ),
    h1: ({ children }) => <h1>{renderCitations(children, result?.sources)}</h1>,
    h2: ({ children }) => <h2>{renderCitations(children, result?.sources)}</h2>,
    h3: ({ children }) => <h3>{renderCitations(children, result?.sources)}</h3>,
  };

  function renderCitations(children, sources) {
    if (!Array.isArray(children)) {
      children = [children];
    }

    return children.map((child, index) => {
      if (typeof child !== "string") {
        return child;
      }

      const parts = child.split(/(\[\d+\])/g);

      return parts.map((part, partIndex) => {
        const match = part.match(/^\[(\d+)\]$/);

        if (!match) return part;

        const source = sources?.[Number(match[1]) - 1];

        if (!source?.url) return part;

        return (
          <a
            key={`${index}-${partIndex}`}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-citation"
            title={`Open source ${match[1]}: ${source.title}`}
          >
            [{match[1]}]
          </a>
        );
      });
    });
  }

  async function handleResearch(event) {
    event.preventDefault();

    const question = query.trim();

    if (question.length < 3 || loading) return;

    setLoading(true);
    setError("");
    setResult(null);
    setActiveJobId(null);

    try {
      const response = await fetch(`${API_BASE}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Research could not be completed.");
      }

      setResult(data);
      await loadHistory();
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to ResearchPilot. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  async function openSavedResearch(jobId) {
    if (openingJobId !== null) return;

    setOpeningJobId(jobId);
    setError("");
    setHistoryError("");

    try {
      const response = await fetch(
        `${API_BASE}/research/history/${jobId}`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not open this report.");
      }

      setResult({
        question: data.question,
        answer: data.answer,
        sources: data.sources || [],
      });
      setQuery(data.question);
      setActiveJobId(jobId);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setHistoryError(err.message || "Could not open this report.");
    } finally {
      setOpeningJobId(null);
    }
  }

  async function deleteSavedResearch(event, jobId) {
    event.stopPropagation();

    if (deletingJobId !== null) return;

    const confirmed = window.confirm(
      "Delete this saved research report and its associated data?"
    );

    if (!confirmed) return;

    setDeletingJobId(jobId);
    setHistoryError("");

    try {
      const response = await fetch(
        `${API_BASE}/research/history/${jobId}`,
        { method: "DELETE" }
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not delete this report.");
      }

      setHistory((previous) =>
        previous.filter((item) => item.id !== jobId)
      );

      if (activeJobId === jobId) {
        setResult(null);
        setActiveJobId(null);
        setQuery("");
      }
    } catch (err) {
      setHistoryError(err.message || "Could not delete this report.");
    } finally {
      setDeletingJobId(null);
    }
  }

  function startNewResearch() {
    setQuery("");
    setResult(null);
    setError("");
    setActiveJobId(null);
    document.getElementById("research-input")?.focus();
  }

  function useSuggestion(prompt) {
    setQuery(prompt);
    setError("");
    document.getElementById("research-input")?.focus();
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/" aria-label="ResearchPilot home">
          <span className="brand-icon">
            <Atom size={22} />
          </span>
          <span>
            <strong>ResearchPilot</strong>
            <small>AI RESEARCH WORKSPACE</small>
          </span>
        </a>

        <button className="new-research" onClick={startNewResearch}>
          <Plus size={17} />
          New research
          <span className="shortcut">⌘ K</span>
        </button>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${!activeJobId ? "active" : ""}`}
            onClick={startNewResearch}
            type="button"
          >
            <Search size={17} />
            Research
          </button>
          <button
            className="nav-item"
            onClick={() =>
              document.getElementById("sources")?.scrollIntoView({
                behavior: "smooth",
              })
            }
            type="button"
          >
            <BookOpen size={17} />
            Sources
          </button>
          <button
            className="nav-item"
            onClick={() =>
              document.getElementById("reports")?.scrollIntoView({
                behavior: "smooth",
              })
            }
            type="button"
          >
            <FileText size={17} />
            Reports
          </button>
        </nav>

        <div className="sidebar-label history-label">RESEARCH HISTORY</div>

        <div className="history-list">
          {historyLoading ? (
            <p className="history-message">
              <LoaderCircle size={15} className="history-spinner" />
              Loading history...
            </p>
          ) : historyError && history.length === 0 ? (
            <p className="history-message">{historyError}</p>
          ) : history.length === 0 ? (
            <div className="empty-history">
              <Clock3 size={19} />
              <p>Your saved research will appear here.</p>
            </div>
          ) : (
            history.map((item) => (
              <div
                className={`history-item ${
                  activeJobId === item.id ? "active" : ""
                }`}
                key={item.id}
              >
                <button
                  className="history-open"
                  onClick={() => openSavedResearch(item.id)}
                  disabled={openingJobId !== null}
                  type="button"
                  title={item.question}
                >
                  <FileText size={15} />
                  <span>{item.question}</span>
                  {openingJobId === item.id && (
                    <LoaderCircle size={14} className="history-spinner" />
                  )}
                </button>

                <button
                  className="history-delete"
                  onClick={(event) => deleteSavedResearch(event, item.id)}
                  disabled={deletingJobId !== null}
                  type="button"
                  aria-label={`Delete report: ${item.question}`}
                  title="Delete report"
                >
                  {deletingJobId === item.id ? (
                    <LoaderCircle size={14} className="history-spinner" />
                  ) : (
                    <Trash2 size={14} />
                  )}
                </button>
              </div>
            ))
          )}

          {!historyLoading && historyError && history.length > 0 && (
            <p className="history-message">{historyError}</p>
          )}

          <button
            className="history-refresh"
            onClick={loadHistory}
            disabled={historyLoading}
            type="button"
          >
            <Clock3 size={14} />
            Refresh history
          </button>
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <span>Research engine</span>
          <span className="status-badge">SQLite</span>
        </div>
      </aside>

      <main className="main-content" id="research">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span>{" "}
            <strong>
              {activeJobId ? "Saved research" : "New research"}
            </strong>
          </div>

          <button className="model-selector" type="button">
            <span className="model-dot" />
            AI research
            <ChevronDown size={15} />
          </button>
        </header>

        <section className="hero">
          <div className="eyebrow">
            <Sparkles size={14} />
            YOUR PERSONAL RESEARCH ASSISTANT
          </div>

          <h1>
            Good research starts
            <br />
            with a <span>better question.</span>
          </h1>

          <p className="hero-description">
            Explore complex topics, investigate reliable sources, and turn
            scattered information into research you can actually use.
          </p>

          <form className="research-form" onSubmit={handleResearch}>
            <div className="input-heading">
              <span>
                <Search size={16} />
                RESEARCH QUESTION
              </span>
              <span className="input-hint">Be as specific as you like</span>
            </div>

            <textarea
              id="research-input"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="What would you like to investigate today?"
              rows={3}
            />

            <div className="form-footer">
              <span className="privacy-note">
                <ShieldCheck size={15} />
                Source-backed research
              </span>

              <button
                className="research-button"
                type="submit"
                disabled={query.trim().length < 3 || loading}
              >
                {loading ? "Researching..." : "Start research"}
                {loading ? (
                  <span className="loading-spinner" />
                ) : (
                  <ArrowRight size={16} />
                )}
              </button>
            </div>
          </form>

          {!result && (
            <>
              <div className="suggestion-heading">
                <span>NOT SURE WHERE TO START?</span>
                <span>TRY AN EXAMPLE</span>
              </div>

              <div className="suggestion-grid">
                {suggestions.map((item) => {
                  const Icon = item.icon;

                  return (
                    <button
                      className="suggestion-card"
                      key={item.title}
                      onClick={() => useSuggestion(item.prompt)}
                      type="button"
                    >
                      <span className="suggestion-icon">
                        <Icon size={19} />
                      </span>
                      <span className="suggestion-title">{item.title}</span>
                      <span className="suggestion-description">
                        {item.prompt}
                      </span>
                      <ArrowRight
                        className="suggestion-arrow"
                        size={16}
                      />
                    </button>
                  );
                })}
              </div>

              <div className="capabilities">
                <div className="capability">
                  <Globe2 size={17} />
                  <span>Web-based discovery</span>
                </div>
                <div className="capability">
                  <ShieldCheck size={17} />
                  <span>Traceable evidence</span>
                </div>
                <div className="capability">
                  <Zap size={17} />
                  <span>Structured reports</span>
                </div>
              </div>
            </>
          )}

          {error && (
            <div className="result-error" role="alert">
              <strong>Research failed</strong>
              <p>{error}</p>
            </div>
          )}

          {loading && (
            <div className="research-status" role="status">
              <span className="loading-spinner" />
              <div>
                <strong>Investigating your question</strong>
                <p>Searching the web and synthesizing relevant evidence...</p>
              </div>
            </div>
          )}

          {result && (
            <section
              className="results-panel"
              id="reports"
              aria-live="polite"
            >
              <div className="results-heading">
                <div>
                  <span className="results-eyebrow">
                    <Sparkles size={14} /> RESEARCH RESULTS
                  </span>
                  <h2>Your research report</h2>
                  <p>{result.question}</p>
                </div>
                <span className="source-count">
                  {result.sources.length} sources
                </span>
              </div>

              <div className="answer-content">
                <div className="research-report">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={markdownComponents}
                  >
                    {result.answer}
                  </ReactMarkdown>
                </div>
              </div>

              <div className="sources-section" id="sources">
                <h3>
                  <BookOpen size={17} /> Sources consulted
                </h3>

                {result.sources.map((source, index) => (
                  <article className="source-item" key={source.url}>
                    <span className="source-number">{index + 1}</span>
                    <div className="source-info">
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {source.title}
                        <ArrowRight size={14} />
                      </a>
                      <p>{source.content}</p>
                      <span className="source-url">{source.url}</span>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}
        </section>

        <footer className="page-footer">
          <span>
            RESEARCHPILOT <span className="footer-separator">/</span> EARLY
            BUILD
          </span>
          <span>Built for curious minds.</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
