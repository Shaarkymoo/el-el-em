🧠 Forensics Assistant (LLM-Powered CLI Agent)

A local Digital Forensics Assistant powered by LLMs that can:
- Understand natural language forensic queries
- Translate them into CLI tool calls
- Execute tools like nmap, volatility, binwalk, etc.
- Analyze and summarize results

This project is designed as a forensic co-pilot for analysts working with memory dumps, binaries, and network targets.

🚀 Features
🔍 Natural Language → CLI

Ask questions like:

"Compute the SHA256 hash of this file"
"Scan open ports on scanme.nmap.org"
"Analyze this memory dump for processes"

🛠 Supported Tools
sha256sum — file hashing
binwalk — firmware analysis
cat — file inspection
nmap — network scanning
john — password cracking
volatility3 — memory forensics
🧠 LLM Integration

🏗 Architecture
User Input
   ↓
LLM (intent understanding)
   ↓
Tool Call (JSON)
   ↓
Tool Execution
   ↓
LLM (result analysis)
   ↓
Final Answer
