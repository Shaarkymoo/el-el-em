import subprocess
import shlex
import re
from typing import List, Union, Tuple, Optional, Dict
from pathlib import Path

testfile1 = r"D:/college/capstone/mem images/192-Reveal.dmp"
testfile2 = r"D:/college/capstone/mem images/162-Ramnit.dmp"

# ==========================
# Validation
# ==========================

_SAFE_PATH_RE = re.compile(r"^.+$")

def _validate_memory_file(path: str) -> Path:
    if not isinstance(path, str) or not path:
        raise ValueError("memory_file must be a non-empty string")
    if not _SAFE_PATH_RE.match(path):
        raise ValueError(f"memory_file contains unsafe characters: {path!r}")
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Memory file does not exist: {path}")
    return p

# ==========================
# Description → Plugin Map
# ==========================

# Canonical Windows Volatility 3 plugins
_DESCRIPTION_TO_PLUGIN: Dict[str, str] = {
    # process related
    "list processes": "windows.pslist",
    "process list": "windows.pslist",
    "running processes": "windows.pslist",
    "process tree": "windows.pstree",
    "ppid": "windows.pstree",
    "parent process": "windows.pstree",
    "process command line": "windows.cmdline",
    "cmdline": "windows.cmdline",

    # suspicious / malware triage
    "malicious processes": "windows.malfind",
    "injected code": "windows.malfind",
    "dll list": "windows.dlllist",
    "loaded dlls": "windows.dlllist",
    "handles": "windows.handles",

    # system info
    "system info": "windows.info",
    "os info": "windows.info",
    "registry hives": "windows.registry.hivelist",
    "hivelist": "windows.registry.hivelist",

    # networking
    "network connections": "windows.netscan",
    "open ports": "windows.netscan",
    "sockets": "windows.netscan",

    # credentials
    "lsa secrets": "windows.lsadump",
    "credentials": "windows.hashdump",
    "password hashes": "windows.hashdump",
}

# ==========================
# Helper: parse plugin token
# ==========================

def _parse_plugin_token(token: str) -> str:
    """
    Accept:
    - exact plugin name: windows.pslist
    - descriptive phrase: "list processes"
    - fuzzy match on known descriptions
    """
    token = token.strip()
    if not token:
        raise ValueError("Empty plugin token")

    # If user already provided a proper plugin name
    if token.startswith("windows."):
        return token

    lower = token.lower()

    # Exact description match
    if lower in _DESCRIPTION_TO_PLUGIN:
        return _DESCRIPTION_TO_PLUGIN[lower]

    # Fuzzy contains match
    for key, plugin in _DESCRIPTION_TO_PLUGIN.items():
        if key in lower:
            return plugin

    raise ValueError(f"Unknown or unsupported Volatility plugin description: {token!r}")

# ==========================
# Main Volatility Runner
# ==========================

def volatility_scan(
    options: Optional[Union[str, List[str]]] = None,
    #volatility_path: str = r"./mnt/d/Projects/el-el-em/Volatility/venv/Scripts/vol.exe",
    volatility_path: str = r"D:/Projects/el-el-em/Volatility/venv/Scripts/vol.exe",
    use_wsl: bool = False,
) -> Tuple[List[str], str]:
    """
    Run a Volatility 3 plugin against a memory image.

    Parameters:
    - memory_file: path to memory dump
    - plugin: plugin name or descriptive phrase (e.g. "process tree")
    - options: optional flags (e.g. "--pid 1234")
    - volatility_path: path to vol.py
    - use_wsl: run via WSL if True
    - timeout: optional execution timeout

    Returns:
    (command_list, stdout+stderr)
    """

    # Build command
    cmd: List[str] = []
    if use_wsl:
        cmd.append("wsl")

    cmd.extend([volatility_path,"-f"])

    # Parse options
    if options:
        if isinstance(options, str):
            opt_tokens = shlex.split(options)
        elif isinstance(options, list):
            opt_tokens = [str(o) for o in options]
        else:
            raise ValueError("options must be a string or list of strings")

        cmd.extend(opt_tokens)

    # Execute
    try: 
        proc = subprocess.run(cmd, capture_output=True, text=True)
        combined = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
    except FileNotFoundError as e:
        raise RuntimeError(f"Volatility not found at {volatility_path}. Error: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to run Volatility: {e}")

    return cmd, combined

# ==========================
# Example usage
# ==========================

if __name__ == "__main__":
    # List processes
    #print(volatility_scan("mem.raw", "list processes", use_wsl=True))

    # Process tree (PPID analysis)
    #print(volatility_scan("mem.raw", "process tree", use_wsl=True))

    # Malfind with PID
    print(volatility_scan(
        options="windows.pslist",
        use_wsl=False
    ))
