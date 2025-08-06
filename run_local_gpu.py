#!/usr/bin/env python3
import os
import platform
import shutil
import subprocess
import sys
import time

from pydantic import BaseModel

CONFIG_PATH = ".env"
PID_FILE = "local_gpu/ollama.pid"
LOG_FILE = "local_gpu/ollama.log"


class Config(BaseModel):
    LOCAL_GPU: str
    ENABLE_LOCAL_GPU_MODEL: bool


def load_config() -> Config:
    if not os.path.isfile(CONFIG_PATH):
        log(f"❌ Missing config at {CONFIG_PATH}")
        sys.exit(1)

    config_data: dict[str, str] = {}
    with open(CONFIG_PATH) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                config_data[k] = v.lower() if v.lower() in ["true", "false"] else v

    try:
        return Config(
            LOCAL_GPU=config_data["LOCAL_GPU"],
            ENABLE_LOCAL_GPU_MODEL=config_data["ENABLE_LOCAL_GPU_MODEL"]
            == "true",  # This is coersion to boolean.   if not "true", default is false.
        )
    except KeyError as e:
        log(f"❌ Missing required config variable: {e}")
        sys.exit(1)


def log(message: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def check_ollama_installed():
    if shutil.which("ollama") is None:
        log("❌ Ollama is not installed.")
        log("➡️  Please install the latest version from https://ollama.com/download")
        sys.exit(1)


def get_total_memory_gb():
    system = platform.system()
    if system == "Linux":
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    return int(line.split()[1]) // 1024 // 1024
    elif system == "Darwin":
        mem_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
        return mem_bytes // (1024 * 1024 * 1024)
    else:
        log(f"❌ Unsupported OS: {system}")
        sys.exit(1)


def get_required_mem(model: str) -> int:
    return {
        "llama3": 8,
        "deepseek-r1": 16,
        "gemma": 4,
    }.get(model, 0)


def list_models():
    check_ollama_installed()
    log("📋 Listing available Ollama models...")
    total_mem = get_total_memory_gb() or 0
    log(f"🧠 System Memory: {total_mem} GB")

    output = subprocess.check_output(["ollama", "list"], text=True)
    print(f"\n{'Model Name':<25} ")
    print(f"{'-'*25} ")
    for line in output.strip().splitlines():
        model = line.split()[0]
        base_model = model.split(":")[0]
        required = get_required_mem(base_model)
        note = f"* Requires {required}GB RAM" if required > total_mem else ""
        print(f"{model:<25} {note}")
    print(f"{'-'*25} ")


def start_ollama():
    log("ℹ️ Ollama currently listens on port only 11434... listening!")
    env = os.environ.copy()
    env["OLLAMA_HOST"] = "0.0.0.0"
    with open(LOG_FILE, "a") as logf:
        proc = subprocess.Popen(["ollama", "serve"], stdout=logf, stderr=logf, env=env)
        with open(PID_FILE, "w") as pidf:
            pidf.write(str(proc.pid))


def wait_for_ready():
    log("⏳ Waiting for Ollama to be ready on :11434...")
    import requests

    for _ in range(10):
        try:
            res = requests.get("http://localhost:11434", timeout=1)
            if "Ollama is running" in res.text:
                log("✅ Ollama is ready on :11434")
                return
        except Exception:
            pass
        time.sleep(1)
    log("❌ Ollama did not start on :11434 in time.")
    sys.exit(1)


def pull_or_verify_model(model: str, online: bool):
    if online:
        log(f"📥 Pulling model: {model}")
        try:
            subprocess.check_call(["ollama", "pull", model])
            log("✅ Model pulled.")
        except subprocess.CalledProcessError:
            log(f"❌ Failed to pull model: {model}")
            sys.exit(1)
    else:
        log(f"📴 OFFLINE MODE: Verifying {model} is locally available...")
        output = subprocess.check_output(["ollama", "list"], text=True)
        if model not in output:
            log(f"❌ Model {model} not found in offline mode.")
            sys.exit(1)
        log(f"✅ Model {model} is cached.")


def up():
    config = load_config()
    check_ollama_installed()
    start_ollama()
    wait_for_ready()
    pull_or_verify_model(config.LOCAL_GPU, config.ENABLE_LOCAL_GPU_MODEL)
    log(f"🏁 Local GPU model '{config.LOCAL_GPU}' ready at http://localhost:11434")


def stop():
    if os.path.isfile(PID_FILE):
        log("🛑 Stopping Ollama process...")
        try:
            with open(PID_FILE) as pidf:
                pid = int(pidf.read().strip())
            os.kill(pid, 15)
        except Exception:
            log("⚠️ Could not kill Ollama process (may already be stopped).")
        os.remove(PID_FILE)
        log("✅ Ollama process stopped.")
    else:
        log("⚠️ No PID file found. Ollama may not be running.")


def print_help():
    print("""
run_local_gpu.py — Start or stop a local GPU Ollama instance

Usage:
  python run_local_gpu.py up      Start Ollama on the GPU with model from local_gpu/config.env
  python run_local_gpu.py stop    Stop Ollama process only (keep install and model)
  python run_local_gpu.py list    List local models and memory requirements
  python run_local_gpu.py help    Show this help message

Config file:
  Expected at: .env

Required variables in config.env:
  LOCAL_GPU=<ollama_model_name>    e.g. llama3, deepseek-r1:8b
  ENABLE_LOCAL_GPU_MODEL=true|false

NOTE: Ollama always binds to port 11434.
""")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    {"up": up, "stop": stop, "list": list_models, "help": print_help}.get(
        cmd, print_help
    )()
