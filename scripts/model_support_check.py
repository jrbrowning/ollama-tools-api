# File: scripts/model_support_check.py
import json
import os
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.markup import escape as rich_escape
from rich.panel import Panel
from rich.table import Table

ENV_PATH = ".env"
MODEL_KEYS = [
    "LOCAL_GPU",
    "TRADITIONAL_MODEL",
    "TRADITIONAL_MODEL_ALT",
    "REASONING_MODEL",
    "REASONING_MODEL_ALT",
]

RE_SIZE = re.compile(r":\s*([0-9]+(?:\.[0-9]+)?)\s*b\b", re.IGNORECASE)
BYTES_IN_GIB = 1024**3
BYTES_IN_GB = 1000**3

DEFAULT_TIMEOUT_SEC = 5
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")

console = Console()


def die(msg: str, code: int = 1) -> None:
    console.print(f"[bold red]ERROR:[/bold red] {msg}")
    sys.exit(code)


def _sanitize_for_rich(s: str) -> str:
    # Strip control chars, then escape Rich markup
    return rich_escape(CONTROL_CHARS_RE.sub("", s))


def _run(cmd: List[str], timeout: int = DEFAULT_TIMEOUT_SEC) -> str:
    # Shell disabled; enforce timeouts to avoid hangs
    return subprocess.check_output(cmd, text=True, timeout=timeout)


def ensure_macos() -> None:
    try:
        out = _run(["uname", "-s"]).strip()
        if out != "Darwin":
            die("This checker is macOS-only (Darwin required).")
    except Exception as e:
        die(f"Failed to determine OS: {e}")


def read_env(path: str) -> Dict[str, str]:
    if not os.path.isfile(path):
        die(f"Missing {path}. Run from repo root.")

    data: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def sysctl_int(name: str) -> int:
    try:
        out = _run(["/usr/sbin/sysctl", "-n", name]).strip()
        return int(float(out))
    except Exception as e:
        die(f"sysctl {name} failed: {e}")
        return 0  # Unreachable; keeps type-checkers happy


def get_host_resources() -> Tuple[int, int, int]:
    mem_bytes = sysctl_int("hw.memsize")
    # Use GiB for consistency with Docker Desktop reporting
    mem_gib = int(round(mem_bytes / BYTES_IN_GIB))
    physical = sysctl_int("hw.physicalcpu")
    logical = sysctl_int("hw.logicalcpu")
    return mem_gib, physical, logical


def parse_param_b(model_spec: str) -> Optional[float]:
    m = RE_SIZE.search(model_spec)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def required_ram_gib(param_b: float) -> float:
    # Need = 0.7 × params[billions], in GiB
    return 0.7 * param_b


def docker_running() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        _run(["docker", "info"])
        return True
    except Exception:
        return False


def get_docker_resources() -> Optional[Tuple[int, int]]:
    """
    Returns (docker_mem_gib, docker_cpus) using structured `docker info`.
    If Docker is not running or fields are missing, returns None.
    """
    if not docker_running():
        return None
    try:
        raw = _run(["docker", "info", "--format", "{{json .}}"])
        info = json.loads(raw)
        mem_bytes = info.get("MemTotal")
        cpus = info.get("NCPU")
        if not isinstance(mem_bytes, int) or not isinstance(cpus, int):
            return None
        mem_gib = int(round(mem_bytes / BYTES_IN_GIB))
        return mem_gib, cpus
    except Exception:
        return None


