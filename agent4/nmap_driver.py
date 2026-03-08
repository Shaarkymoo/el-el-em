import subprocess
import shlex
import re
from typing import List, Union, Tuple, Optional, Dict
from pathlib import Path

# ---------- Helper: safe target validation ----------
# Allow typical hostnames, IPv4, IPv6, CIDR, and port-spec suffixes like: 192.168.1.1, example.com, 10.0.0.0/24, [2001:db8::1], host:80
_SAFE_TARGET_RE = re.compile(r'^[A-Za-z0-9\.\-\:\/\[\],]+$')

def _validate_target(target: str) -> None:
    if not isinstance(target, str) or not target:
        raise ValueError("target must be a non-empty string")
    if not _SAFE_TARGET_RE.match(target):
        raise ValueError(f"target contains unsafe characters: {target!r}")

# ---------- Mapping descriptions -> flags ----------
# Add or edit synonyms here as you need.
_DESCRIPTION_TO_FLAG: Dict[str, Union[str, List[str]]] = {
    # scans
    "syn scan": "-sS",
    "stealth": "-sS",
    "tcp connect": "-sT",
    "connect": "-sT",
    "udp scan": "-sU",
    "icmp ping": "-PE",
    "no ping": "-Pn",  # skip host discovery
    "skip host discovery": "-Pn",
    "os detection": "-O",
    "version detection": "-sV",
    "service version": "-sV",
    "aggressive": "-A",      # OS detection + version + script + traceroute
    "fast": "-T4",           # faster timing template
    "slow": "-T2",
    "very slow": "-T1",
    "very fast": "-T5",

    # ports / port selection are handled specially, but include descriptive keys
    "top ports": "--top-ports",  # requires a number
    "ports": "-p",               # requires ports spec

    # output
    "output xml": "-oX",         # requires filename
    "output all": "-oA",         # requires basename
    "output grepable": "-oG",    # requires filename
    "output normal": "-oN",      # requires filename

    # scripts
    "script": "--script",        # requires script name(s)
    "vuln": "--script vuln",

    # extra features
    "traceroute": "--traceroute",
    "verbose": "-v",
    "very verbose": "-vv",
}

# ---------- Parser for description-like options ----------
def _parse_option_token(tok: str) -> List[str]:
    """
    Convert a single user-provided token (which can be a raw flag or a description)
    into one or several command-line tokens.
    """
    tok = tok.strip()
    if not tok:
        return []

    # If user provided a proper flag already, return as-is (respect quoting)
    if tok.startswith('-'):
        # split safetly using shlex
        parts = shlex.split(tok)
        return parts

    # Accept forms like "ports:22,80", "ports 22-80", "top ports 100"
    lower = tok.lower()

    # special handling for 'ports' or 'top ports'
    m = re.match(r'^(top[\s-]*ports?)\s*[:=]?\s*(\d+)$', lower)
    if m:
        return [f"--top-ports", m.group(2)]

    m = re.match(r'^(ports?)\s*[:=]?\s*(.+)$', lower)
    if m:
        ports = m.group(2).strip()
        # ensure ports string is not weird
        # allow digits, commas, hyphens, and ranges
        if not re.match(r'^[0-9,\-\s]+$', ports):
            raise ValueError(f"Invalid ports spec: {ports!r}")
        return ["-p", ports.replace(" ", "")]

    # scripts, e.g. "script vuln" or "script: auth"
    m = re.match(r'^(script|scripts?)\s*[:=]?\s*(.+)$', lower)
    if m:
        script_arg = m.group(2).strip()
        return ["--script", script_arg]

    # top-ports with number in plain language: "top ports 100"
    m = re.match(r'^top[\s-]*ports?\s+(\d+)$', lower)
    if m:
        return ["--top-ports", m.group(1)]

    # If exact mapping exists in dictionary, use it (and return as list)
    for key, val in _DESCRIPTION_TO_FLAG.items():
        if lower == key:
            if isinstance(val, list):
                return val[:]
            return [val]

    # try some fuzzy matches: if token contains a known keyword, map it
    for key, val in _DESCRIPTION_TO_FLAG.items():
        if key in lower:
            if isinstance(val, list):
                return val[:]
            return [val]

    # fallback: treat token as raw flag(s) split by spaces
    return shlex.split(tok)

