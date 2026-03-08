# Windows Memory Forensics – Workflow Library

This document describes common investigative workflows.
Workflows define intent → plugins → expected outcome.

---

## Workflow: Find Parent Process (PPID)

Intent:
Determine which process spawned a target process.

Trigger Phrases:
- "find the PPID"
- "identify parent process"
- "who spawned this process"

Required Inputs:
- Memory image
- Target process name or PID

Plugins Used:
- windows.pslist
- windows.pstree

Steps:
1. Enumerate processes to confirm target PID
2. Analyze process tree for parent-child relationship
3. Extract PPID and parent ImageFileName

Expected Outcome:
- Parent process name
- Parent PID (PPID)
- Contextual explanation

---

## Workflow: Identify Suspicious Command Line

Intent:
Review how a process was executed.

Trigger Phrases:
- "how was this process launched"
- "show command line arguments"

Required Inputs:
- Memory image
- Target process name or PID

Plugins Used:
- windows.pslist
- windows.cmdline

Steps:
1. Identify PID
2. Extract command-line arguments
3. Highlight suspicious parameters
