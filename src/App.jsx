import { useEffect, useState } from "react";
import { Routes, Route, Link, useParams, useLocation } from "react-router-dom";
import { documents } from "./docs.js";
import { renderMarkdown } from "./markdown.js";
import { useTheme } from "./useTheme.js";
import config from "./config.js";

const themeVars = {
  "--ink": config.theme.text,
  "--paper": config.theme.background,
  "--sheet": config.theme.surface,
  "--accent": config.theme.accent,
  "--muted": config.theme.muted,
  "--rule": config.theme.border,
};

function SearchBox({ onQuery }) {
  return (
    <div className="sidebar-section">
      <label className="search-box">
        <span className="search-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
        </span>
        <input
          id="document-search"
          type="search"
          placeholder="Search pages"
          autoComplete="off"
          aria-label="Filter documentation pages"
          onChange={(e) => onQuery(e.target.value)}
        />
        <kbd>/</kbd>
      </label>
    </div>
  );
}

function ThemeToggle() {
  const { label, cycle } = useTheme();
  return (
    <button className="theme-toggle" onClick={cycle} aria-label="Toggle color theme">
      <svg className="toggle-icon toggle-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
      </svg>
      <svg className="toggle-icon toggle-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
      </svg>
      <span className="toggle-label">{label}</span>
    </button>
  );
}

function SidebarContent({ query, setQuery, currentPath, onClose, sidebarOpen }) {
  const q = query.trim().toLowerCase();
  const visible = documents.filter((d) => d.title.toLowerCase().includes(q));

  return (
    <aside className={`sidebar${sidebarOpen ? " is-open" : ""}`}>
      <div className="sidebar-head">
        <Link className="brand" to="/" aria-label={`${config.title} home`} onClick={onClose}>
          <span className="brand-name">
            {config.title}
            <small>{config.tagline}</small>
          </span>
        </Link>
        <button className="icon-only" onClick={onClose} aria-label="Close sidebar" hidden>
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <SearchBox onQuery={setQuery} />

      <div className="sidebar-overflow">
        <nav className="sidebar-section document-nav" aria-label="Documentation">
          <p className="section-label">Pages</p>
          {visible.length === 0 && q && <p className="search-empty">No matching pages.</p>}
          {visible.length === 0 && !q && <p className="nav-empty">No pages yet.</p>}
          {visible.map((d) => (
            <Link
              key={d.path}
              className={`document-link${d.path === currentPath ? " is-current" : ""}`}
              to={`/docs/${d.path}`}
              data-document-link
              onClick={onClose}
            >
              {d.title}
            </Link>
          ))}
        </nav>
      </div>

      <div className="sidebar-footer">
        <ThemeToggle />
      </div>
    </aside>
  );
}

function LibraryPage() {
  return (
    <section className="library-page">
      <p className="page-eyebrow">Documentation</p>
      <div className="library-intro">
        <h1>{config.title}</h1>
        <p>{config.tagline}</p>
      </div>
      <div className="library-meta">
        <span>
          {documents.length} {documents.length === 1 ? "page" : "pages"}
        </span>
        <span className="meta-line" />
        <span>{config.title}</span>
      </div>

      {documents.length > 0 ? (
        <div className="document-grid">
          {documents.map((d, i) => (
            <Link className="document-card" key={d.path} to={`/docs/${d.path}`}>
              <span className="card-index">{String(i + 1).padStart(2, "0")}</span>
              <span className="card-kicker">{d.path}</span>
              <span className="card-title">{d.title}</span>
              <span className="card-open">Read →</span>
            </Link>
          ))}
        </div>
      ) : (
        <div className="empty-library">
          <h2>No pages yet</h2>
          <p>Add a Markdown file to the configured documentation folder and it will appear here.</p>
        </div>
      )}
    </section>
  );
}

function DocumentPage() {
  const { document } = useParams();
  const doc = documents.find((d) => d.path === document);
  if (!doc) {
    return (
      <div className="document-page">
        <p className="page-eyebrow">Not found</p>
        <div className="document-heading">
          <h1>Page not found</h1>
          <Link className="back-link" to="/docs/docs.md">← All pages</Link>
        </div>
      </div>
    );
  }
  const { html, toc } = renderMarkdown(doc.content);
  return (
    <div className="document-page">
      <p className="page-eyebrow">{doc.path}</p>
      <div className="document-heading">
        <h1>{doc.title}</h1>
        <Link className="back-link" to="/">← All pages</Link>
      </div>
      <div className="document-layout">
        <article className="markdown-body" dangerouslySetInnerHTML={{ __html: html }} />
        {toc.length > 0 && (
          <aside className="toc-panel" aria-label="On this page">
            <p className="toc-title">On this page</p>
            <nav>
              {toc.map((item) => (
                <a key={item.id} className={`toc-link toc-level-${item.level}`} href={`#${item.id}`}>
                  {item.title}
                </a>
              ))}
            </nav>
          </aside>
        )}
      </div>
    </div>
  );
}

function useScrollTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
}

export default function App() {
  const [query, setQuery] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  useScrollTop();

  const currentPath = location.pathname.replace(/^\/docs\//, "");
  const pageTitle = currentPath && currentPath !== "" ? documents.find((d) => d.path === currentPath)?.title || "Library" : "Library";

  return (
    <div style={themeVars}>
      <div className={`scrim${sidebarOpen ? " is-open" : ""}`} onClick={() => setSidebarOpen(false)} />
      <div className="site-shell">
        <SidebarContent
          query={query}
          setQuery={setQuery}
          currentPath={currentPath}
          onClose={() => setSidebarOpen(false)}
          sidebarOpen={sidebarOpen}
        />
        <main className="main-area">
          <header className="topbar">
            <div className="topbar-left">
              <button className="menu-button" onClick={() => setSidebarOpen(true)} aria-label="Open sidebar">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M3 6h18M3 12h18M3 18h18" />
                </svg>
                Menu
              </button>
              <div className="breadcrumb">
                <span>{config.title}</span>
                <span className="crumb-sep">/</span>
                <span className="crumb-current">{pageTitle}</span>
              </div>
            </div>
            <div className="topbar-actions">
              <Link className="topbar-link" to="/">All pages</Link>
            </div>
          </header>

          <Routes>
            <Route path="/" element={<LibraryPage />} />
            <Route path="/docs/:document" element={<DocumentPage />} />
          </Routes>

          <footer className="page-footer">
            <span>{config.title}</span>
            <span className="footer-line" />
            <span>Documentation</span>
          </footer>
        </main>
      </div>
    </div>
  );
}


