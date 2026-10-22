<div align="center">
  <img src="logo.png" width="30%">
  
  ![GitHub Repo Banner](https://ghrb.waren.build/render/banner?header=CodeDocPlus&subheader=Generate+searchable+docs+from+code+comments.&bg=00000000&color=FFFFFF&headerfont=DynaPuff&subheaderfont=Cherry+Cream+Soda&support=false)
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey" alt="Platform">
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#cli-reference">CLI Reference</a> ·
  <a href="#docs-site">Docs site</a> ·
  <a href="#supported-languages">Languages</a>
</p>

---

CodeDocPlus pulls documentation out of special comments in your source files, formats it into clean Markdown, and ships a built-in searchable web server with navigation, dark mode, and customizable themes.

- **Zero dependencies for generating docs.** Core CLI runs on pure Python 3.10+ standard library.
- **Built-in docs viewer.** Run `cdp serve` or `cdp preview` with lazy-loaded dependencies.
- **25+ languages.** C, C++, Rust, Go, Python, TypeScript, Java, Swift, Zig, Lua, and more.
- **Docs live next to code.** Mark a region with a comment, and it shows up in the output.
- **Search & Themes.** Sidebar navigation, sticky table of contents, fast search (`/`), and light/dark mode.
- **Themeable.** Colors, fonts, code highlighting, and branding in a single `codedocplus.json`.

## Quick start

### Install

```bash
# Linux / macOS
curl -fsSL https://raw.githubusercontent.com/Terminay/CodeDocPlus/main/install/install.sh | bash
```

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/Terminay/CodeDocPlus/main/install/install.ps1 | iex
```

### Mark up some code

```c
//Doc code : Entry point
/*
 * Boots the system and verifies memory.
 */
int main(void)
{
    printf("hello\n");
    return 0;
}
//Doc end
```

### Generate Markdown

```bash
cdp build src/ -o docs/api
```

### Serve the docs website

```bash
cdp serve
```

### Or do both in one step:

```bash
cdp preview src/
```

Open <http://127.0.0.1:8000>.

## How it works

Three comment markers control extraction:

| Marker | What it does |
|:---|:---|
| `Doc` | Starts an untitled section. The code that follows is captured as a code block. |
| `Doc code : <title>` | Starts a section with a `## <title>` heading. A comment block right after it becomes the description, and the code after that becomes the code block. |
| `Doc end` | Closes the current section. |

The C example above produces:

````markdown
# main.c

## Entry point

Boots the system and verifies memory.

```c
int main(void)
{
    printf("hello\n");
    return 0;
}
```
````

Files are scanned concurrently, and the output mirrors your directory layout.

```
source files  →  cdp build (parser)  →  Markdown  →  cdp serve (web)  →  docs site
```

## CLI reference

CodeDocPlus can be invoked via `cdp` or `codedocplus`:

```bash
cdp <command> [options]
```

### Available commands:

| Command | Alias | Description |
|:---|:---|:---|
| `cdp build [path]` | `generate` | Scans source files and generates documentation Markdown |
| `cdp serve` | `web` | Starts the Flask web server to view the documentation |
| `cdp preview [path]` | | Generates documentation into `/docs` and immediately opens the web viewer |
| `cdp init` | | Creates a starter `codedocplus.json` in the current working directory |
| `cdp update` | | Checks for and installs the latest version from GitHub |
| `cdp uninstall` | | Removes the launcher, installation files, and PATH entries |

---

### `cdp build [path]` options

```text
cdp build [path] [-o OUT] [-exd DIRS ...] [-exf FILES ...] [-c] [-ca]
```

| Option | Default | Description |
|:---|:---|:---|
| `path` | `.` | Directory to scan |
| `-o`, `--output` | `out` | Output Markdown file (`.md` is added automatically) |
| `-exd`, `--exclude-dirs` | built-in list | Extra directories to skip |
| `-exf`, `--exclude-files` | none | Specific files to skip |
| `-c`, `--clean` | off | Remove `Doc end` markers from source files after reading |
| `-ca`, `--cleanall` | off | Remove all `Doc` markers, leaving plain source |

---

### `cdp serve` options

```text
cdp serve [--docs-dir DIR] [--config CONFIG] [--host HOST] [--port PORT] [--open]
```

| Option | Default | Description |
|:---|:---|:---|
| `--docs-dir` | `docs` | Directory containing Markdown documentation |
| `--config` | `codedocplus.json` | Path to site config |
| `--host` | `127.0.0.1` | Network interface to bind |
| `--port` | `8000` | Port to bind |
| `--open` | off | Automatically open default browser on launch |

---

### `cdp preview [path]` options

```text
cdp preview [path] [-o OUT] [--port PORT] [--host HOST] [--no-open]
```

Generates Markdown into the local `docs/` folder (default `docs/index.md`) and starts the server with browser auto-open enabled.

---

## Docs site configuration

Run `cdp init` or create a `codedocplus.json` in your project root:

```json
{
  "title": "My Project Docs",
  "tagline": "API reference generated from source.",
  "docs_dir": "docs",
  "logo": "assets/logo.png",
  "footer_text": "Built with CodeDocPlus",

  "theme": {
    "accent": "#c6532f",
    "background": "#f5f5f5",
    "surface": "#ffffff",
    "text": "#333333",
    "navbar_bg": "#c6532f",
    "navbar_text": "#ffffff",
    "font_family": "'Helvetica Neue', Arial, sans-serif",
    "sidebar_width": "260px",
    "code_theme": "dark"
  },

  "custom_css": "site-overrides.css"
}
```

<details>
<summary>All theme options</summary>

| Key | Default | Description |
|:---|:---|:---|
| `accent` | `#c6532f` | Links and highlights |
| `accent_dark` | `#a03d1e` | Hover color |
| `background` | `#f5f5f5` | Page background |
| `surface` | `#ffffff` | Sidebar, cards, panels |
| `text` | `#333333` | Body text |
| `muted` | `#888888` | Secondary text |
| `border` | `#e0e0e0` | Borders and dividers |
| `navbar_bg` | `#c6532f` | Top bar background |
| `navbar_text` | `#ffffff` | Top bar text and icons |
| `font_family` | `'Helvetica Neue', Arial, sans-serif` | Global font stack |
| `sidebar_width` | `260px` | Sidebar width |
| `code_theme` | `dark` | `dark`, `light`, `monokai`, or `github` |

</details>

## Supported languages

| Language family | Extensions | Single-line | Multi-line |
|:---|:---|:---:|:---:|
| C-style | `.c` `.h` `.cpp` `.cc` `.cxx` `.hpp` `.hh` `.cs` `.java` `.js` `.jsx` `.ts` `.tsx` `.go` `.rs` `.d` `.swift` `.kt` `.kts` `.php` `.dart` `.scala` `.mm` | `//` | `/* ... */` |
| Pascal / F# | `.pas` `.pp` `.inc` `.fs` | `//` | `(* ... *)` |
| Python | `.py` `.pyw` `.pyi` | `#` | `""" ... """` |
| Erlang | `.erlang` | `#` | `#` |
| Lua / Haskell | `.lua` `.hs` | `--` | `--[[ ]]` / `{- -}` |
| Assembly | `.asm` `.s` | `;` | `;` |
| Basic | `.vb` `.vbs` `.bas` | `'` | `'` |
| TeX / MATLAB | `.tex` `.sty` `.cls` `.m` | `%` | `%{ ... }%` |
| HTML / XML | `.html` `.htm` `.xhtml` `.xml` | `<!-- -->` | `<!-- ... -->` |
| Zig | `.zig` | `//` | `//` |

## Project layout

```
.
├── main.py             # CLI entry point (build, serve, preview, init, update)
├── parser.py           # Comment parsing and Markdown generation
├── langs.py            # Per-language comment syntax
├── web.py              # Flask docs server and Markdown renderer
├── codedocplus.json    # Default site config template
├── requirements.txt    # Server dependencies (Flask, markdown-it-py)
├── install/            # Install and uninstall scripts (install.sh, install.ps1)
├── static/             # site.css, site.js
└── templates/          # base.html, index.html, document.html
```

## Contributing

Issues and pull requests are welcome. For larger changes, open an issue first so we can talk it through.

## License

[MIT](LICENSE)
