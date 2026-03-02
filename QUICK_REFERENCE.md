# ⚡ ENVIRONMENT QUICK REFERENCE

**Print this or bookmark it!**

---

## 🎯 Quick Commands

### Activate Environment (Every terminal session)
```powershell
.venv\Scripts\Activate.ps1
```

### Install/Update Packages
```powershell
pip install -r requirements.txt
```

### Check Installation
```powershell
python diagnostic.py
```

### Run Tests
```powershell
python tests/demo_voice_to_chat.py
python tests/test_integrated_system.py
python tests/test_components.py
```

### List Installed Packages
```powershell
pip list
```

---

## 🚀 One-Command Setup

### Full Automated Setup
```powershell
.\setup.ps1
```
**Time:** 10 minutes | **Requires:** Internet, ~2GB disk

---

## 🔧 Troubleshooting Matrix

| Problem | Quick Fix | Full Solution |
|---------|-----------|---------------|
| Module not found | Activate venv first | See VENV_SETUP_GUIDE.md |
| Protobuf error | `pip install protobuf==4.24.0 --force-reinstall` | See UNIFIED_SOLUTION.md |
| Activation fails | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` | See VENV_SETUP_GUIDE.md |
| Import errors | `pip install -r requirements.txt` | Reinstall all packages |
| API key not found | Add to `.env`: `GEMINI_API_KEY=your_key` | See tests/README.md |

---

## 📊 Environment Info

**Default Setup:**
- venv location: `.venv/`
- Python: 3.9+
- Pip version: Latest (auto-upgraded)

**Key Packages:**
- ✅ google-generativeai (LLM)
- ✅ opencv-python-headless (CV)
- ✅ ultralytics (YOLO)
- ✅ mediapipe (Detection)
- ✅ faster-whisper (STT)
- ✅ sounddevice (Audio)
- ✅ rapidfuzz (Intent)

**Key Files:**
- `requirements.txt` - Dependencies
- `.env` - API configuration
- `setup.ps1` - Setup script
- `diagnostic.py` - Verification tool

---

## ✅ Verification Steps

```powershell
# 1. Check activation
echo $env:VIRTUAL_ENV  # Should show .venv path

# 2. Check Python
python --version  # Should be 3.9+

# 3. Check packages
pip show google-generativeai  # Should show version

# 4. Import all libraries
python -c "import google.generativeai, cv2, ultralytics, mediapipe, faster_whisper, sounddevice, rapidfuzz; print('OK')"

# 5. Run diagnostic
python diagnostic.py  # Shows complete status
```

---

## 🎓 Learning Path

### Beginner (5 minutes)
1. Run setup: `.\setup.ps1`
2. Activate: `.venv\Scripts\Activate.ps1`
3. Run: `python tests/demo_voice_to_chat.py`

### Intermediate (30 minutes)
1. Read: `UNIFIED_SOLUTION.md`
2. Run: `python diagnostic.py`
3. Test: `python tests/test_components.py`

### Advanced (1 hour)
1. Read: `VENV_SETUP_GUIDE.md`
2. Read: `requirements.txt` (understand dependencies)
3. Modify: `test_config.py` (customize settings)
4. Run: `python tests/test_integrated_system.py`

---

## 📞 Quick Reference Card

### Activation Methods

| OS | Command |
|----|---------|
| PowerShell | `.venv\Scripts\Activate.ps1` |
| CMD | `.venv\Scripts\activate.bat` |
| Bash | `source .venv/Scripts/activate` |

### Common Tasks

| Task | Command |
|------|---------|
| Activate | `.venv\Scripts\Activate.ps1` |
| Install all | `pip install -r requirements.txt` |
| Check status | `python diagnostic.py` |
| View packages | `pip list` |
| Run test | `python tests/[test_name].py` |
| View Python | `python --version` |
| Reinstall | `pip install --force-reinstall -r requirements.txt` |
| Update pip | `python -m pip install --upgrade pip` |

### Important Paths

| Item | Path |
|------|------|
| Virtual env | `.venv/` |
| Requirements | `requirements.txt` |
| Tests | `tests/` |
| Diagnostics | `diagnostic.py` |
| Setup script | `setup.ps1` or `setup.bat` |
| API config | `.env` |

---

## ⚠️ Common Mistakes

❌ **Don't:**
- Run without activating venv
- Mix pip from system with venv
- Delete .venv without backup
- Forget to add API key to .env
- Use old .venv_cv/.venv_llm after setup

✅ **Do:**
- Always activate `.venv` first
- Use `pip` from venv only
- Backup before deleting
- Set GEMINI_API_KEY in .env
- Use new single `.venv`

---

## 🆘 I'm Stuck!

1. **Check status:** `python diagnostic.py`
2. **Reactivate:** `.venv\Scripts\Activate.ps1`
3. **Reinstall:** `pip install -r requirements.txt`
4. **Read guides:**
   - Quick: `UNIFIED_SOLUTION.md`
   - Detailed: `VENV_SETUP_GUIDE.md`
   - Tests: `tests/README.md`
5. **Reset (nuclear):**
   ```powershell
   Remove-Item -Recurse .venv
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

---

## 📋 Pre-Flight Checklist

Before running tests:

- [ ] `.venv` folder exists
- [ ] Venv activated (see `(.venv)` in prompt)
- [ ] `python --version` is 3.9+
- [ ] `pip list` shows all required packages
- [ ] `.env` file has GEMINI_API_KEY
- [ ] `diagnostic.py` shows all green ✅

---

## 🎯 What's Installed

```
LLM:
  ✅ google-generativeai

VISION:
  ✅ opencv-python-headless
  ✅ ultralytics (YOLO)
  ✅ mediapipe

SPEECH:
  ✅ faster-whisper
  ✅ sounddevice

INTENT:
  ✅ rapidfuzz

UTILITIES:
  ✅ numpy
  ✅ scipy
  ✅ python-dotenv
  ✅ protobuf (4.24.0 - CONFLICT FIX)
```

---

## 💡 Tips & Tricks

### Keep terminal always activated
Add to PowerShell profile ($PROFILE):
```powershell
& "D:\WORK SELF\MAJOR PROJECT\.venv\Scripts\Activate.ps1"
```

### Create alias for commands
```powershell
Set-Alias test-all "python tests/test_integrated_system.py"
Set-Alias test-demo "python tests/demo_voice_to_chat.py"
```

### Check venv size
```powershell
(Get-ChildItem .venv -Recurse | Measure-Object -Sum Length).Sum / 1GB
```

### List outdated packages
```powershell
pip list --outdated
```

---

## 🚀 Next Steps

1. **Setup:** Run `.\setup.ps1`
2. **Verify:** Run `python diagnostic.py`
3. **Test:** Run `python tests/demo_voice_to_chat.py`
4. **Learn:** Read `tests/START_HERE.md`

**You're all set! 🎉**

---

*Quick Reference v1.0 - March 2, 2026*
