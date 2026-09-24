"""
Build script to compile AuraSalat Desktop Overlay (ASDO) into a single standalone .exe
"""
import os
import subprocess
import sys

def build():
    print("=" * 60)
    print("Building AuraSalat Desktop Overlay (ASDO) Standalone Executable")
    print("=" * 60)

    # Ensure assets directory and icons exist
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "icon.ico")
    main_py = os.path.join(base_dir, "main.py")

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=AuraSalatOverlay",
        "--onefile",
        "--noconsole",
        "--clean",
    ]

    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    # Include assets folder
    assets_dir = os.path.join(base_dir, "assets")
    if os.path.exists(assets_dir):
        cmd.extend(["--add-data", f"{assets_dir};assets"])

    cmd.append(main_py)

    print("Running command:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=base_dir)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("Standalone executable located at:")
        print(os.path.join(base_dir, "dist", "AuraSalatOverlay.exe"))
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print(f"BUILD FAILED with exit code {result.returncode}")
        print("=" * 60)

if __name__ == "__main__":
    build()
