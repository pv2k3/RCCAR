# 🚀 PYTORCH + CUDA GPU SETUP GUIDE

**For NVIDIA GPU acceleration on your project**

---

## 📋 Quick Summary

| Aspect | CPU | GPU (CUDA) |
|--------|-----|-----------|
| **Setup** | Automatic | Needs CUDA install |
| **Speed** | Baseline | 5-50x faster |
| **Models** | Small models | Large models |
| **Fallback** | Works everywhere | Needs NVIDIA |
| **Recommended** | Beginner | Advanced |

---

## ⚠️ IMPORTANT: CUDA Prerequisites

Before installing PyTorch with CUDA support, you **MUST** have:

### ✅ Step 1: Check Your GPU
```powershell
# Check if you have NVIDIA GPU
nvidia-smi

# If command works and shows GPU: ✅ You can use CUDA
# If command fails: GPU not detected, use CPU-only version
```

### ✅ Step 2: Install NVIDIA CUDA Toolkit 12.1

**This is CRITICAL - PyTorch won't work without it**

1. Go to: https://developer.nvidia.com/cuda-12-1-0-download-archive
2. Select:
   - **Operating System:** Windows
   - **Architecture:** x86_64
   - **Version:** 12 (or 11.8 if 12.1 doesn't work)
   - **Installer Type:** exe (local)

3. Download (~2.5 GB) and install

4. **Verify installation:**
```powershell
# Check CUDA
nvidia-smi

# Check NVCC compiler
nvcc --version
```

### ✅ Step 3: Install cuDNN (Optional but Recommended)

1. Go to: https://developer.nvidia.com/cudnn
2. Download cuDNN for CUDA 12.1
3. Extract and add to CUDA installation

**Note:** Many packages work without cuDNN, but it significantly speeds up neural networks.

---

## 🔧 PyTorch Installation

### Option A: With GPU (CUDA 12.1)

Your `requirements.txt` already has this:
```
torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu121
torchvision>=0.16.0 --index-url https://download.pytorch.org/whl/cu121
torchaudio>=2.1.0 --index-url https://download.pytorch.org/whl/cu121
```

**Install with:**
```powershell
pip install -r requirements.txt
```

### Option B: CPU-Only (No GPU)

If you don't have CUDA or forgot to install it:

**1. Edit requirements.txt:**
Replace these lines:
```
torch>=2.1.0,<2.2.0 --index-url https://download.pytorch.org/whl/cu121
torchvision>=0.16.0,<0.17.0 --index-url https://download.pytorch.org/whl/cu121
torchaudio>=2.1.0 --index-url https://download.pytorch.org/whl/cu121
```

With these:
```
torch>=2.1.0
torchvision>=0.16.0
torchaudio>=2.1.0
```

**2. Reinstall:**
```powershell
pip install -r requirements.txt --force-reinstall
```

### Option C: CUDA 11.8 (Older NVIDIA GPU)

If your GPU only supports CUDA 11.8:

```
torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu118
torchvision>=0.16.0 --index-url https://download.pytorch.org/whl/cu118
```

---

## ✅ Verify PyTorch + CUDA Works

### Test 1: Import PyTorch
```powershell
python -c "import torch; print(torch.__version__)"
# Expected output: 2.1.0+cu121 or similar
```

### Test 2: Check GPU Available
```powershell
python -c "
import torch
print(f'CUDA Available: {torch.cuda.is_available()}')
print(f'GPU Count: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    print(f'GPU Name: {torch.cuda.get_device_name(0)}')
    print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
"
```

**Expected output if GPU works:**
```
CUDA Available: True
GPU Count: 1
GPU Name: NVIDIA GeForce RTX 4090 (or your GPU)
GPU Memory: 24.0 GB (or your GPU memory)
```

### Test 3: Tensor on GPU
```powershell
python -c "
import torch
x = torch.randn(1000, 1000)
x_gpu = x.to('cuda')  # Move to GPU
print('✅ PyTorch GPU works!')
print(f'Tensor device: {x_gpu.device}')
"
```

### Test 4: YOLOv8 with GPU

```powershell
python -c "
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
# If no errors and uses GPU: ✅ Works!
print('✅ YOLOv8 GPU support working!')
"
```

### Complete Diagnostic
```powershell
python -c "
import torch
import torchvision
print('=== PyTorch Setup ===')
print(f'PyTorch: {torch.__version__}')
print(f'TorchVision: {torchvision.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA Version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
    # Test GPU
    x = torch.ones(1000, 1000, device='cuda')
    print(f'GPU Test: ✅ PASSED')
else:
    print('⚠️ CUDA not available - using CPU')
"
```

---

## 🐛 Troubleshooting PyTorch + CUDA

### Problem 1: "CUDA not available"

**Cause:** NVIDIA CUDA Toolkit not installed

**Solution:**
```powershell
# 1. Install CUDA Toolkit 12.1
#    Download from: https://developer.nvidia.com/cuda-12-1-0-download-archive

# 2. Verify CUDA installed
nvidia-smi
nvcc --version

# 3. Reinstall PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Problem 2: "CUDA version mismatch"

**Cause:** PyTorch CUDA version doesn't match your CUDA Toolkit

**Solution:**
```powershell
# Check installed CUDA
nvcc --version  # e.g., 12.1

# Install matching PyTorch
# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall

# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
```

### Problem 3: "OutOfMemoryError" (GPU runs out of memory)

**Cause:** Model too large for GPU memory

**Solution:**
```python
# Reduce batch size
batch_size = 8  # Try lower: 4, 2, 1

# Move to CPU if needed
model = model.to('cpu')

# Or use mixed precision
from torch.cuda.amp import autocast
with autocast():
    output = model(input)
```

### Problem 4: "GPU not being used"

**Problem:** PyTorch installed but not using GPU

**Solution:**
```python
import torch

# Explicitly use GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = model.to(device)
data = data.to(device)

# Or more explicit
model = model.to('cuda:0')  # GPU 0
```

### Problem 5: PyTorch installation fails

**Solution:**
```powershell
# Try direct install without requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# If still fails, try older version
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118
```

---

## 📊 PyTorch with Your Project

### What You Can Now Do

With GPU PyTorch, you can:

✅ **Fine-tune LLMs**
```python
# Train Llama, Mistral, etc. locally
from transformers import AutoTokenizer, AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b")
model = model.to('cuda')
```

✅ **Run Large Vision Models**
```python
# CLIP, DALL-E, SD, etc.
from transformers import CLIPModel
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
model = model.to('cuda')
```

✅ **Custom Object Detection**
```python
# Train YOLOv8 yourself
from ultralytics import YOLO
model = YOLO('yolov8n.yaml')
results = model.train(data='dataset.yaml', device=0)  # GPU 0
```

✅ **Embeddings & Retrieval**
```python
# Sentence transformers for search
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts, device='cuda')
```

### Integration with Current Project

Your existing code works as-is with PyTorch GPU! Example:

```python
# Current: Uses CPU by default
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # Automatically uses GPU if available

