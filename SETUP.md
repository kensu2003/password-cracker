# Password cracker setup

## Hashcat on Mac (optional, for `--gpu`)

You can use hashcat on your Mac so `python3 sha256_bruteforce.py --gpu -n 4` uses it (CPU/OpenCL; no NVIDIA GPU on Mac).

**Install with Homebrew:**

```bash
brew install hashcat
```

Then run:

```bash
python3 sha256_bruteforce.py --gpu -n 4
```

Hashcat will show its own progress. On a PC with an NVIDIA GPU, use the same command there for much higher speed.

---

## Python (progress bar / brute force)

If you get **"externally managed environment"** when running `pip install -r requirements.txt`, use a virtual environment inside this project:

```bash
# From the password-cracker folder:

# Create venv
python3 -m venv .venv

# Activate it
# macOS/Linux:
source .venv/bin/activate
# Windows (cmd):
# .venv\Scripts\activate.bat
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# Then install (no more "externally managed" error)
pip install -r requirements.txt

# Run
python sha256_bruteforce.py -n 4
```

After activation, your prompt usually shows `(.venv)`. Then `pip install` only affects this folder.
