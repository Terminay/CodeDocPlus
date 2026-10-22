# Doc : Description
# main.py processes the command line flags and starts the
# dispatcher to generate the documentation, it also checks
# for updates at the end of every run and can update itself
# or launch the CodeDocPlus web server.

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from parser import dispatch
from pathlib import Path

# Doc : list of ignored directories, extensions and files
# we keep lists called IGNORE_DIRS IGNORE_EXTENSIONS IGNORE_FILES of the
# files we would like to ignore like hidden files (.git) or .exe files we
# shouldn't bother reading
IGNORE_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "vendor",
    "bower_components",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "dist",
    "build",
    "out",
    "target",
    ".next",
    ".nuxt",
    "bin",
    "obj",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".idea",
    ".vscode",
    ".vs",
    ".gradle",
    ".terraform",
    "coverage",
    "site-packages",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".class",
    ".o",
    ".so",
    ".dll",
    ".dylib",
    ".exe",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".rar",
    ".7z",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".webp",
    ".mp3",
    ".mp4",
    ".wav",
    ".avi",
    ".mov",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".bin",
    ".lock",
    ".mod",
}

IGNORE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    ".gitignore",
}


# Doc code : recursive listing of all the files in the directories
# walks the root directory recursively and returns the sorted
# list of files to parse, skipping the ignored directories,
# extensions, files and the user excluded ones


def list_files_req(root_dir, exc_dirs: list, exc_files: list):
    files = []
    exc_dirs = exc_dirs or []
    exc_files = exc_files or []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [
            d for d in dirnames if (d not in exc_dirs and d not in IGNORE_DIRS)
        ]

        for fname in filenames:
            if fname in IGNORE_FILES or fname in exc_files:
                continue
            ext = Path(fname).suffix.lower()

            if ext in IGNORE_EXTENSIONS:
                continue

            # keep the walk path as-is so workers can open the file
            # from the current working directory, it also gets
            # displayed in the end file
            files.append(os.path.join(dirpath, fname))

    files.sort()
    return files


# Doc end

# Doc : update helpers
# the update check compares the installed copy against the latest
# commit on github, it runs at the end of main so the file reading
# is never slowed down by the network, it stays quiet when there
# is no connection or a rate limit and it skips dev checkouts

REPO = "Terminay/CodeDocPlus"
BRANCH = "main"
APP = "codedocplus"
COMMITS_URL = f"https://api.github.com/repos/{REPO}/commits/{BRANCH}"
TARBALL_URL = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.tar.gz"


def get_install_dir() -> str | None:
    # the launcher runs main.py from the install dir, so the script's
    # own location is the install, a dev checkout has a .git folder
    d = os.path.dirname(os.path.realpath(__file__))
    if os.path.isdir(os.path.join(d, ".git")):
        return None
    return d


def fetch_latest_commit() -> str | None:
    try:
        with urllib.request.urlopen(COMMITS_URL, timeout=5) as resp:
            data = json.load(resp)
        return data.get("sha")
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        return None


def apply_update(install_dir: str, latest: str) -> bool:
    tmp = tempfile.mkdtemp(prefix="codedocplus-")
    try:
        tarball = os.path.join(tmp, "codedocplus.tar.gz")
        urllib.request.urlretrieve(TARBALL_URL, tarball)
        with tarfile.open(tarball, "r:gz") as tf:
            tf.extractall(tmp)

        # find the extracted project folder, a broken tarball
        # simply has no main.py and the update is aborted
        src = None
        for entry in os.listdir(tmp):
            if os.path.isfile(os.path.join(tmp, entry, "main.py")):
                src = os.path.join(tmp, entry)
                break
        if src is None:
            return False

        for entry in os.listdir(src):
            source = os.path.join(src, entry)
            target = os.path.join(install_dir, entry)
            if os.path.isdir(source):
                shutil.rmtree(target, ignore_errors=True)
                shutil.copytree(source, target)
            else:
                try:
                    os.replace(source, target)
                except OSError:
                    shutil.copy2(source, target)

        with open(os.path.join(install_dir, ".commit"), "w") as f:
            f.write(latest)
        return True
    except (urllib.error.URLError, OSError, tarfile.ReadError, EOFError):
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def read_stamp(commit_file: str) -> str | None:
    try:
        if not os.path.isfile(commit_file):
            return None
        with open(commit_file) as f:
            return f.read().strip()
    except OSError:
        return None


async def check_for_update(apply: bool):
    install_dir = get_install_dir()
    if install_dir is None:
        if apply:
            print("cdp update only works on an installed copy, use git pull in a dev checkout")
        return

    latest = await asyncio.to_thread(fetch_latest_commit)
    if latest is None:
        if apply:
            print("couldn't check for updates, check your network connection")
        return

    current = await asyncio.to_thread(read_stamp, os.path.join(install_dir, ".commit"))

    if current is not None and current == latest:
        if apply:
            print(f"CodeDocPlus is already up to date ({current[:7]})")
        return

    if not apply:
        print("a new version of CodeDocPlus is available, run 'cdp update' to update")
        return

    if await asyncio.to_thread(apply_update, install_dir, latest):
        print(f"CodeDocPlus updated: {current[:7] if current else 'unknown'} -> {latest[:7]}")
    else:
        print("update failed, try again later")


