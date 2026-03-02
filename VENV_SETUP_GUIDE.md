# 🔧 UNIFIED ENVIRONMENT SETUP - Complete Migration Guide

This guide will help you migrate from 2 separate venvs (.venv_cv + .venv_llm) to a single unified environment with zero conflicts.

---

## ❌ THE PROBLEM (Why 2 venvs?)

```
.venv_llm (LLM environment)
├── google-generativeai → requires protobuf >=3.20
├── ...
└── protobuf (version X)

.venv_cv (Vision environment)
├── ultralytics → can need different protobuf
├── mediapipe → can need different protobuf
└── protobuf (version Y) ❌ CONFLICT!
```

**Result:** Dependencies conflict, force you to switch between environments.

---

## ✅ THE SOLUTION

### Option 1: RECOMMENDED - Single Unified venv (Easiest)

#### Step 1: Create new unified environment
```powershell
# Go to project root
cd D:\WORK\ SELF\MAJOR\ PROJECT

# Delete old venvs (BACKUP FIRST if needed!)
Remove-Item -Recurse .venv_cv
Remove-Item -Recurse .venv_llm

# Create single unified venv
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1
```

#### Step 2: Install all dependencies
```powershell
# Upgrade pip (important!)
python -m pip install --upgrade pip

# Install all requirements (protobuf conflict resolved)
pip install -r requirements.txt

# Verify installation
python -c "import google.generativeai; import cv2; import mediapipe; print('✅ All libraries loaded!')"
```

#### Step 3: Update PowerShell profile (optional - auto-activation)
```powershell
# Edit PowerShell profile to auto-activate on terminal start
notepad $PROFILE

# Add this to your profile:
if (Test-Path "D:\WORK SELF\MAJOR PROJECT\.venv\Scripts\Activate.ps1") {
    & "D:\WORK SELF\MAJOR PROJECT\.venv\Scripts\Activate.ps1"
}
```

**Time:** ~5-10 minutes | **Best for:** Everyone

---

### Option 2: Docker (Ultimate Isolation)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t ai-project .
docker run -it ai-project
```

**Benefits:** No local environment conflicts, reproducible on any machine

---

### Option 3: Conda (Better dependency resolution)

```bash
# Install Miniconda from: https://docs.conda.io/projects/miniconda/en/latest/

# Create environment
conda create -n ai-project python=3.11

# Activate
conda activate ai-project

# Install (conda handles protobuf conflicts better)
pip install -r requirements.txt
```

**Benefits:** Better built-in dependency resolution, easier to manage

---

### Option 4: Poetry (Professional approach)

```bash
# Install poetry
pip install poetry

# Create pyproject.toml from requirements.txt
poetry init

# Or manually create pyproject.toml (see below)

# Install
poetry install

# Activate
poetry shell
```

`pyproject.toml` example:
```toml
[tool.poetry.dependencies]
python = "^3.11"
google-generativeai = ">=0.3.0"
opencv-python-headless = ">=4.8.0"
ultralytics = ">=8.0.0"
mediapipe = ">=0.10.0"
faster-whisper = ">=0.10.0"
sounddevice = ">=0.4.5"
rapidfuzz = ">=3.0.0"
python-dotenv = ">=1.0.0"
protobuf = ">=4.23.0,<5.0.0"
```

---

## 📋 QUICK COMPARISON TABLE

| Method | Setup Time | Maintenance | Reproducibility | Recommended |
|--------|-----------|-------------|-----------------|-------------|
| **Option 1: Single venv** | 5 min | Easy | Good | ✅ YES |
| Option 2: Docker | 10 min | Easy | Excellent | For production |
| Option 3: Conda | 5 min | Medium | Very Good | If using conda |
| Option 4: Poetry | 10 min | Hard | Excellent | For teams |

---

## 🚀 IMMEDIATE ACTION PLAN

### Step-by-step to get working in 5 minutes:

```powershell
# 1. Activate current .venv_cv (or .venv_llm)
.venv_cv\Scripts\Activate.ps1

# 2. Install missing packages
pip install google-generativeai protobuf>=4.23.0,<5.0.0

# 3. Test if everything works
python -c "import google.generativeai; import cv2; import mediapipe; print('✅ Works!')"

# 4. If works: Done!
# 5. If fails: Follow the full migration below
```

---

## 🔄 FULL MIGRATION (For permanent fix)

### Step 1: Backup current environments (optional)
```powershell
# Create archive of working venv
$date = Get-Date -Format "yyyyMMdd_HHmm"
Copy-Item -Path .venv_cv -Destination ".venv_cv_backup_$date" -Recurse
Copy-Item -Path .venv_llm -Destination ".venv_llm_backup_$date" -Recurse
```

### Step 2: Delete old venvs
```powershell
Remove-Item -Recurse -Force .venv_cv
Remove-Item -Recurse -Force .venv_llm
```

### Step 3: Create new unified venv
```powershell
# Make sure you're in project root
cd "D:\WORK SELF\MAJOR PROJECT"

