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
import time

try:
    from tqdm import tqdm
    _HAS_TQDM = True
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable
    _HAS_TQDM = False

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
        # -m 1400 = SHA256, -a 3 = mask, -1 ?l?u?d = our 62-char set; no --quiet so hashcat shows progress on GPU
        subprocess.run(
            [hashcat, "-m", "1400", "-a", "3", hashfile, "-1", "?l?u?d", mask, "-o", outfile, "--potfile-disable"],
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

# Default target hashes by length (so -n 4 uses the 4-char hash, etc.)
DEFAULT_HASH_BY_LENGTH = {4: TARGET_HASH_4, 6: TARGET_HASH_6}

def main():
    p = argparse.ArgumentParser(description="Brute force SHA-256 for fixed-length [a-zA-Z0-9].")
    p.add_argument("-n", "--length", type=int, default=6, help="Character length (default 6)")
    p.add_argument("-t", "--target", default=None, help="Target SHA-256 hex (default: use built-in hash for chosen length)")
    p.add_argument("--gpu", action="store_true", help="Use GPU via hashcat (NVIDIA, e.g. RTX 5090)")
    args = p.parse_args()
    length = args.length
    target = (args.target or DEFAULT_HASH_BY_LENGTH.get(length) or TARGET_HASH_6).strip().lower()
    total = len(CHARS) ** length

    if args.gpu:
        if platform.system() == "Darwin":
            print("Note: On macOS, hashcat runs in CPU/OpenCL mode (no NVIDIA). Still faster than Python in many cases.", file=sys.stderr)
        print(f"Length {length}, charset [a-zA-Z0-9], total candidates: {total} (hashcat)", flush=True)
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
    start = time.perf_counter()
    last_print_tried = 0
    last_print_time = start
    interval_sec = 1.0
    iterator = itertools.product(CHARS, repeat=length)
    use_tqdm = _HAS_TQDM and sys.stdout.isatty()
    if use_tqdm:
        iterator = tqdm(iterator, total=total, unit=" cand", unit_scale=True, ncols=100, mininterval=0.5)
    for t in iterator:
        candidate = "".join(t)
        tried += 1
        if sha256_hex(candidate) == target:
            if use_tqdm and hasattr(iterator, "close"):
                iterator.close()
            print(f"\n[+] FOUND: {candidate!r}")
            print(f"    Tried {tried} candidates.")
            return
        if not use_tqdm:
            now = time.perf_counter()
            if now - last_print_time >= interval_sec or tried - last_print_tried >= 500_000:
                elapsed = now - start
                rate = tried / elapsed if elapsed > 0 else 0
                eta_sec = (total - tried) / rate if rate > 0 else 0
                pct = 100.0 * tried / total
                print(f"\r  {tried:,} / {total:,} ({pct:.1f}%) | {elapsed:.0f}s elapsed | ~{eta_sec:.0f}s left ", end="", flush=True)
                last_print_tried, last_print_time = tried, now
    if use_tqdm and hasattr(iterator, "close"):
        iterator.close()
    print("\n[-] No match (tried {} candidates).".format(tried))

if __name__ == "__main__":
    main()
