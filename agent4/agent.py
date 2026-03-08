"""
agent.py — Digital Forensics Assistant agent.

Architecture:
  • tools.py   — tool registry (add new tools there)
  • rag.py     — vector-store backed retrieval of man pages / docs
  • agent.py   — LLM orchestration and chat loop  ← you are here

Before first run:
    python ingest_manpages.py
"""

import json
import re
import ollama
from tools import list_tools, run_tool
from rag import query_docs

# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

MODELS = [
    "dolphin3:8b",
    "qwen2.5-coder:7b",
    "qwen3:8b",
    "deepseek-r1:8b",
    "gemma2:9b",
    "llama3.1:8b",
]
MODEL = MODELS[5]

# ---------------------------------------------------------------------------
# Intent classification — keyword-based, no LLM call needed
# ---------------------------------------------------------------------------

# Words that strongly suggest the user wants to RUN a tool
_TOOL_INTENT_KEYWORDS = re.compile(
    r"\b(run|scan|hash|analyse|analyze|execute|check|compute|inspect|dump|"
    r"extract|crack|enumerate|fingerprint|identify|detect)\b",
    re.IGNORECASE,
)

# Words that strongly suggest plain conversation
_CHAT_INTENT_KEYWORDS = re.compile(
    r"\b(hi|hello|hey|thanks|thank you|what can you|what do you|how are you|"
    r"who are you|help me understand|explain|what is|what are|how does|"
    r"tell me about|what tools|can you)\b",
    re.IGNORECASE,
)

def _needs_rag(user_input: str) -> bool:
    """
    Return True only when the input looks like an actionable tool request
    that would benefit from man page context.

    Logic:
      - If it matches chat keywords and NOT tool keywords → no RAG
      - If it matches tool keywords → RAG
      - Ambiguous short messages (< 6 words, no path) → no RAG
    """
    has_tool_intent = bool(_TOOL_INTENT_KEYWORDS.search(user_input))
    has_chat_intent = bool(_CHAT_INTENT_KEYWORDS.search(user_input))
    has_path        = "/" in user_input or "\\" in user_input or "." in user_input.split()[-1]

    if has_chat_intent and not has_tool_intent:
        return False
    if has_tool_intent or has_path:
        return True
    # Short vague messages
    if len(user_input.split()) < 6:
        return False
    return True


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
        You are a Digital Forensics Analyst Assistant.
        Your purpose is to help a security analyst investigate digital evidence such as memory dumps, disk images, files, and logs.
        You run locally and have access to forensic tools installed on the system (via Python wrappers or CLI commands).
        Your job is to understand the user's requests in plain English and translate them into the correct tool usage, then analyze and summarize the results for the user.

        Behavior rules:
        1. Modes
            You must produce exactly ONE of the following outputs.

            MODE A — TOOL CALL
            Output exactly one JSON object of the format {"tool":"<tool_name>","args":["<arg1>","<arg2>", ...]} and nothing else. 
            Do not output commands in any other format. If you have pretrained data related to the user's request or the tool, forget it. 

            MODE B — ANALYSIS
            Output plain English analysis only. No JSON. No code blocks.

            If a tool is required, you MUST use MODE A.
            If a tool is not required, you MUST use MODE B.

            Any other output is invalid.

            INVALID OUTPUT EXAMPLES (DO NOT DO THIS):

                ❌ "Here is the command you asked for:"
                ❌ "Sure! I will now run the tool."
                ❌ "The answer is:"
                ❌ ```json ... ```

                VALID OUTPUT EXAMPLES:

                { "tool": "volatility3", "command": ["mem.raw", "process tree"] }

                OR

                The memory image shows multiple PowerShell instances spawned from winword.exe, indicating...


        2. Tool Call Format
        - Always output JSON exactly like this when you need a tool:
            {"tool":"<tool_name>","args":["<arg1>","<arg2>", ...]}
        - No extra text, no markdown, no explanations — just the JSON.
        - <tool_name> corresponds to the known tools given in the knowledge base only. You may refer to the knowledge base as well as the workflow chart for which tools are available and their usage.
        - Arguments must be passed as a JSON array of strings exactly as received from the user. Do not modify paths or filenames. 
        - Do not add or remove arguments like flags or plugins unless specifically instructed by the user. Use only that which is necessary for the tool to run within the users request.
        - If no arguments are needed, use an empty array: {"tool":"<tool_name>","args":[]}

        3. After Tool Execution
        - Once the system returns the output of the tool, you will receive a follow-up message describing the tools result.
        - At that point, respond to the user naturally, summarizing the results in clear English. You do not need to explain the commands.
        - You may also format your answer in JSON dictionaries or key-value lists if that makes it clearer, but do not expose internal commands.

        4. Consistency & Safety
        - Do not hallucinate tools or paths; only use tools you know.
        - Do not modify file paths or command arguments provided by the user.
        - If a requested action cannot be performed, explain why in natural language.

        5. Your style
        - Be concise but informative.
        - Be accurate and factual.
        - Provide structured outputs (tables, JSON summaries, or bullet points) when summarizing complex results.

        6. Example
        - User: “Can you compute the SHA256 hash of /mnt/c/Users/Alice/Desktop/test.txt?”
        - You (Tool Call): {"tool":"sha256sum","args":["/mnt/c/Users/Alice/Desktop/test.txt"]}
        - System runs sha256sum and gives you the output.
        - You (Natural Reply): “The SHA256 hash of /mnt/c/Users/Alice/Desktop/test.txt is 8b5f5…”
