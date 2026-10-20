import argparse
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

from flask import Flask, abort, render_template, send_file, url_for
from markdown_it import MarkdownIt


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = PROJECT_ROOT / "codedocplus.json"
DEFAULT_THEME = {
    "accent": "#c6532f",
    "background": "#f3f0e8",
    "surface": "#fffdf8",
    "text": "#25271f",
    "muted": "#74776b",
    "border": "#d9d5c9",
}
THEME_KEYS = set(DEFAULT_THEME)
COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$")


def load_site_config(config_path: str | Path | None, docs_dir: str | Path | None):
    config_file = Path(config_path).expanduser().resolve() if config_path else DEFAULT_CONFIG
    config = {}
    if config_path is not None and not config_file.is_file():
        raise ValueError(f"site config file does not exist: {config_file}")
    if config_file.is_file():
        try:
            with config_file.open(encoding="utf-8") as config_stream:
                config = json.load(config_stream)
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"could not read site config {config_file}: {error}") from error
        if not isinstance(config, dict):
            raise ValueError("site config must contain a JSON object")

    title = config.get("title", "CodeDocPlus")
    tagline = config.get(
        "tagline",
        "A quiet, searchable home for the knowledge tucked inside your code.",
    )
    if not isinstance(title, str) or not title.strip():
        raise ValueError("site config 'title' must be a non-empty string")
    if not isinstance(tagline, str):
        raise ValueError("site config 'tagline' must be a string")

    configured_docs = docs_dir if docs_dir is not None else config.get("docs_dir", "docs")
    if not isinstance(configured_docs, (str, Path)):
        raise ValueError("site config 'docs_dir' must be a path string")
    docs_path = Path(configured_docs).expanduser()
    if not docs_path.is_absolute():
        docs_path = config_file.parent / docs_path
    docs_path = docs_path.resolve()
    if not docs_path.is_dir():
        raise ValueError(f"documentation directory does not exist: {docs_path}")

    configured_theme = config.get("theme", {})
    if not isinstance(configured_theme, dict):
        raise ValueError("site config 'theme' must be a JSON object")
    unknown_colors = set(configured_theme) - THEME_KEYS
    if unknown_colors:
        raise ValueError(f"unknown theme color(s): {', '.join(sorted(unknown_colors))}")
    theme = {**DEFAULT_THEME, **configured_theme}
    for key, color in theme.items():
        if not isinstance(color, str) or not COLOR_PATTERN.fullmatch(color):
            raise ValueError(f"site config theme '{key}' must be a 3- or 6-digit hex color")

    custom_css = config.get("custom_css")
    if custom_css is not None:
        if not isinstance(custom_css, str) or not custom_css:
            raise ValueError("site config 'custom_css' must be a CSS file path")
        css_path = Path(custom_css).expanduser()
        if not css_path.is_absolute():
            css_path = config_file.parent / css_path
        css_path = css_path.resolve()
        if css_path.suffix.lower() != ".css" or not css_path.is_file():
            raise ValueError(f"custom CSS file does not exist or is not a .css file: {css_path}")
        custom_css = css_path

    return {
        "title": title.strip(),
        "tagline": tagline.strip(),
        "docs_path": docs_path,
        "theme": theme,
        "custom_css": custom_css,
    }


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def document_files(docs_root: Path):
    documents = []
    for path in docs_root.rglob("*.md"):
        if any(part.startswith(".") for part in path.relative_to(docs_root).parts):
            continue
        resolved = path.resolve()
        if path.is_file() and is_within(resolved, docs_root):
            documents.append(resolved)
    return sorted(documents, key=lambda item: item.relative_to(docs_root).as_posix().casefold())


def document_record(path: Path, docs_root: Path):
    relative_path = path.relative_to(docs_root).as_posix()
    title = path.stem.replace("-", " ").replace("_", " ").strip().title()
    return {"path": relative_path, "title": title}


def heading_slug(text: str) -> str:
    slug = re.sub(r"[^\w-]+", "-", text.casefold(), flags=re.UNICODE).strip("-")
    return slug or "section"


def local_target_path(destination: str, document_path: str):
    parsed = urlsplit(destination)
    if parsed.scheme or parsed.netloc or destination.startswith("/"):
        return None
    parent = posixpath.dirname(document_path)
    resolved = posixpath.normpath(posixpath.join(parent, parsed.path))
    if resolved == ".." or resolved.startswith("../"):
        return None
    return resolved, parsed


