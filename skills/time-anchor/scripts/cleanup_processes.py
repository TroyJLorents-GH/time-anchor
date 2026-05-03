#!/usr/bin/env python3
"""Find and optionally kill stale Claude Code processes.

Windows leaks `claude.exe` processes when terminal windows are closed via
the X button instead of `/exit` or Ctrl-C. They keep running, holding RAM,
until reboot or manual kill.

Usage:
    python cleanup_processes.py                 # list only (dry run)
    python cleanup_processes.py --kill-orphans  # kill processes started > N hours ago
    python cleanup_processes.py --kill-all      # kill EVERY claude-code proc except current ancestor
                                                # (other open terminals will die — restart them after)

Flags:
    --older-than HOURS   Threshold for --kill-orphans (default 1)
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone


def list_claude_code_procs() -> list[dict]:
    """Return list of {pid, parent_pid, started_at, command_line} dicts."""
    if sys.platform == "win32":
        ps = (
            "Get-CimInstance Win32_Process -Filter \"Name='claude.exe'\" "
            "| Where-Object { $_.CommandLine -like '*claude-code*' } "
            "| Select-Object ProcessId, ParentProcessId, "
            "@{n='Started';e={$_.CreationDate.ToString('o')}}, CommandLine "
            "| ConvertTo-Json -Compress"
        )
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps],
                text=True, timeout=10, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return []
        if not out.strip():
            return []
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        return [
            {
                "pid": int(p["ProcessId"]),
                "parent_pid": int(p.get("ParentProcessId", 0) or 0),
                "started_at": p["Started"],
                "command_line": p.get("CommandLine", ""),
            }
            for p in data
        ]
    else:
        try:
            out = subprocess.check_output(
                ["pgrep", "-af", "claude-code"],
                text=True, timeout=5, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return []
        result = []
        for line in out.strip().splitlines():
            parts = line.split(None, 1)
            if not parts:
                continue
            try:
                pid = int(parts[0])
            except ValueError:
                continue
            cmd = parts[1] if len(parts) > 1 else ""
            try:
                started = subprocess.check_output(
                    ["ps", "-o", "lstart=", "-p", str(pid)],
                    text=True, timeout=3, stderr=subprocess.DEVNULL).strip()
            except Exception:
                started = ""
            result.append({
                "pid": pid,
                "parent_pid": 0,
                "started_at": started,
                "command_line": cmd,
            })
        return result


def find_my_claude_ancestor() -> int | None:
    """Walk up the parent chain from this Python process. Return the
    PID of the first claude.exe ancestor whose command line includes
    'claude-code', or None if not found."""
    if sys.platform == "win32":
        ps = """
        $cur = $PID
        while ($cur -gt 0) {
            $p = Get-CimInstance Win32_Process -Filter "ProcessId=$cur" -ErrorAction SilentlyContinue
            if (-not $p) { break }
            if ($p.Name -eq 'claude.exe' -and $p.CommandLine -like '*claude-code*') {
                Write-Output $p.ProcessId
                exit
            }
            $cur = $p.ParentProcessId
        }
        """
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps],
                text=True, timeout=10, stderr=subprocess.DEVNULL).strip()
            return int(out) if out.isdigit() else None
        except Exception:
            return None
    else:
        try:
            pid = os.getpid()
            for _ in range(20):
                with open(f"/proc/{pid}/status") as f:
                    name = ""
                    ppid = 0
                    for line in f:
                        if line.startswith("Name:"):
                            name = line.split()[1]
                        elif line.startswith("PPid:"):
                            ppid = int(line.split()[1])
                if name.startswith("claude"):
                    with open(f"/proc/{pid}/cmdline") as f:
                        if "claude-code" in f.read():
                            return pid
                if ppid <= 1:
                    return None
                pid = ppid
        except Exception:
            return None
    return None


def kill_pid(pid: int) -> bool:
    """Best-effort kill. Returns True on success."""
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                timeout=5, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        else:
            os.kill(pid, 9)
        return True
    except Exception:
        return False


def parse_iso(s: str) -> datetime | None:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def main() -> int:
    args = sys.argv[1:]
    mode = "list"
    older_than_hours = 4.0

    i = 0
    while i < len(args):
        a = args[i]
        if a == "--kill-orphans":
            mode = "kill_orphans"
        elif a == "--kill-all":
            mode = "kill_all"
        elif a == "--older-than" and i + 1 < len(args):
            try:
                older_than_hours = float(args[i + 1])
            except ValueError:
                print(f"ERROR: --older-than expects a number, got '{args[i+1]}'",
                      file=sys.stderr)
                return 1
            i += 1
        else:
            print(f"ERROR: unknown arg '{a}'", file=sys.stderr)
            return 1
        i += 1

    procs = list_claude_code_procs()
    keep_pid = find_my_claude_ancestor()

    now = datetime.now(timezone.utc)
    threshold = now - timedelta(hours=older_than_hours)

    candidates = []
    for p in procs:
        if p["pid"] == keep_pid:
            p["status"] = "current"
            continue
        started = parse_iso(p["started_at"]) if p["started_at"] else None
        is_orphan = started is not None and started < threshold
        p["is_orphan"] = is_orphan
        if mode == "kill_all":
            candidates.append(p)
        elif mode == "kill_orphans" and is_orphan:
            candidates.append(p)

    killed: list[int] = []
    failed: list[int] = []
    if mode in ("kill_orphans", "kill_all"):
        for p in candidates:
            if kill_pid(p["pid"]):
                killed.append(p["pid"])
            else:
                failed.append(p["pid"])

    print(json.dumps({
        "ok": True,
        "mode": mode,
        "total_processes": len(procs),
        "current_pid": keep_pid,
        "older_than_hours": older_than_hours,
        "candidates": [
            {"pid": p["pid"], "started_at": p["started_at"],
             "is_orphan": p.get("is_orphan", False)}
            for p in procs if p["pid"] != keep_pid
        ],
        "killed": killed,
        "failed": failed,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
