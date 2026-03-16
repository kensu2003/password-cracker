#!/usr/bin/env python3
"""SHA-256 dictionary attack: walk current directory (SecLists), check every line of every .txt against target hash."""

import hashlib
from pathlib import Path

# 6-char secret
TARGET_HASH = "9994a0007e4271061b671424371f3f04dce63520b25ef9036fa45f3439e2f062"

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def main():
    base = Path(".").resolve()
    tried = 0
    for p in sorted(base.rglob("*.txt")):
        if not p.is_file():
            continue
        try:
            with p.open("r", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, 1):
                    candidate = line.rstrip("\n\r")
                    if not candidate:
                        continue
                    tried += 1
                    if sha256_hex(candidate) == TARGET_HASH:
                        print(f"[+] FOUND: {candidate!r}")
                        print(f"    File: {p.relative_to(base)} (line {line_no})")
                        print(f"    Tried {tried} candidates.")
                        return
                    if tried % 500000 == 0 and tried:
                        print(f"Tried {tried} candidates...")
        except (OSError, PermissionError) as e:
            print(f"Skip {p}: {e}", file=__import__("sys").stderr)
    print(f"[-] No match in directory (tried {tried} candidates).")

if __name__ == "__main__":
    main()
