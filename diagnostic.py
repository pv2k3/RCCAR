#!/usr/bin/env python
"""
Environment Diagnostic & Setup Utility
Tests all dependencies and helps diagnose environment issues
"""

import sys
import subprocess
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
END = "\033[0m"

class EnvironmentDiagnostic:
    """Diagnose and verify environment setup."""
    
    def __init__(self):
        self.results = {}
        self.failed = []
        self.warnings = []
    
    def print_header(self, text):
        """Print section header."""
        print(f"\n{BLUE}{'='*70}{END}")
        print(f"{BLUE}{text:^70}{END}")
        print(f"{BLUE}{'='*70}{END}\n")
    
    def check_python(self):
        """Check Python version."""
        print(f"🐍 Python Version: {sys.version}")
        print(f"   Location: {sys.executable}")
        
        major, minor = sys.version_info[:2]
        if major >= 3 and minor >= 9:
            print(f"   {GREEN}✅ Compatible (3.9+){END}\n")
            return True
        else:
            print(f"   {RED}❌ Needs Python 3.9+{END}\n")
            self.failed.append("Python version too old")
            return False
    
    def check_venv(self):
        """Check if running in virtual environment."""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            print(f"🎯 Virtual Environment: {GREEN}✅ ACTIVE{END}")
            print(f"   Location: {sys.prefix}\n")
            return True
        else:
            print(f"🎯 Virtual Environment: {RED}❌ NOT ACTIVE{END}")
            print(f"   {YELLOW}⚠️  Activate with: .venv\\Scripts\\Activate.ps1{END}\n")
            self.warnings.append("Not running in virtual environment")
            return False
    
    def check_pip(self):
        """Check pip version."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True
            )
            print(f"📦 Pip: {result.stdout.strip()}")
            print(f"   {GREEN}✅ Available{END}\n")
            return True
        except Exception as e:
            print(f"📦 Pip: {RED}❌ Error{END}")
            print(f"   {e}\n")
            self.failed.append(f"Pip error: {e}")
            return False
    
    def check_package(self, name, import_name=None, description=None):
        """Check if a package is installed."""
        if import_name is None:
            import_name = name.split('[')[0]
        
        try:
            exec(f"import {import_name}")
            # Get version
            try:
                module = __import__(import_name)
                version = getattr(module, '__version__', 'unknown')
                print(f"   {GREEN}✅{END} {name:<30} (v{version})")
            except:
                print(f"   {GREEN}✅{END} {name:<30}")
            return True
        except ImportError:
            print(f"   {RED}❌{END} {name:<30} {YELLOW}MISSING{END}")
            self.failed.append(f"Missing: {name}")
            return False
    
    def check_dependencies(self):
        """Check all required dependencies."""
        print(f"{BLUE}Checking Dependencies:{END}\n")
        
        packages = [
            ("google-generativeai", "google.generativeai", "LLM/Chat"),
            ("python-dotenv", "dotenv", "Environment config"),
            ("opencv-python-headless", "cv2", "Computer vision"),
            ("ultralytics", "ultralytics", "YOLOv8 detection"),
            ("mediapipe", "mediapipe", "Hand/face detection"),
            ("numpy", "numpy", "Numerical computing"),
            ("faster-whisper", "faster_whisper", "Speech-to-text"),
            ("sounddevice", "sounddevice", "Audio capture"),
            ("scipy", "scipy", "Scientific computing"),
            ("rapidfuzz", "rapidfuzz", "Intent detection"),
            ("protobuf", "google.protobuf", "Protocol buffers"),
        ]
        
        results = {}
        for name, import_name, desc in packages:
            results[name] = self.check_package(name, import_name, desc)
        
        print()
        return results
    
    def check_api_key(self):
        """Check if API key is configured."""
        print(f"{BLUE}API Key Configuration:{END}\n")
        
        # Check .env file
        env_path = Path(".env")
        if env_path.exists():
            print(f"   📄 .env file: {GREEN}✅ Found{END}")
            with open(env_path) as f:
                content = f.read()
                if "GEMINI_API_KEY" in content:
                    print(f"   🔑 GEMINI_API_KEY: {GREEN}✅ Set{END}\n")
                    return True
                else:
                    print(f"   🔑 GEMINI_API_KEY: {RED}❌ Not found{END}")
                    print(f"      Add to .env: GEMINI_API_KEY=your_key\n")
                    self.warnings.append("GEMINI_API_KEY not in .env")
                    return False
        else:
            print(f"   📄 .env file: {RED}❌ Not found{END}")
            print(f"      Create .env with: GEMINI_API_KEY=your_key\n")
            self.warnings.append(".env file not found")
            return False
    
    def check_model_file(self):
        """Check if YOLOv8 model file exists."""
        print(f"{BLUE}Model Files:{END}\n")
        
        model_path = Path("yolov8n.pt")
        if model_path.exists():
            size = model_path.stat().st_size / (1024*1024)
            print(f"   🤖 yolov8n.pt: {GREEN}✅ Found{END} ({size:.1f} MB)\n")
            return True
        else:
            print(f"   🤖 yolov8n.pt: {YELLOW}⚠️  Not found{END}")
            print(f"      Will auto-download on first use\n")
            return True  # Not critical
    
    def check_folders(self):
        """Check required folders."""
        print(f"{BLUE}Project Structure:{END}\n")
        
        folders = ["ai", "utils", "tests", "captured_images"]
        for folder in folders:
            path = Path(folder)
            if path.exists():
                print(f"   📁 {folder:<20} {GREEN}✅{END}")
            else:
                print(f"   📁 {folder:<20} {RED}❌ Missing!{END}")
                self.failed.append(f"Missing folder: {folder}")
    
    def print_summary(self):
        """Print summary and recommendations."""
        self.print_header("SUMMARY")
        
        if not self.failed and not self.warnings:
            print(f"{GREEN}✅✅✅ ALL CHECKS PASSED! ✅✅✅{END}\n")
            print("Your environment is ready to use!")
            return True
        
        if self.warnings:
            print(f"{YELLOW}⚠️  WARNINGS ({len(self.warnings)}):{END}\n")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
        
        if self.failed:
            print(f"{RED}❌ ERRORS ({len(self.failed)}):{END}\n")
            for error in self.failed:
                print(f"   • {error}")
            print()
            return False
        
        return True
    
    def print_recommendations(self):
        """Print fix recommendations."""
        print(f"{BLUE}{'='*70}{END}")
        print(f"{BLUE}RECOMMENDATIONS{END}")
        print(f"{BLUE}{'='*70}\n{END}")
        
        if "Not running in virtual environment" in self.warnings:
            print(f"1. {YELLOW}Activate virtual environment:{END}")
            print(f"   PowerShell: .venv\\Scripts\\Activate.ps1")
            print(f"   CMD: .venv\\Scripts\\activate.bat")
            print(f"   Bash: source .venv/Scripts/activate\n")
        
        if any("Missing" in e for e in self.failed):
            print(f"2. {YELLOW}Install missing packages:{END}")
            print(f"   pip install -r requirements.txt\n")
        
        if "GEMINI_API_KEY not in .env" in self.warnings:
            print(f"3. {YELLOW}Set up API key:{END}")
            print(f"   Create/edit .env file:")
            print(f"   GEMINI_API_KEY=your_api_key_here\n")
        
        if any("Missing folder" in e for e in self.failed):
            print(f"4. {YELLOW}Create missing folders:{END}")
            for error in self.failed:
                if "Missing folder" in error:
                    folder = error.split(": ")[1]
                    print(f"   mkdir {folder}")
            print()
    
    def run_all_checks(self):
        """Run all diagnostic checks."""
        self.print_header("ENVIRONMENT DIAGNOSTIC")
        
        self.check_python()
        self.check_venv()
        self.check_pip()
        
        self.print_header("DEPENDENCIES")
        self.check_dependencies()
        
        self.print_header("CONFIGURATION")
        self.check_api_key()
        self.check_model_file()
        self.check_folders()
        
        success = self.print_summary()
        self.print_recommendations()
        
        return success

def main():
    """Main entry point."""
    print(f"\n{BLUE}🔧 Environment Diagnostic Tool{END}")
    
    diagnostic = EnvironmentDiagnostic()
    success = diagnostic.run_all_checks()
    
    print(f"\n{BLUE}{'='*70}{END}")
    if success or not diagnostic.failed:
        print(f"{GREEN}Ready to use!{END}")
        print(f"\n📚 Next steps:")
        print(f"   1. Read: VENV_SETUP_GUIDE.md")
        print(f"   2. Run:  python tests/demo_voice_to_chat.py")
        print(f"   3. Read: tests/START_HERE.md")
    else:
        print(f"{RED}Fix errors above before proceeding.{END}")
    print(f"{BLUE}{'='*70}\n{END}")
    
    return 0 if (success or not diagnostic.failed) else 1

if __name__ == "__main__":
    sys.exit(main())
