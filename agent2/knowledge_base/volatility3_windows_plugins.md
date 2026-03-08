# Volatility 3 – Windows Plugin Reference

This document lists supported Volatility 3 plugins for Windows forensics.
Only plugins listed here are valid.

---

## windows.pslist
Category: Process Enumeration  
Purpose: List active processes in memory.

Key Fields:
- PID: Process ID
- PPID: Parent Process ID
- ImageFileName: Executable name

Command Pattern:
vol.py -f <memory_file> windows.pslist

Typical Use Cases:
- Identify suspicious processes
- Obtain PID and PPID
- Baseline running processes

---

## windows.pstree
Category: Process Relationships  
Purpose: Display parent-child relationships between processes.

Key Fields:
- PID
- PPID
- ImageFileName
- Children

Command Pattern:
vol.py -f <memory_file> windows.pstree

Typical Use Cases:
- Identify process lineage
- Confirm parent process
- Detect anomalous process trees

---

## windows.cmdline
Category: Process Context  
Purpose: Display command-line arguments for processes.

Key Fields:
- PID
- ImageFileName
- CommandLine

Command Pattern:
vol.py -f <memory_file> windows.cmdline

Typical Use Cases:
- Identify suspicious execution parameters