# Doc : uninstall helper
# removes the launcher, the install dir and the path lines the
# installer added to the shell configs, a dev checkout is left
# alone


def uninstall_self() -> None:
    install_dir = get_install_dir()
    if install_dir is None:
        print(f"{APP} uninstall only works on an installed copy, use git rm in a dev checkout")
        return

    bin_dir = os.environ.get(
        "XDG_BIN_HOME", os.path.join(os.path.expanduser("~"), ".local", "bin")
    )
    if os.name == "nt":
        target_dir = os.path.join(os.environ.get("LOCALAPPDATA", bin_dir), "bin")
        launchers = [
            os.path.join(target_dir, f"{APP}.cmd"),
            os.path.join(target_dir, "cdp.cmd"),
            os.path.join(target_dir, "codedoc.cmd"),
        ]
    else:
        launchers = [
            os.path.join(bin_dir, APP),
            os.path.join(bin_dir, "cdp"),
            os.path.join(bin_dir, "codedoc"),
        ]

    for launcher in launchers:
        try:
            os.remove(launcher)
        except OSError:
            pass

    if os.name != "nt":
        # remove the lines the installer added to shell configs
        removed = [
            f"# {APP}",
            "# codedoc",
            f"export PATH={bin_dir}:$PATH",
            f"fish_add_path {bin_dir}",
        ]
        configs = [
            os.path.expanduser("~/.bashrc"),
            os.path.expanduser("~/.bash_profile"),
            os.path.expanduser("~/.profile"),
            os.path.join(os.environ.get("ZDOTDIR", os.path.expanduser("~")), ".zshrc"),
            os.path.expanduser("~/.zshenv"),
            os.path.expanduser("~/.config/fish/config.fish"),
        ]
        for cfg in configs:
            try:
                with open(cfg) as f:
                    lines = f.readlines()
            except OSError:
                continue
            keep = [ln for ln in lines if ln.rstrip("\n") not in removed]
            if len(keep) == len(lines):
                continue
            with open(cfg, "w") as f:
                f.writelines(keep)

    shutil.rmtree(install_dir, ignore_errors=True)
    print(f"{APP} uninstalled")


def ensure_web_dependencies() -> bool:
    try:
        import flask  # noqa: F401
        import markdown_it  # noqa: F401
        return True
    except ModuleNotFoundError:
        print("[CodeDocPlus] The web documentation viewer requires 'flask' and 'markdown-it-py'.")
        is_interactive = hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
        if is_interactive:
            try:
                ans = input("Would you like to install them now using pip? [Y/n]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return False
            if ans in ("", "y", "yes"):
                print("Installing dependencies via pip...")
                try:
                    res = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "Flask>=3.0,<4.0", "markdown-it-py>=3.0,<5.0"],
                        check=False,
                    )
                    if res.returncode == 0:
                        print("Dependencies installed successfully.\n")
                        return True
                    else:
                        print("Failed to install dependencies.")
                        return False
                except Exception as e:
                    print(f"Error while running pip: {e}")
                    return False
        print("To install dependencies manually, run:")
        print('  pip install "Flask>=3.0,<4.0" "markdown-it-py>=3.0,<5.0"\n')
        return False


def run_serve(docs_dir=None, config_path=None, host="127.0.0.1", port=8000, open_browser=False):
    if not ensure_web_dependencies():
        return

    from web import create_app
    import webbrowser
    import threading

    try:
        app = create_app(config_path, docs_dir)
    except Exception as e:
        print(f"Error starting documentation server: {e}")
        return

    url = f"http://{host}:{port}"
    print(f"CodeDocPlus web server running at {url}")
    print("Press Ctrl+C to stop.")

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    app.run(host=host, port=port)


def cmd_init():
    target = Path.cwd() / "codedocplus.json"
    if target.exists():
        print("codedocplus.json already exists in the current directory.")
        return

    bundled = Path(__file__).resolve().parent / "codedocplus.json"
    if bundled.is_file():
        shutil.copy2(bundled, target)
        print("Created codedocplus.json in the current directory.")
    else:
        starter = {
            "title": "CodeDocPlus",
            "tagline": "A quiet, searchable home for the knowledge tucked inside your code.",
            "docs_dir": "docs",
            "theme": {
                "accent": "#c6532f",
                "accent_dark": "#a03d1e",
                "code_theme": "dark"
            }
        }
        with open(target, "w", encoding="utf-8") as f:
            json.dump(starter, f, indent=2)
        print("Created codedocplus.json in the current directory.")


async def cmd_build(args):
    file_list = list_files_req(args.path, args.exc_d, args.exc_f)

    out = args.out
    if not out.lower().endswith(".md"):
        out = f"{out}.md"

    await dispatch(file_list, out, args.clean, args.cleanall)
    print(f"documentation written to {out}")


