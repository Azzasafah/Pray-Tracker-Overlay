"""
Automated Build Script for AuraSalat Desktop Overlay (ASDO)
1. Compiles Python application to standalone .exe via PyInstaller
2. Compiles Windows Setup Installer (.exe) via Inno Setup
"""
import os
import subprocess
import sys

def find_iscc() -> str:
    """Finds Inno Setup Compiler ISCC.exe on the system."""
    potential_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    for p in potential_paths:
        if os.path.exists(p):
            return p

    # Check PATH
    try:
        res = subprocess.run(["where", "ISCC.exe"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip().splitlines()[0]
    except Exception:
        pass

    return ""

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)

    print("=" * 65)
    print("STEP 1: Compiling ASDO Standalone Executable (.exe)...")
    print("=" * 65)
    build_exe_py = os.path.join(base_dir, "build_exe.py")
    res1 = subprocess.run([sys.executable, build_exe_py], cwd=base_dir)
    if res1.returncode != 0:
        print("[ERROR] PyInstaller compilation failed!")
        sys.exit(res1.returncode)

    print("\n" + "=" * 65)
    print("STEP 2: Compiling Windows Setup Installer (.exe)...")
    print("=" * 65)
    iscc_path = find_iscc()
    if not iscc_path:
        print("[WARNING] Inno Setup compiler (ISCC.exe) not found.")
        print("Please install Inno Setup 6 to generate Setup.exe installer.")
        return

    iss_file = os.path.join(base_dir, "installer.iss")
    res2 = subprocess.run([iscc_path, iss_file], cwd=base_dir)
    if res2.returncode == 0:
        print("\n" + "=" * 65)
        print("ALL BUILDS COMPLETED SUCCESSFULLY!")
        print("1. Standalone Portable Exe: dist/AuraSalatOverlay.exe")
        print("2. Windows Setup Installer:  dist/AuraSalatOverlay-Setup-v1.0.0.exe")
        print("=" * 65)
    else:
        print(f"[ERROR] Inno Setup compilation failed with code {res2.returncode}")

if __name__ == "__main__":
    main()
