#!/usr/bin/env python
"""
PyTorch + CUDA GPU Diagnostic Tool
Checks your GPU setup and PyTorch installation
"""

import sys
import subprocess
from pathlib import Path

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
END = "\033[0m"

def print_header(text):
    """Print section header."""
    print(f"\n{BLUE}{'='*70}{END}")
    print(f"{BLUE}{text:^70}{END}")
    print(f"{BLUE}{'='*70}{END}\n")

def check_nvidia_smi():
    """Check if NVIDIA drivers are installed."""
    print_header("STEP 1: NVIDIA GPU Check")
    
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"{GREEN}✅ NVIDIA Driver Installed{END}\n")
            print(result.stdout)
            return True
        else:
            print(f"{RED}❌ nvidia-smi failed{END}\n")
            print("Make sure NVIDIA drivers are installed")
            return False
    except FileNotFoundError:
        print(f"{RED}❌ nvidia-smi not found{END}\n")
        print("NVIDIA drivers not installed or not in PATH")
        print("Download from: https://www.nvidia.com/Download/driverDetails.aspx")
        return False
    except Exception as e:
        print(f"{RED}❌ Error: {e}{END}\n")
        return False

def check_cuda_toolkit():
    """Check if CUDA Toolkit is installed."""
    print_header("STEP 2: CUDA Toolkit Check")
    
    try:
        result = subprocess.run(
            ["nvcc", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"{GREEN}✅ CUDA Toolkit Installed{END}\n")
            print(result.stdout)
            return True
        else:
            print(f"{RED}❌ nvcc not found{END}\n")
            print("CUDA Toolkit not installed or not in PATH")
            print("Download from: https://developer.nvidia.com/cuda-downloads")
            return False
    except FileNotFoundError:
        print(f"{RED}❌ CUDA Toolkit not found{END}\n")
        print("Install from: https://developer.nvidia.com/cuda-12-1-0-download-archive")
        return False
    except Exception as e:
        print(f"{RED}❌ Error: {e}{END}\n")
        return False

def check_pytorch():
    """Check PyTorch installation."""
    print_header("STEP 3: PyTorch Installation")
    
    try:
        import torch
        print(f"{GREEN}✅ PyTorch Installed{END}\n")
        print(f"Version: {torch.__version__}")
        print(f"Location: {torch.__file__}")
        return True, torch
    except ImportError:
        print(f"{RED}❌ PyTorch not installed{END}\n")
        print("Install with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        return False, None

def check_cuda_availability(torch):
    """Check if CUDA is available to PyTorch."""
    print_header("STEP 4: CUDA Availability in PyTorch")
    
    if torch is None:
        print(f"{RED}❌ PyTorch not available{END}\n")
        return False
    
    is_available = torch.cuda.is_available()
    
    if is_available:
        print(f"{GREEN}✅ CUDA Available to PyTorch{END}\n")
        print(f"CUDA Version in PyTorch: {torch.version.cuda}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        return True
    else:
        print(f"{RED}❌ CUDA NOT available to PyTorch{END}\n")
        print("Possible causes:")
        print("  1. CUDA Toolkit not installed")
        print("  2. PyTorch CPU version installed (not GPU)")
        print("  3. CUDA version mismatch with PyTorch")
        print("\nFix: Reinstall PyTorch with CUDA support")
        print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall")
        return False

def check_gpu_details(torch):
    """Show GPU details."""
    print_header("STEP 5: GPU Details")
    
    if torch is None or not torch.cuda.is_available():
        print(f"{YELLOW}⚠️  CUDA not available - skipping GPU details{END}\n")
        return False
    
    try:
        device_count = torch.cuda.device_count()
        print(f"{GREEN}✅ GPU Information:{END}\n")
        
        for i in range(device_count):
            props = torch.cuda.get_device_properties(i)
            print(f"GPU {i}:")
            print(f"  Name: {torch.cuda.get_device_name(i)}")
            print(f"  Compute Capability: {props.major}.{props.minor}")
            print(f"  Total Memory: {props.total_memory / 1024**3:.1f} GB")
            
            # Try to allocate a small tensor to test memory
            try:
                x = torch.zeros(100, 100, device=f'cuda:{i}')
                allocated = torch.cuda.memory_allocated(i) / 1024**3
                print(f"  Available Memory: ~{props.total_memory / 1024**3 - allocated:.1f} GB")
            except:
                pass
            print()
        
        return True
    except Exception as e:
        print(f"{RED}❌ Error getting GPU details: {e}{END}\n")
        return False

def test_tensor_on_gpu(torch):
    """Test creating tensors on GPU."""
    print_header("STEP 6: Tensor GPU Test")
    
    if torch is None or not torch.cuda.is_available():
        print(f"{YELLOW}⚠️  CUDA not available - skipping tensor test{END}\n")
        return False
    
    try:
        print(f"{GREEN}✅ Creating tensors on GPU...{END}\n")
        
        # Test 1: Simple tensor
        x = torch.ones(1000, 1000, device='cuda')
        print(f"  Tensor created: shape {x.shape}, device {x.device}")
        
        # Test 2: Math operation
        y = x + x
        print(f"  Math operation: {y.shape} on {y.device}")
        
        # Test 3: GPU computation time
        import time
        start = time.time()
        z = torch.matmul(x, x)
        elapsed = time.time() - start
        print(f"  1000x1000 matrix multiply: {elapsed*1000:.2f}ms")
        
        print(f"\n{GREEN}✅ GPU tensor operations working!{END}\n")
        return True
    except Exception as e:
        print(f"{RED}❌ Tensor test failed: {e}{END}\n")
        return False

def check_cuda_memory(torch):
    """Check CUDA memory usage."""
    print_header("STEP 7: CUDA Memory")
    
    if torch is None or not torch.cuda.is_available():
        print(f"{YELLOW}⚠️  CUDA not available - skipping memory check{END}\n")
        return False
    
    try:
        print(f"{GREEN}✅ CUDA Memory Info:{END}\n")
        
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            total = props.total_memory / 1024**3
            allocated = torch.cuda.memory_allocated(i) / 1024**3
            reserved = torch.cuda.memory_reserved(i) / 1024**3
            
            print(f"GPU {i}:")
            print(f"  Total Memory: {total:.1f} GB")
            print(f"  Allocated: {allocated:.1f} GB")
            print(f"  Reserved: {reserved:.1f} GB")
            print(f"  Available: {total - reserved:.1f} GB")
            print()
        
        return True
    except Exception as e:
        print(f"{RED}❌ Error: {e}{END}\n")
        return False

def check_torchvision(torch):
    """Check TorchVision installation."""
    print_header("STEP 8: TorchVision Check")
    
    try:
        import torchvision
        print(f"{GREEN}✅ TorchVision Installed{END}\n")
        print(f"Version: {torchvision.__version__}")
        
        # Check CUDA support
        print(f"CUDA Supported: {torchvision.ops.roi_align.__module__}")
        return True
    except ImportError:
        print(f"{RED}❌ TorchVision not installed{END}\n")
        print("Install with: pip install torchvision --index-url https://download.pytorch.org/whl/cu121")
        return False
    except Exception as e:
        print(f"{YELLOW}⚠️  Warning: {e}{END}\n")
        return True

def check_ultralytics():
    """Check if YOLOv8 can use GPU."""
    print_header("STEP 9: YOLOv8 GPU Support")
    
    try:
        from ultralytics import YOLO
        print(f"{GREEN}✅ Ultralytics Installed{END}\n")
        
        # Check if YOLO can use GPU
        import torch
        if torch.cuda.is_available():
            print(f"{GREEN}✅ YOLOv8 can use GPU{END}\n")
            print("GPUs available for YOLOv8:")
            for i in range(torch.cuda.device_count()):
                print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
            return True
        else:
            print(f"{YELLOW}⚠️  YOLOv8 GPU not available (CPU mode){END}\n")
            return False
    except ImportError:
        print(f"{RED}❌ Ultralytics not installed{END}\n")
        return False
    except Exception as e:
        print(f"{RED}❌ Error: {e}{END}\n")
        return False

def print_summary(checks):
    """Print diagnostic summary."""
    print_header("DIAGNOSTIC SUMMARY")
    
    total = len(checks)
    passed = sum(1 for c in checks if c)
    failed = total - passed
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed}/{total}\n")
    
    if failed == 0:
        print(f"{GREEN}✅✅✅ ALL CHECKS PASSED! ✅✅✅{END}\n")
        print("Your GPU + PyTorch setup is complete and working!")
        print("\nNext steps:")
        print("  1. Run: python diagnostic.py (to verify venv setup)")
        print("  2. Run: python tests/test_integrated_system.py")
        print("  3. GPU acceleration enabled for YOLOv8 and PyTorch models!")
        return True
    else:
        print(f"{RED}❌ Some checks failed{END}\n")
        print("See errors above and follow the suggested fixes")
        return False

def main():
    """Run all diagnostics."""
    print(f"\n{BLUE}🚀 PyTorch + CUDA GPU Diagnostic Tool{END}")
    
    checks = []
    torch_instance = None
    
    # Run checks
    checks.append(check_nvidia_smi())
    checks.append(check_cuda_toolkit())
    pytorch_ok, torch_instance = check_pytorch()
    checks.append(pytorch_ok)
    checks.append(check_cuda_availability(torch_instance))
    checks.append(check_gpu_details(torch_instance))
    checks.append(test_tensor_on_gpu(torch_instance))
    checks.append(check_cuda_memory(torch_instance))
    checks.append(check_torchvision(torch_instance))
    checks.append(check_ultralytics())
    
    # Print summary
    success = print_summary(checks)
    
    print(f"{BLUE}{'='*70}{END}\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