# Create
python -m venv .venv

# Activate
.venv\Scripts\Activate.ps1

# Verify activation (should show (.venv) prefix)
```

### Step 4: Install dependencies
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all packages from requirements.txt
pip install -r requirements.txt

# Check installation
pip list | grep -E "google|opencv|ultralytics|mediapipe|whisper|sounddevice|rapidfuzz"
```

### Step 5: Test everything works
```powershell
# Test LLM
python -c "
import google.generativeai
print('✅ Gemini API ready')
"

# Test Vision
python -c "
import cv2
from ultralytics import YOLO
import mediapipe
print('✅ Vision libraries ready')
"

# Test Speech
python -c "
from faster_whisper import WhisperModel
import sounddevice
print('✅ Speech libraries ready')
"

# Test Intent
python -c "
from rapidfuzz import process
print('✅ Intent library ready')
"

# ALL TOGETHER
python -c "
import google.generativeai
import cv2
from ultralytics import YOLO
import mediapipe
from faster_whisper import WhisperModel
import sounddevice
from rapidfuzz import process
print('✅✅✅ ALL LIBRARIES WORKING!')
"
```

### Step 6: Test your app
```powershell
# Try running a test
python tests/demo_voice_to_chat.py

# Or the main AI
python ai/main_ai.py
```

---

## 🛠️ PROTOBUF CONFLICT - Technical Details

The issue occurs when multiple packages depend on incompatible protobuf versions:

```
google-generativeai → protobuf >=3.20,<4
ultralytics → protobuf >=3.20
mediapipe → protobuf >=3.20
```

**Solution:** Pin protobuf to a version all packages accept:
```
protobuf>=4.23.0,<5.0.0  ← Compatible with all packages
```

If still conflicts:
```powershell
# Nuclear option: force compatible version
pip install protobuf==4.24.0 --force-reinstall

# Then reinstall packages
pip install -r requirements.txt --ignore-installed protobuf
```

---

## ⚡ ACTIVATE ENVIRONMENT (Every time you start)

### PowerShell
```powershell
.venv\Scripts\Activate.ps1
```

### CMD
```cmd
.venv\Scripts\activate.bat
```

### Git Bash
```bash
source .venv/Scripts/activate
```

### Auto-activate (Edit PowerShell profile)
```powershell
# Open profile
notepad $PROFILE

# Add:
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}
```

---

## 📌 TROUBLESHOOTING

### Problem: "No module named google.generativeai"
```powershell
# Solution: Verify activation
python -c "import sys; print(sys.prefix)"  # Should show .venv path

# If not: Activate manually
.venv\Scripts\Activate.ps1

# Reinstall
pip install google-generativeai
```

### Problem: "Protobuf conflict"
```powershell
# Solution: Force compatible version
pip install protobuf==4.24.0 --force-reinstall
pip install -r requirements.txt
```

### Problem: "ImportError: No module named cv2"
```powershell
# Solution: Install headless opencv
pip install opencv-python-headless>=4.8.0

# Or regular (needs GUI libraries)
pip install opencv-python>=4.8.0
```

### Problem: "Multiple vlovs working but tests fail"
```powershell
# Make sure you're in right environment
python -m pip show google-generativeai  # Check install location

# If wrong location: Delete old venvs
Remove-Item -Recurse .venv_cv
Remove-Item -Recurse .venv_llm

# Restart terminal completely (close & reopen)
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Deleted both old venvs
- [ ] Created new .venv
- [ ] Activated .venv (see `(.venv)` in prompt)
- [ ] Installed all requirements
- [ ] Ran test_all_libraries.py successfully
- [ ] Can import google.generativeai
- [ ] Can import cv2, ultralytics, mediapipe
- [ ] Can import faster_whisper
- [ ] demo_voice_to_chat.py runs without errors
- [ ] API key in .env file

---

## 📚 REFERENCE

**Files:**
- `requirements.txt` - All dependencies with pinned versions
- `.env` - API key (must have GEMINI_API_KEY=...)
- `.venv/` - New unified virtual environment

**Key packages:**
- google-generativeai: LLM (Gemini API)
- opencv-python-headless: Computer vision
- ultralytics: YOLOv8 object detection
- mediapipe: Hand/face detection
- faster-whisper: Speech-to-text
- sounddevice: Audio input
- rapidfuzz: Intent detection

**Commands:**
```powershell
# Activate
.venv\Scripts\Activate.ps1

# Install/update
pip install -r requirements.txt

# Freeze current
pip freeze > requirements.txt

# Check specific package
pip show google-generativeai

# List all
pip list
```

---

## 🎯 RECOMMENDED NEXT STEPS

1. ✅ Run: `pip install -r requirements.txt`
2. ✅ Test: `python tests/demo_voice_to_chat.py`
3. ✅ Read: `tests/START_HERE.md`
4. ✅ Run: `python tests/test_integrated_system.py`

**Done! You now have a unified, conflict-free environment.** 🎉

---

*Last updated: March 2, 2026*
