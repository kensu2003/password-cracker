#!/usr/bin/env python3
"""SHA-256 brute force: try all strings of given length from [a-zA-Z0-9] until hash matches."""

import argparse
import hashlib
import itertools
import string

# Default: 6-char secret
TARGET_HASH_6 = "9994a0007e4271061b671424371f3f04dce63520b25ef9036fa45f3439e2f062"
TARGET_HASH_4 = "3803b47609a2a464054659b14a0cdfba92830fb46ee70c03a336d5554b9acad4"  # c0de
CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits  # 62 chars

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def main():
    p = argparse.ArgumentParser(description="Brute force SHA-256 for fixed-length [a-zA-Z0-9].")
    p.add_argument("-n", "--length", type=int, default=6, help="Character length (default 6)")
    p.add_argument("-t", "--target", default=TARGET_HASH_6, help="Target SHA-256 hex (default 6-char hash)")
    args = p.parse_args()
    length = args.length
    target = args.target.strip().lower()
    total = len(CHARS) ** length
    print(f"Length {length}, charset size {len(CHARS)}, total candidates: {total}", flush=True)
    tried = 0
    for t in itertools.product(CHARS, repeat=length):
        candidate = "".join(t)
        tried += 1
        if sha256_hex(candidate) == target:
            print(f"[+] FOUND: {candidate!r}")
            print(f"    Tried {tried} candidates.")
            return
        if tried % 1_000_000 == 0:
            print(f"Tried {tried} candidates...", flush=True)
    print(f"[-] No match (tried {tried} candidates).")

if __name__ == "__main__":
    main()
