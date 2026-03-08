"""
ingest_manpages.py — One-time (or periodic) script to populate the RAG vector store.

Run this before starting the agent:
    python ingest_manpages.py

Sources (in priority order):
  1. Local .txt / .md files in knowledge_base/manpages/
  2. `man <tool>` via WSL (if available)
  3. Hardcoded fallback summaries for offline use
"""
import os
import subprocess
from rag import ingest_document

# ---------------------------------------------------------------------------
# Config: map tool name → optional extra local doc paths
# ---------------------------------------------------------------------------
TOOLS_TO_INGEST = {
    "sha256sum":  [],
    "binwalk":    [],
    "cat":        [],
    "nmap":       [],
    "john":       [],
    "volatility3": [
        r"D:\Projects\el-el-em\agent4\knowledge_base\manpages\volatility_plugins.md",
        #"knowledge_base/volatility_usage.txt",
    ],
}

MANPAGES_DIR = "knowledge_base/manpages"   # drop pre-downloaded .txt files here


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_manpage_wsl(tool: str) -> str | None:
    """Try to grab a man page via WSL. Returns plain text or None."""
    try:
        result = subprocess.run(
            ["wsl", "man", "--encoding=utf-8", tool],
            capture_output=True, text=True, timeout=10, errors="replace"
        )
        if result.returncode == 0 and result.stdout.strip():
            # Strip backspace-based bold/underline formatting (man page artefacts)
            import re
            clean = re.sub(r'.\x08', '', result.stdout)
            return clean
    except Exception:
        pass
    return None


def load_local_file(path: str) -> str | None:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return None


def load_manpages_dir(tool: str) -> str | None:
    """Check knowledge_base/manpages/<tool>.txt (or .md)."""
    for ext in (".txt", ".md"):
        path = os.path.join(MANPAGES_DIR, tool + ext)
        text = load_local_file(path)
        if text:
            return text
    return None


# ---------------------------------------------------------------------------
# Main ingestion
# ---------------------------------------------------------------------------

def main():
    print("=== Ingesting tool documentation into RAG store ===\n")
    os.makedirs(MANPAGES_DIR, exist_ok=True)

    for tool, extra_paths in TOOLS_TO_INGEST.items():
        print(f"► {tool}")
        combined = ""

        # 1. Pre-downloaded man page in knowledge_base/manpages/
        local_man = load_manpages_dir(tool)
        if local_man:
            print(f"  • Loaded from {MANPAGES_DIR}/{tool}.txt")
            combined += local_man + "\n\n"

        # 2. Live WSL man page
        if not combined:
            wsl_man = fetch_manpage_wsl(tool)
            if wsl_man:
                print(f"  • Fetched via WSL man")
                combined += wsl_man + "\n\n"
                # Cache it for next time
                cache_path = os.path.join(MANPAGES_DIR, tool + ".txt")
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(wsl_man)

        # 3. Extra knowledge-base files (e.g. existing volatility docs)
        for path in extra_paths:
            text = load_local_file(path)
            if text:
                print(f"  • Loaded extra: {path}")
                combined += text + "\n\n"

        if combined.strip():
            ingest_document(doc_id=tool, text=combined, metadata={"tool": tool})
        else:
            print(f"  ⚠ No documentation found for '{tool}' — skipping")

    print("\n✅ Ingestion complete.")


if __name__ == "__main__":
    main()
