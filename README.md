# CodeDocPlus

A documentation tool that turns specialized `Doc` comments into Markdown and serves Markdown files as a customizable website.

It scans a directory recursively, extracts every `Doc` comment block from the supported languages, and writes the result to a markdown file in the same order as the files on disk.

## Installation

**Linux / macOS** (requires Python 3.10+ and curl):

```
curl -fsSL https://raw.githubusercontent.com/vortex3964/CodeDoc/main/install/install.sh | bash
```

**Windows** (requires Python 3.10+):

```
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/vortex3964/CodeDoc/main/install/install.ps1 | iex"
```

This installs the `codedoc` command to `~/.local/bin` (Linux/macOS) or `%LOCALAPPDATA%\codedoc\bin` (Windows) and adds it to your PATH. Open a new terminal and run `codedoc` from anywhere.

Installer options (`install/install.sh`): `--no-modify-path` to skip touching your shell config, `--local <dir>` to install from a local copy of the project (useful for development).

Uninstall:

```
bash install/uninstall.sh                    # Linux/macOS
powershell -File install/uninstall.ps1       # Windows
```

## Updating

`codedoc --update` checks for and applies the latest version, it only updates and skips the documentation run:

```
codedoc --update
```

Every normal run also checks for updates at the end and prints a note when a newer version is available, the check runs after the documentation is written so it never slows the file reading down.

Uninstall with the tool itself:

```
codedoc --uninstall
```

or with the script:

```
bash install/uninstall.sh
```

## Requirements

- Python 3.10 or newer
- no pip needed

## Usage

```
codedoc [path] [-o OUT] [-exd DIRS ...] [-exf FILES ...] [-c] [-ca]
```

| Option | Description |
| --- | --- |
| `path` | directory to scan, defaults to the current directory |
| `-o`, `--output` | output file name, `.md` is appended automatically, defaults to `out` |
| `-exd`, `--exclude-dirs` | directories to skip (in addition to the built-in ignore list) |
| `-exf`, `--exclude-files` | files to skip |
| `-c`, `--clean` | remove `Doc end` comments from the source files (documents them first) |
| `-ca`, `--cleanall` | remove every doc comment and `Doc end` from the source files, the code stays (documents them first) |
| `--update` | update codedoc to the latest version, skips the documentation run |
| `--uninstall` | remove codedoc, its launcher and the path lines, skips the documentation run |

Examples:

```
codedoc                            # scan "." and write out.md
codedoc src/ -o docs/api           # scan src/ and write docs/api.md
codedoc . -o out -exd test build -exf setup.py
```

Running from source instead (no install needed):

```
python3 main.py [path] [-o OUT] [-exd DIRS ...] [-exf FILES ...]
```

## Serve the docs as a website

CodeDocPlus can serve Markdown files as a browsable documentation site. Install
the web dependencies and start the local server:

```
python -m pip install -r requirements.txt
python web.py
```

Open `http://127.0.0.1:8000`. By default, the site reads Markdown files from
the `docs/` directory, including nested folders. You can select another folder
when starting the site:

```
python web.py --docs-dir path/to/markdown
```

Customize the site using `codedocplus.json`:

```json
{
  "title": "My Project",
  "tagline": "Notes and guides for the team.",
  "docs_dir": "docs",
  "theme": {
    "accent": "#c6532f",
    "background": "#f3f0e8",
    "surface": "#fffdf8",
    "text": "#25271f",
    "muted": "#74776b",
    "border": "#d9d5c9"
  },
  "custom_css": "site-overrides.css"
}
```

Paths in the config are relative to the config file. `custom_css` is optional;
use it to override the site's styles. The theme colors accept three- or
six-digit hex values. Pass `--config path/to/config.json` to use another
configuration file. The server binds to `127.0.0.1` by default; use `--host`
and `--port` to change its address.

The site includes page navigation, a keyboard-focusable page filter (`/`),
per-page heading links, Markdown tables and code fences, relative links to
other Markdown pages, and images/assets stored inside the documentation
folder. Raw HTML embedded in Markdown is not rendered.

Notes:

- the output directory must already exist,
- the output file is truncated at the start of every run,
- files without any `Doc` comment are skipped,
- ignored by default: `.git`, `node_modules`, `venv`, `__pycache__`, `dist`, `build`, `out`, `target`, `bin`, `obj`, and other common build/tooling directories, plus a list of binary extensions (`.pyc`, `.o`, `.png`, `.zip`, ...).

## Doc comment syntax

Doc comments look like normal comments, but start with the word `Doc`. The comment token depends on the language .

Three tags are recognized:

| Tag | Meaning |
| --- | --- |
| `Doc` | starts a section with no heading, everything until the next tag is emitted as code |
| `Doc code : name` | starts a section with a `## name` heading; a leading comment block becomes description text, the rest is emitted as code |
| `Doc end` | ends the current section |

Example in C:

```c
//Doc
#include <stdio.h>

//Doc code : hello world program
/*
 * hello world program
 * */

int main(void)
{
    printf("hello world");
    return 0;
}

//Doc end
```

Generates:

````markdown
# main.c

```c
#include <stdio.h>
```

## hello world program

hello world program  

```c
int main(void)
{
    printf("hello world");
    return 0;
}
```

````

## Supported languages

| Extension(s) | Single line | Multi line |
| --- | --- | --- |
| `.c .h .cpp .cc .cxx .hpp .hh .cs .java .js .jsx .ts .tsx .go .rs .d .swift .kt .kts .php .dart .scala .mm` | `//` | `/* */` |
| `.pas .pp .inc .fs` | `//` | `(* *)` |
| `.zig` | `//` | `//` (derived) |
| `.py .pyw .pyi` | `#` | `""" """` |
| `.erlang` | `#` | `#` (derived) |
| `.lua` | `--` | `--[[ ]]` |
| `.hs` | `--` | `{- -}` |
| `.asm .s` | `;` | `;` (derived) |
| `.vb .vbs .bas` | `'` | `'` (derived) |
| `.tex .sty .cls` | `%` | `%` (derived) |
| `.m` | `%` | `%{ }%` |
| `.html .htm .xhtml .xml` | `<!-- -->` (derived) | `<!-- -->` |

Languages with only one comment family derive the other from it: a language with only single line comments treats a run of consecutive comment lines as a multi line block, and a language with only multi line comments uses the pair as a single line comment (e.g. `<!--Doc-->` in HTML).

## Project layout

- `main.py` — argument parsing and file listing
- `parser.py` — comment extraction and markdown generation, runs one async worker per file and preserves the file order in the output
- `langs.py` — supported languages, comment tokens and the extension to family conversion tables
- `install/` — the curl/PowerShell installers and uninstallers for Linux, macOS and Windows

## Generating this project's own docs

The project documents itself with the command:

```
python3 main.py . -o docs -exd test
```
The documentation is in a docs dir in the project