def markdown_renderer():
    return MarkdownIt("commonmark", {"html": False}).enable("table").enable("strikethrough")


def render_markdown(source: str, document_path: str):
    parser = markdown_renderer()
    tokens = parser.parse(source)
    toc = []
    slug_counts = {}

    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            inline = tokens[index + 1]
            slug_base = heading_slug(inline.content)
            count = slug_counts.get(slug_base, 0)
            slug_counts[slug_base] = count + 1
            slug = slug_base if count == 0 else f"{slug_base}-{count + 1}"
            token.attrSet("id", slug)
            toc.append(
                {
                    "level": int(token.tag[1]),
                    "title": inline.content,
                    "id": slug,
                }
            )

    for token in tokens:
        nested = token.children or []
        for child in nested:
            if child.type == "link_open":
                href = child.attrGet("href")
                target = local_target_path(href, document_path) if href else None
                if target and target[0].lower().endswith(".md"):
                    child.attrSet(
                        "href",
                        url_for("show_document", document=target[0])
                        + (f"?{target[1].query}" if target[1].query else "")
                        + (f"#{quote(target[1].fragment, safe='')}" if target[1].fragment else ""),
                    )
            elif child.type == "image":
                src = child.attrGet("src")
                target = local_target_path(src, document_path) if src else None
                if target:
                    child.attrSet(
                        "src",
                        url_for("show_asset", asset=target[0])
                        + (f"?{target[1].query}" if target[1].query else "")
                        + (f"#{quote(target[1].fragment, safe='')}" if target[1].fragment else ""),
                    )

    return parser.renderer.render(tokens, parser.options, {}), toc


def create_app(config_path: str | Path | None = None, docs_dir: str | Path | None = None):
    settings = load_site_config(config_path, docs_dir)
    app = Flask(__name__)
    app.config.update(
        SITE_TITLE=settings["title"],
        TAGLINE=settings["tagline"],
        DOCS_ROOT=settings["docs_path"],
        THEME=settings["theme"],
        CUSTOM_CSS=settings["custom_css"],
    )

    @app.context_processor
    def inject_site_settings():
        return {
            "site_title": app.config["SITE_TITLE"],
            "tagline": app.config["TAGLINE"],
            "theme": app.config["THEME"],
            "custom_css": app.config["CUSTOM_CSS"],
        }

    @app.get("/")
    def index():
        documents = [
            document_record(path, app.config["DOCS_ROOT"])
            for path in document_files(app.config["DOCS_ROOT"])
        ]
        return render_template("index.html", documents=documents, page_title="Library")

    @app.get("/docs/<path:document>")
    def show_document(document: str):
        if not document.lower().endswith(".md"):
            abort(404)
        root = app.config["DOCS_ROOT"]
        path = (root / document).resolve()
        if not is_within(path, root) or not path.is_file():
            abort(404)
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            app.logger.exception("Could not read documentation file %s", path)
            abort(500)
        rendered, toc = render_markdown(source, path.relative_to(root).as_posix())
        documents = [
            document_record(item, root)
            for item in document_files(root)
        ]
        current = document_record(path, root)
        return render_template(
            "document.html",
            documents=documents,
            current_document=current["path"],
            document_title=current["title"],
            content=rendered,
            toc=toc,
            page_title=current["title"],
        )

    @app.get("/files/<path:asset>")
    def show_asset(asset: str):
        root = app.config["DOCS_ROOT"]
        path = (root / asset).resolve()
        if not is_within(path, root) or not path.is_file():
            abort(404)
        return send_file(path)

    @app.get("/custom.css")
    def custom_stylesheet():
        path = app.config["CUSTOM_CSS"]
        if path is None:
            abort(404)
        return send_file(path, mimetype="text/css")

    return app


def main():
    argument_parser = argparse.ArgumentParser(description="Serve Markdown documentation as a website.")
    argument_parser.add_argument("--config", help="path to a CodeDocPlus JSON site config")
    argument_parser.add_argument("--docs-dir", help="override the documentation directory in the config")
    argument_parser.add_argument("--host", default="127.0.0.1", help="interface to bind (default: 127.0.0.1)")
    argument_parser.add_argument("--port", type=int, default=8000, help="port to bind (default: 8000)")
    args = argument_parser.parse_args()

    app = create_app(args.config, args.docs_dir)
    app.run(host=args.host, port=args.port)


app = create_app()


if __name__ == "__main__":
    main()
