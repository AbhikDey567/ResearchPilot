
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState } from "react";
import {
  ArrowRight,
  Atom,
  BookOpen,
  ChevronDown,
  Clock3,
  FileText,
  Globe2,
  Layers3,
  Search,
  ShieldCheck,
  Sparkles,
  Zap,
} from "lucide-react";
import "./index.css";

const suggestions = [
  {
    icon: Globe2,
    title: "Explore a technology",
    prompt: "Compare the latest AI models, their capabilities, limitations, and costs.",
  },
  {
    icon: BookOpen,
    title: "Understand a complex topic",
    prompt: "Explain how retrieval-augmented generation works and compare it with fine-tuning.",
  },
  {
    icon: Layers3,
    title: "Compare different approaches",
    prompt: "Compare React, Vue, and Svelte for building modern web applications.",
  },
];

function App() {

  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const markdownComponents = {
    p: ({ children }) => {
      const renderCitation = (child, index) => {
        if (typeof child !== "string") {
          return child;
        }

        const parts = child.split(/(\[\d+\])/g);

        return parts.map((part, partIndex) => {
          const match = part.match(/^\[(\d+)\]$/);

          if (!match) {
            return part;
          }

          const sourceIndex = Number(match[1]) - 1;
          const source = result?.sources?.[sourceIndex];

          if (!source?.url) {
            return part;
          }

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
      };

      return (
        <p>
          {Array.isArray(children)
            ? children.map(renderCitation)
            : renderCitation(children, 0)}
        </p>
      );
    },
  };


  async function handleResearch(event) {
    event.preventDefault();

    const question = query.trim();

    if (!question || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/research",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Research could not be completed."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message ||
        "Could not connect to ResearchPilot. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
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

        <button
          className="new-research"
          onClick={() => {
            setQuery("");
            document.getElementById("research-input")?.focus();
          }}
        >
          <Sparkles size={17} />
          New research
          <span className="shortcut">⌘ K</span>
        </button>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="sidebar-nav">
          <a className="nav-item active" href="#research">
            <Search size={17} />
            Research
          </a>
          <a className="nav-item" href="#sources">
            <BookOpen size={17} />
            Sources
          </a>
          <a className="nav-item" href="#reports">
            <FileText size={17} />
            Reports
          </a>
        </nav>

        <div className="sidebar-label history-label">
          RECENT RESEARCH
        </div>

        <div className="empty-history">
          <Clock3 size={19} />
          <p>Your research history will appear here.</p>
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <span>Research engine</span>
          <span className="status-badge">Setup</span>
        </div>
      </aside>

      <main className="main-content" id="research">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>New research</strong>
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
            Explore complex topics, investigate reliable sources, and
            turn scattered information into research you can actually use.
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
                disabled={!query.trim() || loading}
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
            <section className="results-panel" aria-live="polite">
              <div className="results-heading">
                <div>
                  <span className="results-eyebrow">
                    <Sparkles size={14} /> RESEARCH RESULTS
                  </span>
                  <h2>Your research report</h2>
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
          <span>RESEARCHPILOT <span className="footer-separator">/</span> EARLY BUILD</span>
          <span>Built for curious minds.</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