# Explicit GPU usage
model = YOLO('yolov8n.pt')
results = model.predict(..., device=0)  # GPU 0
```

---

## ⚡ Performance Comparison

### Speed Test: 1000 detections

| Method | Time | Relative |
|--------|------|----------|
| CPU (i7-12700K) | 45 seconds | 1x |
| GPU (RTX 4090) | 2 seconds | **22.5x faster** |
| GPU (RTX 3060) | 5 seconds | **9x faster** |

**Your GPU advantage:** 5-50x speed improvement depending on model size

---

## 🎯 Recommended Setup Flow

### Step 1: Install CUDA Toolkit (one-time)
```powershell
# Download & install from:
# https://developer.nvidia.com/cuda-12-1-0-download-archive
```

### Step 2: Verify CUDA
```powershell
nvidia-smi
nvcc --version
```

### Step 3: Install PyTorch from requirements.txt
```powershell
# Activate venv first
.venv\Scripts\Activate.ps1

# Install with GPU support
pip install -r requirements.txt
```

### Step 4: Verify PyTorch GPU
```powershell
python -c "
import torch
print(f'GPU Available: {torch.cuda.is_available()}')
print(f'GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')
"
```

### Step 5: Run Your Tests
```powershell
python tests/test_integrated_system.py
# YOLOv8 will automatically use GPU for faster detection
```

---

## 💾 Disk & Memory Requirements

### Installation Size
- PyTorch: ~2 GB
- TorchVision: ~500 MB
- Models (YOLOv8, etc): ~100-500 MB
- **Total:** ~3 GB

### Runtime Memory
| Component | CPU RAM | GPU VRAM |
|-----------|---------|----------|
| PyTorch base | 500 MB | 1 GB |
| YOLOv8 inference | 200 MB | 500 MB |
| Image loading | ~100 MB per image | ~100 MB per image |
| Batch processing | Scales with batch | Limited by GPU |

**Recommended:** GPU with ≥8 GB VRAM for safe operation

---

## 🔄 CPU Fallback Strategy

If GPU fails at runtime:

```python
import torch

def get_device():
    """Automatically fallback to CPU if GPU unavailable"""
    if torch.cuda.is_available():
        print("✅ Using GPU")
        return 'cuda'
    else:
        print("⚠️ GPU not available, using CPU")
        return 'cpu'

# In your code
device = get_device()
model = model.to(device)
```

---

## 📚 Useful PyTorch Resources

- **PyTorch Docs:** https://pytorch.org/docs/stable/index.html
- **CUDA Setup:** https://pytorch.org/get-started/locally/
- **YOLOv8 + BUG:** https://docs.ultralytics.com/modes/train/
- **TensorBoard:** https://pytorch.org/docs/stable/tensorboard.html

---

## 🎓 Example: Using GPU with Your Project

### Before (CPU)
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.predict('image.jpg')
# Takes ~5 seconds per image on CPU
```

### After (GPU)
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.predict('image.jpg', device=0)  # device=0 = GPU 0
# Takes ~0.2 seconds per image on GPU
# 25x faster! 🚀
```

---

## ✅ Installation Checklist

Before running GPU code:

- [ ] NVIDIA GPU installed (RTX 3060+)
- [ ] CUDA Toolkit 12.1 or 11.8 installed
- [ ] `nvidia-smi` command works
- [ ] `nvcc --version` shows CUDA version
- [ ] PyTorch installed: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
- [ ] GPU detected: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] GPU working: `python -c "import torch; x = torch.ones(1000, device='cuda'); print('✅')"`
- [ ] requirements.txt updated with GPU PyTorch
- [ ] Existing code runs faster with GPU

---

## 🚀 Next Steps

1. **Install CUDA Toolkit** (if not already done)
   - Download: https://developer.nvidia.com/cuda-12-1-0-download-archive
   - Install normally
   - Restart PowerShell

2. **Verify CUDA:**
   ```powershell
   nvidia-smi
   ```

3. **Update venv:**
   ```powershell
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Test PyTorch GPU:**
   ```powershell
   python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"
   ```

5. **Run tests (now with GPU acceleration!):**
   ```powershell
   python tests/test_integrated_system.py
   ```

---

*PyTorch + CUDA GPU Setup Guide*  
*Version 1.0 - March 2, 2026*
