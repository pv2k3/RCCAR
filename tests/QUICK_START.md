# 🎯 Quick Test Reference

**Fastest way to test everything!**

---

## 🚀 Get Started in 30 Seconds

### 1. Activate Environment
```bash
.\.venv_cv\Scripts\Activate.ps1
```

### 2. Run Test
```bash
# Option A: Full integrated test
python tests/test_integrated_system.py

# Option B: Simple voice-to-chat
python tests/demo_voice_to_chat.py

# Option C: Component tests
python tests/test_components.py
```

### 3. Follow On-Screen Menu

---

## 🎤 Voice-to-Chat Test (Recommended)

**Simplest test - shows complete workflow**

```bash
python tests/demo_voice_to_chat.py
```

Then select:
- `1` - Single Voice Demo (speak for 5 seconds)
- `2` - Multi-turn Chat (chat for 3 exchanges)
- `3` - Quick Demo (no voice needed)

---

## 📝 Text-Only Test (No Microphone)

If you don't have a microphone:

```bash
python tests/test_integrated_system.py
```

Then select:
- `6` - Workflow with Text Input

Enter any text like:
- `"Hello"`
- `"Move forward"`
- `"Take a photo"`

---

## 🤖 What Gets Tested

Each test covers:

✅ **Speech-to-Text** (Whisper)
- Records 5 seconds of voice
- Converts to text

✅ **Intent Detection**
- Figures out what you want (chat, movement, etc.)
- Returns confidence score

✅ **AI Chat**
- Generates natural responses
- Uses Gemini API

✅ **Vision** (Optional)
- Captures image from camera
- Analyzes with AI

---

## 📊 Expected Results

### Chat Example
```
Input:  "Hello how are you"
Intent: chat (95% confidence)
Output: "Hello! I'm doing well, thank you for asking..."
```

### Movement Example
```
Input:  "Move forward slowly"
Intent: movement (90% confidence)
Output: Direction: forward, Speed: 1.0
```

### Photo Example
```
Input:  "Take a photo"
Intent: capture_image (92% confidence)
Output: Photo saved + Analysis
```

---

## ⏱️ Timing Expectations

| Operation | Time |
|-----------|------|
| Voice Recording | ~5 seconds |
| Speech-to-Text | 1-2 seconds |
| Intent Detection | 50-200ms |
| Chat Response | 1-3 seconds |
| **Total Single Demo** | **~8-10 seconds** |

---

## 🔍 Troubleshooting

### No microphone?
→ Use option `6` for text input

### No camera?
→ Use chat or component tests only

### API Error?
→ Check `.env` has `GEMINI_API_KEY`

### Model not loading?
→ Run: `pip install -r requirements.txt`

---

## 📁 Test Files Explained

| File | Purpose | Voice? | Camera? |
|------|---------|--------|--------|
| `demo_voice_to_chat.py` | Simple demo | ✅ | ❌ |
| `test_integrated_system.py` | Full pipeline | ✅ | ✅ |
| `test_components.py` | Individual parts | ✅ | ✅ |

---

## 🎯 Testing Order

**First Time:**
1. `demo_voice_to_chat.py` → option `3` (quick demo)
2. `demo_voice_to_chat.py` → option `1` (with voice)
3. `test_integrated_system.py` → option `6` (text input)

**Advanced:**
1. All integrated tests
2. Component tests
3. Custom scenarios

---

## 💡 Pro Tips

- Start with **quick demo** (no voice needed)
- Speak **clearly** into microphone
- Use **short**, **clear** sentences
- Test **one component at a time** first
- Build understanding **gradually**

---

## 📞 Need Help?

See full guide: `tests/README.md`

Common issues:
1. Speech not detected → Check microphone
2. API error → Check API key
3. Model error → Reinstall dependencies

---

**That's it! You're ready to test!** 🎉