def main() -> None:
    ensure_macos()
    env = read_env(ENV_PATH)

    host_mem_gib, host_phys, host_logical = get_host_resources()
    docker_res = get_docker_resources()

    # === System Panels ===
    console.print(
        Panel.fit(
            f"[bold cyan]RAM:[/bold cyan] [yellow]{host_mem_gib} GiB[/yellow]\n"
            f"[bold cyan]CPU (physical):[/bold cyan] {host_phys}\n"
            f"[bold cyan]CPU (logical):[/bold cyan] {host_logical}",
            title="Host Info (macOS)",
            border_style="cyan",
        )
    )

    if docker_res is not None:
        docker_mem_gib, docker_cpus = docker_res
        console.print(
            Panel.fit(
                f"[bold cyan]RAM available to Docker:[/bold cyan] [yellow]{docker_mem_gib} GiB[/yellow]\n"
                f"[bold cyan]CPUs available to Docker:[/bold cyan] {docker_cpus}",
                title="Docker Info (active context)",
                border_style="cyan",
            )
        )
    else:
        console.print(
            Panel.fit(
                "[yellow]Docker Desktop/daemon not detected, not running, or missing fields.[/yellow]\n"
                "Start Docker Desktop, then re-run this script to include Docker limits.",
                title="Docker Info",
                border_style="yellow",
            )
        )

    # === Table ===
    has_docker = docker_res is not None
    table_title = "Model Support Check (Need = 0.7 × params[b], shown in GiB)"
    table = Table(title=table_title)
    table.add_column("VAR", style="bold")
    table.add_column("MODEL")
    table.add_column("NEED (GiB)", justify="right")
    table.add_column("HOST HAVE (GiB)", justify="right")
    table.add_column("HOST STATUS", style="bold")
    if has_docker:
        table.add_column("DOCKER HAVE (GiB)", justify="right")
        table.add_column("DOCKER STATUS", style="bold")

    host_supported: List[str] = []
    docker_supported: List[str] = []

    for key in MODEL_KEYS:
        spec = env.get(key, "")
        safe_spec = _sanitize_for_rich(spec) if spec else _sanitize_for_rich("(missing)")

        if not spec:
            if has_docker:
                docker_mem_gib, _ = docker_res  # type: ignore[misc]
                table.add_row(
                    key,
                    safe_spec,
                    "N/A",
                    str(host_mem_gib),
                    "[red]UNKNOWN[/red]",
                    str(docker_mem_gib),
                    "[red]UNKNOWN[/red]",
                )
            else:
                table.add_row(key, safe_spec, "N/A", str(host_mem_gib), "[red]UNKNOWN[/red]")
            continue

        param_b = parse_param_b(spec)
        if param_b is None:
            if has_docker:
                docker_mem_gib, _ = docker_res  # type: ignore[misc]
                table.add_row(
                    key,
                    safe_spec,
                    "N/A",
                    str(host_mem_gib),
                    "[red]UNKNOWN[/red]",
                    str(docker_mem_gib),
                    "[red]UNKNOWN[/red]",
                )
            else:
                table.add_row(key, safe_spec, "N/A", str(host_mem_gib), "[red]UNKNOWN[/red]")
            continue

        need = round(required_ram_gib(param_b), 1)

        # Host status
        host_status_supported = host_mem_gib >= need
        host_status = (
            "[green]SUPPORTED[/green]" if host_status_supported else "[red]NOT SUPPORTED[/red]"
        )
        if host_status_supported:
            host_supported.append(spec)

        if has_docker:
            docker_mem_gib, _docker_cpus = docker_res  # type: ignore[misc]
            docker_status_supported = docker_mem_gib >= need
            docker_status = (
                "[green]SUPPORTED[/green]"
                if docker_status_supported
                else "[red]NOT SUPPORTED[/red]"
            )
            if docker_status_supported:
                docker_supported.append(spec)
            table.add_row(
                key,
                safe_spec,
                f"{need:.1f}",
                str(host_mem_gib),
                host_status,
                str(docker_mem_gib),
                docker_status,
            )
        else:
            table.add_row(key, safe_spec, f"{need:.1f}", str(host_mem_gib), host_status)

    console.print(table)

    # === Conclusions ===
    # Host conclusion
    if host_supported:
        console.print(
            Panel(
                "[bold green]Based on your system (Host), you can use the following models:[/bold green]\n"
                + "\n".join(f"• {_sanitize_for_rich(m)}" for m in host_supported[:5]),
                title="Conclusion — Host",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                "[bold red]No listed models are supported on the Host based on current RAM.[/bold red]",
                title="Conclusion — Host",
                border_style="red",
            )
        )

    # Docker conclusion
    if has_docker:
        if docker_supported:
            console.print(
                Panel(
                    "[bold green]Based on your Docker limits, you can use the following models:[/bold green]\n"
                    + "\n".join(f"• {_sanitize_for_rich(m)}" for m in docker_supported[:5]),
                    title="Conclusion — Docker",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    "[bold red]No listed models are supported under current Docker RAM limits.[/bold red]\n"
                    "Increase Docker Desktop → Settings → Resources → Memory.",
                    title="Conclusion — Docker",
                    border_style="red",
                )
            )

    # === Notes / Diagnostics ===
    console.print(
        Panel.fit(
            "NEED is computed strictly from the ':<size>b' tag after the model name.\n"
            "If a model lacks that tag, status is UNKNOWN.\n"
            "Docker metrics are taken from the active context via 'docker info --format {{json .}}'.\n"
            f"All subprocess calls use a {DEFAULT_TIMEOUT_SEC}s timeout to avoid hangs.",
            title="Notes",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    main()
