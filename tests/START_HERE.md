# 🚀 START HERE

Welcome to the test suite! Pick your starting point below.

---

## ⚡ Quick Decision Tree

### 👤 "I'm new to this project"
**Start with:** Quick Demo
```bash
python tests/demo_voice_to_chat.py
# Then select option 3
```
**Time:** ~2 minutes | **Requirements:** None | **Learning value:** ⭐⭐⭐⭐⭐

---

### 🎤 "I want to test voice input"
**Start with:** Voice-to-Chat Demo
```bash
python tests/demo_voice_to_chat.py
# Then select option 1
```
**Time:** ~10 seconds | **Requirements:** Microphone | **Learning value:** ⭐⭐⭐⭐

---

### 📝 "I don't have a microphone"
**Start with:** Integrated System Test (Text mode)
```bash
python tests/test_integrated_system.py
# Then select option 6
```
**Time:** ~5 seconds | **Requirements:** None | **Learning value:** ⭐⭐⭐⭐⭐

---

### 🔄 "I want everything"
**Start with:** Full Integrated Test
```bash
python tests/test_integrated_system.py
# Then select option 1
```
**Time:** ~15 seconds | **Requirements:** Microphone (optional) | **Learning value:** ⭐⭐⭐⭐⭐

---

### 🧪 "I want to test individual components"
**Start with:** Component Tests
```bash
python tests/test_components.py
# Then select your component
```
**Time:** Variable | **Requirements:** Depends on component | **Learning value:** ⭐⭐⭐

---

### 📚 "I want to understand it first"
**Read:** [README.md](README.md)
**Then:** [QUICK_START.md](QUICK_START.md)
**Finally:** Choose above

---

## 📋 Test Files Overview

| File | Purpose | Best For |
|------|---------|----------|
| `demo_voice_to_chat.py` | Simple voice → text → intent → chat | Learning, quick tests, beginners |
| `test_integrated_system.py` | Full end-to-end testing | Comprehensive testing, all features |
| `test_components.py` | Individual component testing | Debugging, component validation |
| `test_config.py` | Configuration manager | Internal use |

---

## 🎯 Most Common Commands

```bash
# Quick demo (recommended first test)
python tests/demo_voice_to_chat.py

# Full test suite
python tests/test_integrated_system.py

# Component tests
python tests/test_components.py

# View all options
python tests/__init__.py
```

---

## ✅ Checklist for Success

- [ ] Read [QUICK_START.md](QUICK_START.md) (5 minutes)
- [ ] Run Option 3 of `demo_voice_to_chat.py` (2 minutes)
- [ ] Run Option 1 of `demo_voice_to_chat.py` with microphone (10 seconds)
- [ ] Run full workflow in `test_integrated_system.py` (10 seconds)
- [ ] Explore `test_components.py` (10-20 minutes)
- [ ] Read [README.md](README.md) for deep dive (30 minutes)

---

## 🆘 Troubleshooting

**Problem:** ImportError for packages
- **Solution:** Check [README.md](README.md) "Prerequisites" section

**Problem:** No microphone detected
- **Solution:** Use option 6 in `test_integrated_system.py` (text input)

**Problem:** API key not found
- **Solution:** Create `.env` file in project root with `GEMINI_API_KEY=your_key`

**Problem:** Camera not working
- **Solution:** Check permissions or use demo without camera

More help: See [README.md](README.md#troubleshooting)

---

## 📏 File Structure

```
tests/
├── START_HERE.md              ← You are here
├── QUICK_START.md             ← 5-minute reference
├── README.md                  ← Complete guide
├── SUMMARY.md                 ← Implementation overview
├── __init__.py                ← Test index & helper
├── test_config.py             ← Configuration
├── demo_voice_to_chat.py      ← Simple workflow
├── test_components.py         ← Component tests
└── test_integrated_system.py  ← Full integration test
```

---

## 🎓 Learning Path

1. **Beginner** → `demo_voice_to_chat.py` (option 3)
2. **Intermediate** → `demo_voice_to_chat.py` (option 1) + `test_components.py`
3. **Advanced** → `test_integrated_system.py` + read `README.md`
4. **Expert** → Modify configs in `test_config.py` and extend tests

---

## 📞 Quick Links

- 📖 [QUICK_START.md](QUICK_START.md) - 5 minute reference
- 📚 [README.md](README.md) - Full documentation
- 📋 [SUMMARY.md](SUMMARY.md) - Implementation overview
- 🔧 [test_config.py](test_config.py) - Configuration settings
- 🗂️ [__init__.py](__init__.py) - Test index & helper menu

---

## 🎯 Next Steps

**Pick one:**

```bash
# Absolute first-timer (2 minutes)
python tests/demo_voice_to_chat.py
# Select: 3

# With microphone (10 seconds)
python tests/demo_voice_to_chat.py
# Select: 1

# Without microphone/full test (5 seconds)
python tests/test_integrated_system.py
# Select: 6

# Browse all tests
python tests/__init__.py
```

---

**📝 Happy Testing! 🚀**
