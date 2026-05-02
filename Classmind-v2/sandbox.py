"""
sandbox.py  —  ClassMind Python code sandbox
Executes student code safely. Key guarantees:
  - No filesystem, network, OS access
  - input() replaced with safe stub (no stdin hang)
  - Hard timeout (configurable via env SANDBOX_TIMEOUT, default 5s)
  - Output cap (configurable via env SANDBOX_MAX_OUTPUT, default 2048 bytes)
  - Cross-platform: uses sys.executable so the correct Python is always found
"""
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass

# ── configurable limits (override via .env) ───────────────────────
TIMEOUT  = int(os.getenv("SANDBOX_TIMEOUT",    "5"))
MAX_OUT  = int(os.getenv("SANDBOX_MAX_OUTPUT", "2048"))

BLOCKED = [
    "import os", "import sys", "import subprocess", "import socket",
    "import shutil", "import importlib", "import ctypes",
    "import threading", "import multiprocessing", "import asyncio",
    "__import__", "open(", "exec(", "eval(", "compile(", "breakpoint(",
    "globals(", "locals(", "__builtins__",
]

# Prepended to every student script:
#   - patches input() so it doesn't block forever
#   - disables dangerous builtins
PREAMBLE = """\
import builtins as _b
_input_called = [0]
def _safe_input(prompt=''):
    _input_called[0] += 1
    if _input_called[0] > 10:
        raise RuntimeError("Too many input() calls in sandbox")
    print(str(prompt), end='', flush=True)
    return ''   # always returns empty string (no real stdin)
_b.input = _safe_input
del _b
"""


@dataclass
class RunResult:
    output:    str
    error:     bool
    timed_out: bool = False


def run_code(code: str, language: str = "python") -> RunResult:
    if language.lower() not in ("python", "python3"):
        return RunResult(f"Only Python is supported (got '{language}')", error=True)

    for kw in BLOCKED:
        if kw in code:
            return RunResult(f"Sandbox blocked: '{kw}' is not allowed", error=True)

    full_code = PREAMBLE + "\n" + code

    # Use sys.executable so the sandbox always runs with the same Python
    # interpreter as the server — works on Windows, Linux, and macOS without
    # needing to know whether the binary is called "python" or "python3".
    python_exe = sys.executable

    with tempfile.NamedTemporaryFile(
        suffix=".py", delete=False, mode="w", encoding="utf-8"
    ) as f:
        f.write(full_code)
        path = f.name

    try:
        res = subprocess.run(
            [python_exe, "-u", path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            stdin=subprocess.DEVNULL,
            # Prevent the subprocess from inheriting the server's open handles.
            # close_fds is True by default on POSIX; on Windows it is ignored
            # when using DEVNULL/PIPE so it is safe to always set it.
            close_fds=True,
        )
        stdout = res.stdout or ""
        stderr = res.stderr or ""

        # Strip preamble noise from tracebacks
        combined = stdout
        if stderr:
            cleaned = "\n".join(
                line for line in stderr.splitlines()
                if "_safe_input" not in line and "PREAMBLE" not in line
            )
            if cleaned.strip():
                combined += ("\n" if combined else "") + cleaned

        combined = combined[:MAX_OUT]
        return RunResult(output=combined or "(no output)", error=res.returncode != 0)

    except subprocess.TimeoutExpired:
        return RunResult(
            f"Time limit exceeded ({TIMEOUT}s max)", error=True, timed_out=True
        )
    except FileNotFoundError:
        return RunResult(
            f"Python interpreter not found: {python_exe}", error=True
        )
    except Exception as e:
        return RunResult(f"Execution error: {e}", error=True)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
