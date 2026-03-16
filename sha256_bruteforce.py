#!/usr/bin/env python3
"""SHA-256 brute force: try all strings of given length from [a-zA-Z0-9] until hash matches.
   Use --gpu to run on NVIDIA GPU (e.g. RTX 5070) via hashcat (on Windows/Linux with the GPU)."""

import argparse
import hashlib
import itertools
import os
import platform
import shutil
import string
import subprocess
import sys
import tempfile

# Default: 6-char secret
TARGET_HASH_6 = "9994a0007e4271061b671424371f3f04dce63520b25ef9036fa45f3439e2f062"
TARGET_HASH_4 = "3803b47609a2a464054659b14a0cdfba92830fb46ee70c03a336d5554b9acad4"  # c0de
CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits  # 62 chars

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def crack_gpu(target: str, length: int) -> str | None:
    """Use hashcat (mode 1400 = SHA256) to crack on GPU. Same charset: a-zA-Z0-9 (-1 ?l?u?d)."""
    hashcat = shutil.which("hashcat")
    if not hashcat:
        print("hashcat not found in PATH. Install it to use --gpu (e.g. https://hashcat.net/hashcat/).", file=sys.stderr)
        return None
    target = target.strip().lower()
    if len(target) != 64 or not all(c in "0123456789abcdef" for c in target):
        print("Target must be a 64-character SHA-256 hex string.", file=sys.stderr)
        return None
    mask = "?1" * length  # custom charset 1 = ?l?u?d (a-zA-Z0-9)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(target + "\n")
        hashfile = f.name
    outfile = hashfile + ".out"
    try:
        # -m 1400 = SHA256, -a 3 = mask, -1 ?l?u?d = our 62-char set, --quiet = no banner
        subprocess.run(
            [hashcat, "-m", "1400", "-a", "3", hashfile, "-1", "?l?u?d", mask, "--quiet", "-o", outfile, "--potfile-disable"],
            capture_output=True,
            timeout=3600,
        )
        try:
            with open(outfile) as f:
                for line in f:
                    line = line.strip()
                    if ":" in line and line.startswith(target):
                        return line.split(":", 1)[1]
        except FileNotFoundError:
            pass
        return None
    finally:
        for p in (hashfile, outfile):
            try:
                os.unlink(p)
            except OSError:
                pass

def main():
    p = argparse.ArgumentParser(description="Brute force SHA-256 for fixed-length [a-zA-Z0-9].")
    p.add_argument("-n", "--length", type=int, default=6, help="Character length (default 6)")
    p.add_argument("-t", "--target", default=TARGET_HASH_6, help="Target SHA-256 hex (default 6-char hash)")
    p.add_argument("--gpu", action="store_true", help="Use GPU via hashcat (NVIDIA, e.g. RTX 5090)")
    args = p.parse_args()
    length = args.length
    target = args.target.strip().lower()
    total = len(CHARS) ** length

    if args.gpu:
        if platform.system() == "Darwin":
            print("Note: You're on macOS. NVIDIA GPUs (e.g. RTX 5070) are only used when you run this script on a Windows/Linux PC with the GPU and hashcat installed. Here we'll try hashcat if present (often CPU-only on Mac).", file=sys.stderr)
        print(f"Length {length}, charset [a-zA-Z0-9], total candidates: {total} (GPU via hashcat)", flush=True)
        password = crack_gpu(target, length)
        if password is not None:
            print(f"[+] FOUND: {password!r}")
            return
        if shutil.which("hashcat"):
            print("[-] No match.")
        # else crack_gpu already printed that hashcat was not found
        return

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
