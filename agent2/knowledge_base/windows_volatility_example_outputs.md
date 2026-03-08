# Volatility 3 – Example Outputs (Windows)

These examples illustrate typical output formats for supported plugins.

---

## Plugin: windows.pslist

```text
PID   PPID  ImageFileName
4     0     System
1880  4     explorer.exe
3420  1880  evil.exe
```

---

## Plugin: windows.pstree

```text
PID   PPID  ImageFileName
4     0     System
 └─1880 explorer.exe
    └─3420 evil.exe
```

---

## Plugin: windows.cmdline

```text
PID   ImageFileName  CommandLine
3420  evil.exe       evil.exe -silent -persist
```

---
