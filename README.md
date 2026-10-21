<h1 align="center">CodeDocPlus</h1>

<p align="center">
  Write docs in your code comments. Get Markdown and a searchable docs site.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey" alt="Platform">
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#docs-site">Docs site</a> ·
  <a href="#supported-languages">Languages</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ru.md">Русский</a>
</p>

---

CodeDocPlus pulls documentation out of special comments in your source files and writes it to Markdown, keeping your folder structure. It also ships a small web server that turns those Markdown files into a docs site with search, a table of contents, and light/dark themes.

- **No dependencies for the CLI.** Pure Python 3.10+ standard library.
- **25+ languages.** C, C++, Rust, Go, Python, TypeScript, Java, Swift, Zig, Lua, and more.
- **Docs live next to the code.** Mark a region with a comment, and it shows up in the output.
- **Built-in docs site.** Sidebar navigation, sticky table of contents, search (press `/`), and light/dark mode.
- **Themeable.** Colors, fonts, code highlighting, logo, and footer are set in one JSON file.

## Quick start

Install:

```bash
# Linux / macOS
curl -fsSL https://raw.githubusercontent.com/vortex3964/CodeDoc/main/install/install.sh | bash
```

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/vortex3964/CodeDoc/main/install/install.ps1 | iex
```

Mark up some code:

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

Generate Markdown:

```bash
codedoc src/ -o docs/api
```

Serve it:

```bash
pip install -r requirements.txt
python web.py
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
source files  →  codedoc (parser)  →  Markdown  →  web.py  →  docs site
```

## CLI reference

```
codedoc [path] [-o OUT] [-exd DIRS ...] [-exf FILES ...] [-c] [-ca]
```

| Option | Default | Description |
|:---|:---|:---|
| `path` | `.` | Directory to scan |
| `-o`, `--output` | `out` | Output Markdown file (`.md` is added for you) |
| `-exd`, `--exclude-dirs` | built-in list | Extra directories to skip |
| `-exf`, `--exclude-files` | none | Specific files to skip |
| `-c`, `--clean` | off | Remove `Doc end` markers from source files after reading |
| `-ca`, `--cleanall` | off | Remove all `Doc` markers, leaving plain source |
| `--update` | | Install the latest release |
| `--uninstall` | | Remove the launcher and PATH entry |

More examples:

```bash
# Scan the current directory, write out.md
codedoc

# Skip folders and files
codedoc . -o out -exd test build cache -exf setup.py

# Run without installing
python3 main.py src/ -o docs/overview
```

## Docs site

`web.py` serves any folder of Markdown files.

```bash
python web.py --docs-dir path/to/markdown --port 5000 --host 0.0.0.0
python web.py --config path/to/production.json
```

### Configuration

Create a `codedocplus.json` in your project root:

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
├── main.py             # CLI entry point and file crawler
├── parser.py           # Comment parsing and Markdown generation
├── langs.py            # Per-language comment syntax
├── web.py              # Flask docs server
├── codedocplus.json    # Site config
├── requirements.txt    # Server dependencies (Flask, markdown-it-py)
├── install/            # install and uninstall scripts (sh, ps1)
├── static/             # site.css, site.js
└── templates/          # base.html, index.html, document.html
```

## Install options

```bash
# Don't touch shell rc files
bash install/install.sh --no-modify-path

# Install from a local checkout
bash install/install.sh --local /path/to/CodeDocPlus

# Uninstall
codedoc --uninstall
```

The installer puts `codedoc` in `~/.local/bin` (Linux/macOS) or `%LOCALAPPDATA%\codedoc\bin` (Windows) and adds it to your `PATH`.

## Contributing

Issues and pull requests are welcome. For larger changes, open an issue first so we can talk it through.

## License

[MIT](LICENSE)