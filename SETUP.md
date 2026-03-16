# Password cracker setup

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
