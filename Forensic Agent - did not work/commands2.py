import subprocess
from pathlib import Path
from typing import List, Optional
from nmap_driver import nmap_scan

BASE_DIR = Path(__file__).resolve().parent

TOOLS_DIR = BASE_DIR / "Tools"
VOLATILITY_DIR = TOOLS_DIR / "volatility"
VOLATILITY_VENV = VOLATILITY_DIR / "venv"
VOLATILITY_PYTHON = VOLATILITY_VENV / "Scripts" / "python.exe"

##########################################################

def run_command(cmd: List[str]) -> str:
    """
    Run a subprocess command safely and return combined output.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return (result.stdout + result.stderr).strip()
    except FileNotFoundError:
        return f"❌ Command not found: {cmd[0]}"
    except Exception as e:
        return f"❌ Execution error: {str(e)}"

###########################################################

def hash_file(*command: str) -> str:
    """
    Compute SHA256 hash.
    Expects command to be a list of arguments exactly as passed to sha256sum.
    Example:
        ["file.txt"]
        ["-b", "file.txt"]
    """
    cmd = ["wsl", "sha256sum", command]
    result = run_command(cmd)
    return result.strip()
#can you tell me the sha256 hash of this file "/mnt/c/Users/Shaarav/Desktop/Test.txt"   

def run_binwalk(filepath: str, *args: str) -> str:
    """
    Run binwalk against a file.
    """
    cmd = ["binwalk", *args, filepath]
    return run_command(cmd)
#can you run binwalk on this file "/mnt/c/Users/Shaarav/Desktop/Test.txt"   

def cat(filepath: str, *args: str) -> str:
    """
    Read file contents.
    """
    cmd = ["cat", *args, filepath]
    return run_command(cmd)
#can you read this file "/mnt/c/Users/Shaarav/Desktop/Test.txt"

def run_volatility3(memory_file: str, plugin: str) -> str:
    """
    Execute Volatility 3 from the repo-local virtual environment.
    """
    if not VOLATILITY_PYTHON.exists():
        return "❌ Volatility Python environment not found."

    cmd = [
        str(VOLATILITY_PYTHON),
        "-m", "volatility3",
        "-f", memory_file,
        plugin
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return (result.stdout + result.stderr).strip()

#can you tell me the PPID of the malicious process "powershell.exe" in this memory dump "/mnt/c/Users/Shaarav/Desktop/memdump.raw"

def nmap_wrapper(target: str, *options: str) -> str:
    """
    Wrapper around nmap_driver to maintain consistent output.
    """
    options_str = " ".join(options) if options else None
    cmd, output = nmap_scan(
        target,
        options=options_str,
        use_wsl=False  # native preferred
    )
    return f"Command run: {' '.join(cmd)}\n\n{output}"

#can you run nmap on this target "scanme.nmap.org" with options "syn scan, ports:22,80"
#Can you run nmap on this target "scanme.nmap.org" with options "connect scan, ports 1-200, moderate speed"
#Can you run nmap on this target "scanme.nmap.org" with options "connect scan, top 100 ports, moderate speed"
#Can you run nmap on this target "scanme.nmap.org" with options "connect scan, port 80"

# def johnTheRipper(filepath: str, *args: str) -> str:
#     cmd = ["wsl", "john"] + list(args) + [filepath]
#     result = subprocess.run(cmd, capture_output=True, text=True)
#     return (result.stdout + result.stderr).strip()


##https://github.com/CyberAlbSecOP/Awesome_GPT_Super_Prompting/tree/main

# https://github.com/yueliu1999/Awesome-Jailbreak-on-LLMs

# https://github.com/Techiral/awesome-llm-jailbreaks

# https://github.com/tuxsharxsec/Jailbreaks

# https://github.com/BirdsAreFlyingCameras/GPT-5_Jailbreak_PoC

# nmap, 