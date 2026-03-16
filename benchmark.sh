#!/usr/bin/env bash
# Run C and Python SHA256 crackers (4-char target) and print runtimes.

set -e
cd "$(dirname "$0")"

HASH4="3803b47609a2a464054659b14a0cdfba92830fb46ee70c03a336d5554b9acad4"

echo "=== C (sha256-cracker) - 4-char ==="
make -s 2>/dev/null
t1=$(python3 -c "
import time, subprocess
t = time.perf_counter()
p = subprocess.run(['./sha256-cracker'], capture_output=True, timeout=60)
out = p.stdout.decode()
print(out, end='')
print(time.perf_counter() - t)
")
echo "$t1" | sed '$d'
r1=$(echo "$t1" | tail -1)
echo "Runtime: ${r1}s"
echo ""

echo "=== Python (sha256_bruteforce.py) - 4-char ==="
t2=$(python3 -c "
import time, subprocess
t = time.perf_counter()
p = subprocess.run(['python3', 'sha256_bruteforce.py', '-n', '4', '-t', '$HASH4'], capture_output=True, timeout=60)
out = p.stdout.decode()
print(out, end='')
print(time.perf_counter() - t)
")
echo "$t2" | sed '$d'
r2=$(echo "$t2" | tail -1)
echo "Runtime: ${r2}s"
echo ""

echo "--- Summary ---"
printf "C:      %.3fs\n" "$r1"
printf "Python: %.3fs\n" "$r2"
