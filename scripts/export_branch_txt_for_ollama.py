import argparse
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

import tiktoken
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# === SETTINGS ===
REPO_PATH = Path(".").resolve()
EXPORT_ROOT = Path("./export_docs_export")
INCLUDE_EXT = {
    ".py",
    ".ts",
    ".tsx",
    ".gitignore",
    ".md",
    ".txt",
    ".toml",
    ".json",
    ".yml",
    ".template",
    ".sh",
}
EXCLUDES = {
    ".git",
    "poetry.lock",
    ".venv",
    "node_modules",
    "__pycache__",
    "scripts",
    "export_docs_export",
}
TOKEN_MODEL = "gpt-4"

console = Console()


def assert_at_repo_root():
    if not (REPO_PATH / ".git").is_dir():
        console.print("[red]❌ Must run this script from the root of a Git repository.[/red]")
        sys.exit(1)


def is_valid_source_file(path: Path, branch_out_dir: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix not in INCLUDE_EXT:
        return False
    if any(part in EXCLUDES for part in path.parts):
        return False
    if branch_out_dir in path.parents:
        return False
    if path.name.endswith(f"__{branch_out_dir.name}.txt"):
        return False
    return True


def get_diff_files(from_branch: str, current_branch: str) -> set[str]:
    try:
        cmd = ["git", "diff", "--name-only", f"{from_branch}...{current_branch}"]
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        files = set(result.stdout.strip().splitlines())
        return {f for f in files if f.endswith(tuple(INCLUDE_EXT))}
    except subprocess.CalledProcessError as e:
        console.print("[red]❌ Failed to get diff files from Git:[/red]")
        console.print(e.stderr)
        return set()


def estimate_tokens(text: str, model: str = TOKEN_MODEL) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def export_branch_files(branch: str, diff_from: Optional[str] = None):
    console.print(f"\n[bold green]📦 Exporting branch:[/bold green] {branch}")
    out_path = EXPORT_ROOT / branch

    # Clean out previous export
    if out_path.exists():
        shutil.rmtree(out_path)
    out_path.mkdir(parents=True, exist_ok=True)

    diff_files: set[str] = set()
    if diff_from:
        diff_files = get_diff_files(diff_from, branch)
        console.print(
            f"[cyan]🔎 Detected {len(diff_files)} changed file(s) from {diff_from} to {branch}[/cyan]"
        )

    export_counts: defaultdict[str, int] = defaultdict(int)
    token_estimates: list[tuple[str, int]] = []
    token_by_ext: defaultdict[str, int] = defaultdict(int)
    total_tokens = 0
    exported = 0

    for file_path in REPO_PATH.rglob("*"):
        if not is_valid_source_file(file_path, out_path):
            continue
        if diff_from and str(file_path.relative_to(REPO_PATH)) not in diff_files:
            continue

        rel_path = file_path.relative_to(REPO_PATH)
        flat_name = str(rel_path).replace(os.sep, "__")
        out_file = out_path / f"{flat_name}__{branch}.txt"

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            export_text = f"FILE: {rel_path}\nBRANCH: {branch}\n\n{content}"
            token_est = estimate_tokens(export_text)
            total_tokens += token_est
            token_estimates.append((str(rel_path), token_est))
            token_by_ext[file_path.suffix] += token_est

            with out_file.open("w", encoding="utf-8") as f:
                f.write(f"CONTEXT: FILE: {rel_path}\n")
                f.write(f"BRANCH: {branch}\n\n")
                f.write(content)

            console.print(
                f"[green]✔ Exported:[/green] {rel_path} [dim](~{token_est:,} tokens)[/dim]"
            )
            export_counts[file_path.suffix] += 1
            exported += 1
        except Exception as e:
            console.print(f"[yellow]⚠️ Skipped:[/yellow] {rel_path} — {e}")

    if exported == 0:
        console.print("[yellow]⚠️ No files exported.[/yellow]")
        return

    table = Table(title="Export Summary", show_lines=True)
    table.add_column("Filetype", justify="center", style="cyan")
    table.add_column("Exported", justify="center", style="green")
    table.add_column("Tokens (est.)", justify="center", style="magenta")

    for ext in sorted(export_counts):
        table.add_row(ext, str(export_counts[ext]), f"{token_by_ext[ext]:,}")

    console.print(table)
    console.print(f"[bold magenta]🧠 Total estimated tokens:[/bold magenta] {total_tokens:,}")
    console.print(f"[bold green]✅ Output directory:[/bold green] {out_path.resolve()}")


def print_help():
    console.print(
        Panel.fit(
            "[bold yellow]Usage[/bold yellow]:\n"
            "  poetry run python scripts/export_branch_txt_for_ollama.py --branch <branch-name> [--diff-from <base-branch>]\n\n"
            "[bold]Examples:[/bold]\n"
            "  Export all files:\n"
            "    poetry run python scripts/export_branch_txt_for_ollama.py --branch main\n\n"
            "  Export only changed files:\n"
            "    poetry run python scripts/export_branch_txt_for_ollama.py --branch feature/login --diff-from main",
            title="🔧 Command Help",
            border_style="yellow",
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export code files to Ollama-ready format.", add_help=False
    )
    parser.add_argument("--branch", help="Name of the current Git branch")
    parser.add_argument("--diff-from", help="Base branch to diff against (optional)")
    parser.add_argument("--help", "-h", action="store_true", help="Show help and usage")

    args = parser.parse_args()

    if args.help or not args.branch:
        print_help()
        sys.exit(0)

    assert_at_repo_root()
    export_branch_files(args.branch, diff_from=args.diff_from)
