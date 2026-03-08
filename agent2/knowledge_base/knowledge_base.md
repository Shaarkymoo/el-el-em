# Forensics Tool Reference

This document defines all tools available to the assistant and the exact command formats they support.

The assistant MUST follow these examples exactly when producing tool calls.

---

## Tool: sha256sum

Purpose:
Compute the SHA256 hash of a file.

Command format:
{
  "tool": "sha256sum",
  "command": ["<file_path>"]
}

Example:
{
  "tool": "sha256sum",
  "command": ["/mnt/c/Users/Alice/Desktop/test.txt"]
}

---

## Tool: binwalk

Purpose:
Analyze binary files and firmware images.

Command format:
{
  "tool": "binwalk",
  "command": ["<file_path>"]
}

Example:
{
  "tool": "binwalk",
  "command": ["firmware.bin"]
}

---