"""

# ---------------------------------------------------------------------------
# Conversation state
# ---------------------------------------------------------------------------

def _build_system_message() -> dict:
    return {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }


conversation = [_build_system_message()]


# ---------------------------------------------------------------------------
# LLM query
# ---------------------------------------------------------------------------

def _query_llm(user_message: str) -> str:
    """Append user message, query the model, append assistant reply, return text."""
    conversation.append({"role": "user", "content": user_message})

    response = ollama.chat(
        model=MODEL,
        messages=conversation,
        options={"temperature": 0.1},
    )

    reply = response["message"]["content"]
    conversation.append({"role": "assistant", "content": reply})
    return reply


# ---------------------------------------------------------------------------
# RAG context injection (only when intent warrants it)
# ---------------------------------------------------------------------------

def _build_rag_context(user_input: str) -> str:
    """
    Retrieve relevant man page chunks and return a formatted context block.
    Returns empty string if RAG is not needed or nothing useful is found.
    """
    if not _needs_rag(user_input):
        return ""

    docs = query_docs(user_input, top_k=5)
    if not docs:
        return ""

    return (
        "\n\n────────────────────────────────────\n"
        "RELEVANT TOOL DOCUMENTATION (from local man pages):\n"
        "────────────────────────────────────\n"
        + docs +
        "\n────────────────────────────────────\n"
    )


# ---------------------------------------------------------------------------
# Agent step
# ---------------------------------------------------------------------------

def agent(user_input: str) -> str:
    """
    Single agent turn:
      1. Classify intent — inject RAG context only if tool-related.
      2. Ask the LLM → may return a tool-call JSON or plain text.
      3. If tool call: run the tool, feed result back, get final answer.
      4. Return the final text to print.
    """
    rag_context    = _build_rag_context(user_input)
    augmented_input = user_input + rag_context

    response = _query_llm(augmented_input)

    # --- Attempt to parse as a tool call ---
    try:
        data = json.loads(response.strip())
    except json.JSONDecodeError:
        return response  # plain-language answer — return as-is

    if not (isinstance(data, dict) and "tool" in data and "args" in data):
        return response  # valid JSON but not a tool call

    tool_name = data["tool"]
    args      = data["args"]

    print(f"\n[Tool call] {tool_name}({', '.join(repr(a) for a in args)})\n")

    tool_output = run_tool(tool_name, args)

    followup = (
        f"The '{tool_name}' command has finished.\n\n"
        f"Raw output:\n{tool_output}\n\n"
        "Summarise these results clearly for the analyst. Use MODE B."
    )

    return _query_llm(followup)


# ---------------------------------------------------------------------------
# Chat loop
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("🔬 Digital Forensics Assistant (type 'exit' to quit)")
    print(f"   Model : {MODEL}")
    print(f"   Tools : {', '.join(list_tools())}")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        reply = agent(user_input)
        print(f"\nAssistant: {reply}\n")