# ---------- Main function ----------
def nmap_scan(
    target: str,
    options: Optional[Union[str, List[str]]] = None,
    use_wsl: bool = True,
    timeout: Optional[int] = None,
    model_output_hint: Optional[str] = None,
) -> Tuple[List[str], str]:
    """
    Run an nmap scan on `target`.

    - target: hostname/IP/CIDR (validated for safety).
    - options: either a single string (e.g. "syn scan, ports: 22,80, verbose")
               or a list of strings like ["-sS", "-p", "22,80", "--script", "vuln"].
               Descriptions like "syn scan", "ports 22-80", "vuln", "fast" are supported.
    - use_wsl: if True, run via `wsl nmap ...` (for Windows + WSL setups). Set False to run natively.
    - timeout: optional timeout in seconds for the entire command.
    - model_output_hint: optional text you might want to append to the LLM followup (not used inside function).
    Returns (command_list, stdout_and_stderr).
    """

    _validate_target(target)

    cmd: List[str] = []
    if use_wsl:
        cmd.append("wsl")
    cmd.append("nmap")

    # base: run a basic nmap by default (no aggressive flags)
    # We won't add default flags here — let user specify if needed.
    tokens: List[str] = []

    # Normalize options into list of tokens
    if options is None:
        normalized_opts: List[str] = []
    elif isinstance(options, str):
        # attempt split by common separators (comma, semicolon) while preserving quoted pieces
        # we accept both "syn scan, ports:22,80" and "syn scan; ports 22-80"
        # Use simple heuristic splitting by comma or semicolon if they exist.
        if ',' in options or ';' in options:
            # split by commas/semicolons
            raw_tokens = [t.strip() for t in re.split(r'[;,]+', options) if t.strip()]
        else:
            # if no commas, split on " and " or just whitespace groups—prefer preserving expressions like "ports 22-80"
            # try splitting on " and " / " + " or "|" as separators first
            raw_tokens = re.split(r'\s+(?:and|AND|\+|\|)\s+|\s{2,}', options)
            raw_tokens = [t.strip() for t in raw_tokens if t.strip()]
            # if still single chunk, break into words but rejoin recognized multi-word phrases by checking mapping later
            if len(raw_tokens) == 1:
                # try splitting on runs of two+ spaces, otherwise keep as single token
                raw_tokens = [options.strip()]
        normalized_opts = raw_tokens
    elif isinstance(options, list):
        normalized_opts = [str(x).strip() for x in options if str(x).strip()]
    else:
        raise ValueError("options must be None, a string, or a list of strings")

    # Convert each normalized option into CLI tokens
    for token in normalized_opts:
        try:
            parts = _parse_option_token(token)
        except ValueError as e:
            raise ValueError(f"Failed to parse option {token!r}: {e}") from e
        tokens.extend(parts)

    # If tokens include inline flags like "-p" followed by a comma-separated string,
    # keep them as separate list elements (subprocess will handle it)
    cmd.extend(tokens)
    cmd.append(target)

    # Execute
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        combined = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
    except subprocess.TimeoutExpired as e:
        combined = f"Command timed out after {timeout} seconds. Partial output:\n{e.stdout}\n{e.stderr}"
    except FileNotFoundError as e:
        raise RuntimeError(f"nmap not found. If you're on Windows with WSL, ensure `wsl nmap` is available. Error: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to run nmap: {e}")

    return cmd, combined

# ---------- Example usages ----------
if __name__ == "__main__":
    # Basic scan
    print(nmap_scan("scanme.nmap.org", options=None, use_wsl=False))

    # Descriptive options
    print(nmap_scan("scanme.nmap.org", options="syn scan, ports: 22,80, verbose", use_wsl=False))

    # Mixing raw flags and descriptions / scripts
    print(nmap_scan("192.168.1.0/24", options=["-sV", "ports 1-1024", "--script", "vuln"], use_wsl=False))
