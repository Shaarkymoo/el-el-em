"""
tools.py — Tool registry for the forensics agent.

Register a new tool by decorating a function with @register_tool("name").
Each function receives positional string arguments as the LLM passes them.
"""

import subprocess
from typing import Callable

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_TOOLS: dict[str, Callable] = {}


def register_tool(name: str):
    """Decorator: register a function under a tool name."""
    def decorator(fn: Callable) -> Callable:
        _TOOLS[name] = fn
        return fn
    return decorator


def get_tool(name: str) -> Callable | None:
    return _TOOLS.get(name)


def list_tools() -> list[str]:
    return list(_TOOLS.keys())


def run_tool(name: str, args: list[str]) -> str:
    """Dispatch a tool call and return its string output."""
    tool = get_tool(name)
    if tool is None:
        return f"⚠️ Unknown tool: '{name}'. Available tools: {list_tools()}"
    try:
        return tool(*args)
    except TypeError as e:
        return f"⚠️ Bad arguments for '{name}': {e}"
    except Exception as e:
        return f"⚠️ Tool '{name}' raised an error: {e}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wsl_run(cmd: list[str]) -> str:
    result = subprocess.run(["wsl"] + cmd, capture_output=True, text=True)
    return (result.stdout + result.stderr).strip()


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

@register_tool("sha256sum")
def hash_file(filepath: str, *args: str) -> str:
    """Compute SHA-256 hash of a file."""
    return _wsl_run(["sha256sum", *args, filepath])


@register_tool("binwalk")
def run_binwalk(filepath: str, *args: str) -> str:
    """Analyse a binary file with binwalk."""
    return _wsl_run(["binwalk", *args, filepath])


@register_tool("cat")
def cat(filepath: str, *args: str) -> str:
    """Print file contents."""
    return _wsl_run(["cat", *args, filepath])


@register_tool("john")
def john_the_ripper(filepath: str, *args: str) -> str:
    """Run John the Ripper on a hash file."""
    return _wsl_run(["john", *args, filepath])


@register_tool("nmap")
def nmap_wrapper(target: str, *options: str) -> str:
    """Run an nmap scan. Requires nmap_driver.py."""
    from nmap_driver import nmap_scan  # local dependency
    options_str = " ".join(options) if options else None
    cmd, output = nmap_scan(target, options=options_str, use_wsl=True)
    return f"Command run: {' '.join(cmd)}\n\n{output}"


@register_tool("volatility3")
def volatility_wrapper(memory_file: str, *options: str) -> str:
    """Run a Volatility 3 plugin against a memory image. Requires volat_driver.py."""
    from volat_driver import volatility_scan  # local dependency
    options_str = " ".join(options) if options else None
    cmd, output = volatility_scan(options=options_str)
    return f"Command run: {' '.join(cmd)}\n\n{output}"
