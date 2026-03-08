import json
import ollama
from pathlib import Path
from commands2 import *

# =========================
# Paths & Configuration
# =========================

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
OLLAMA_MODEL = "llama3.1:8b"

# =========================
# Load Knowledge Base
# =========================

def load_reference_texts():
    files = ["knowledge_base.md"]
    contents = []
    for f in files:
        try:
            with open(KNOWLEDGE_BASE_DIR / f, "r", encoding="utf-8") as fh:
                contents.append(f"\n===== {f} =====\n{fh.read()}")
        except FileNotFoundError:
            contents.append(f"\n===== {f} =====\n[FILE NOT FOUND]")
    return "\n".join(contents)

FORENSICS_REFERENCE = load_reference_texts()

# =========================
# Conversation History
# =========================

conversation = [
    {
        "role": "system",
        "content": f"""
You are a Digital Forensics Analyst Assistant.

Your purpose is to assist a security analyst in investigating digital evidence such as memory dumps, disk images, files, and logs.
You run locally and have access only to forensic tools listed in the Tool Reference below.
You do not have direct access to the operating system.

Your responsibilities:
- Understand forensic questions written in natural language
- Translate those questions into structured tool invocations
- Analyze tool output and summarize findings like a human forensic analyst

CRITICAL OUTPUT RULES:

When a tool must be executed, you MUST respond with ONLY a single valid JSON object.
No text before or after.
No markdown.
No backticks.
No explanations.

The ONLY allowed structure is:

{{
  "tool": "<tool_name>",
  "command": ["arg1", "arg2", "..."]
}}

Rules for "command":
- It is a JSON array of raw argument tokens
- Do NOT wrap arguments in extra quotes
- Do NOT combine arguments into a single string
- Do NOT include the binary name

INCORRECT:
["\\"windows.pslist\\""]
["windows.pslist -f mem.raw"]
["`windows.pslist`"]

CORRECT:
["windows.pslist", "-f", "mem.raw"]

If no tool is required, respond in clear, professional English.

After tool execution:
- You will receive raw tool output
- Analyze it and answer the user’s forensic question
- Do NOT expose internal commands

Tool Reference:
{FORENSICS_REFERENCE}
"""
    }
]

# =========================
# LLM Query
# =========================

def query_llm(prompt: str) -> str:
    conversation.append({"role": "user", "content": prompt})

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=conversation,
        options={
            "temperature": 0.1,
            "top_p": 0.9,
            "stop": ["```"]
        }
    )

    message = response["message"]["content"].strip()
    conversation.append({"role": "assistant", "content": message})
    return message

# =========================
# Tools Registry
# =========================

TOOLS = {
    "sha256sum": hash_file,
    "binwalk": run_binwalk,
    "cat": cat,
    "nmap": nmap_wrapper,
    "volatility3": run_volatility3,
}

# =========================
# Validation Helper
# =========================

def is_valid_tool_call(text: str) -> bool:
    try:
        data = json.loads(text)
        return (
            isinstance(data, dict)
            and "tool" in data
            and "command" in data
            and isinstance(data["command"], list)
            and all(isinstance(x, str) for x in data["command"])
        )
    except Exception:
        return False

# =========================
# Agent Logic
# =========================

def agent(user_input: str) -> str:
    response = query_llm(user_input)

    # First attempt
    if not is_valid_tool_call(response):
        return response
    else:
        print("🔧 Tool call detected, executing...")
    try:
        data = json.loads(response)
        tool_name = data["tool"]
        command = data["command"]

        if tool_name not in TOOLS:
            return response

        # Execute tool
        output = TOOLS[tool_name](*command)

        followup = f"""
The following output was produced by the tool "{tool_name}":

{output}

Analyze this output and answer the user's forensic question.
"""
        print(followup)
        return query_llm(followup)

    except json.JSONDecodeError:
        return response

# =========================
# CLI Loop
# =========================

if __name__ == "__main__":
    print("🧠 Forensic Agent (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ").strip()
        print()

        if user_input.lower() in {"exit", "quit"}:
            break

        reply = agent(user_input)
        print("Assistant:", reply)
        print()