async def cmd_preview(args):
    docs_dir = Path.cwd() / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute() and "docs" not in out_path.parts:
            out_file = docs_dir / out_path
        else:
            out_file = out_path
    else:
        out_file = docs_dir / "index.md"

    if out_file.suffix.lower() != ".md":
        out_file = out_file.with_suffix(".md")

    file_list = list_files_req(args.path, args.exc_d, args.exc_f)
    print(f"Generating documentation from '{args.path}' into '{out_file}'...")
    await dispatch(file_list, str(out_file), clean=False, cleanall=False)
    print(f"Documentation written to {out_file}")

    run_serve(
        docs_dir=str(docs_dir),
        config_path=args.config,
        host=args.host,
        port=args.port,
        open_browser=not args.no_open,
    )


# Doc: main
# parses the command line arguments, builds the file list and
# starts the dispatcher, web server or management tasks


async def main():
    parser = argparse.ArgumentParser(
        prog="cdp",
        description="cli tool to parse specialized comments from code files into markdown and serve docs website",
        epilog="Examples:\n  cdp build . -o docs/api\n  cdp serve\n  cdp preview .",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help="check for and apply the latest version",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="remove CodeDocPlus, launchers, and PATH entries",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # build
    p_build = subparsers.add_parser(
        "build",
        aliases=["generate"],
        help="parse code comments into Markdown documentation",
    )
    p_build.add_argument(
        "path",
        nargs="?",
        default=".",
        help="directory to read from (default: current directory)",
    )
    p_build.add_argument(
        "-o",
        "--output",
        dest="out",
        default="out",
        help="output path (default: out)",
    )
    p_build.add_argument(
        "-exd",
        "--exclude-dirs",
        dest="exc_d",
        nargs="*",
        help="directories to exclude from reading",
    )
    p_build.add_argument(
        "-exf",
        "--exclude-files",
        dest="exc_f",
        nargs="*",
        help="files to exclude from reading",
    )
    p_build.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="remove doc end comments from source files",
    )
    p_build.add_argument(
        "-ca",
        "--cleanall",
        action="store_true",
        help="remove every doc comment and doc end from source files",
    )

    # serve
    p_serve = subparsers.add_parser(
        "serve",
        aliases=["web"],
        help="serve documentation as a local website",
    )
    p_serve.add_argument(
        "--docs-dir",
        dest="docs_dir",
        help="documentation directory (default: docs)",
    )
    p_serve.add_argument(
        "--config",
        dest="config",
        help="path to codedocplus.json site config",
    )
    p_serve.add_argument(
        "--host",
        default="127.0.0.1",
        help="interface to bind (default: 127.0.0.1)",
    )
    p_serve.add_argument(
        "--port",
        type=int,
        default=8000,
        help="port to bind (default: 8000)",
    )
    p_serve.add_argument(
        "--open",
        action="store_true",
        help="open browser automatically on launch",
    )

    # preview
    p_preview = subparsers.add_parser(
        "preview",
        help="generate docs into /docs and immediately launch the web viewer",
    )
    p_preview.add_argument(
        "path",
        nargs="?",
        default=".",
        help="directory to read from (default: current directory)",
    )
    p_preview.add_argument(
        "-o",
        "--output",
        dest="out",
        default=None,
        help="output markdown file (default: docs/index.md)",
    )
    p_preview.add_argument(
        "-exd",
        "--exclude-dirs",
        dest="exc_d",
        nargs="*",
        help="directories to exclude from reading",
    )
    p_preview.add_argument(
        "-exf",
        "--exclude-files",
        dest="exc_f",
        nargs="*",
        help="files to exclude from reading",
    )
    p_preview.add_argument(
        "--config",
        dest="config",
        help="path to codedocplus.json site config",
    )
    p_preview.add_argument(
        "--host",
        default="127.0.0.1",
        help="interface to bind (default: 127.0.0.1)",
    )
    p_preview.add_argument(
        "--port",
        type=int,
        default=8000,
        help="port to bind (default: 8000)",
    )
    p_preview.add_argument(
        "--no-open",
        action="store_true",
        help="do not open browser automatically",
    )

    # init
    subparsers.add_parser(
        "init",
        help="create a starter codedocplus.json in the current directory",
    )

    # update
    subparsers.add_parser(
        "update",
        help="check for and apply the latest version",
    )

    # uninstall
    subparsers.add_parser(
        "uninstall",
        help="remove CodeDocPlus, launchers, and PATH entries",
    )

    args = parser.parse_args()

    if args.uninstall or args.command == "uninstall":
        uninstall_self()
        return

    if args.update or args.command == "update":
        await check_for_update(apply=True)
        return

    if args.command in ("build", "generate"):
        await cmd_build(args)
    elif args.command in ("serve", "web"):
        run_serve(
            docs_dir=args.docs_dir,
            config_path=args.config,
            host=args.host,
            port=args.port,
            open_browser=args.open,
        )
    elif args.command == "preview":
        await cmd_preview(args)
    elif args.command == "init":
        cmd_init()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
