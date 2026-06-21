import os
import sys
import subprocess

def run_production_build():
    print("🚀 [ExileLedger Devops] Init production build compilation sequence...")
    
    # Verify PyInstaller binary environments
    try:
        import PyInstaller
    except ImportError:
        print("📦 PyInstaller dependency missing. Auto-installing framework dependency now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Configure PyInstaller build parameters
    # --noconsole hides native prompt shell overlays when opening the compiled GUI application.
    # To keep your console log outputs visible during execution, change '--noconsole' to '--console'.
    build_options = [
        'main.py',
        '--onefile',
        '--noconsole', 
        '--name=ExileLedger',
        '--clean'
    ]
    
    compilation_cmd = [sys.executable, '-m', 'PyInstaller'] + build_options
    print(f"🛠️ Executing build command sequence: {' '.join(compilation_cmd)}")
    
    # Spawn compiler subprocess
    subprocess.call(compilation_cmd)
    print("\n✨ Build sequence complete! Standalone executable available inside target path: './dist/ExileLedger.exe'")

if __name__ == "__main__":
    run_production_build()