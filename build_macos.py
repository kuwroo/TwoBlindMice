#!/usr/bin/env python3
import os
import shutil
import subprocess
import plistlib

def create_app_bundle():
    # App bundle name
    app_name = "TwoBlindMice.app"
    
    # Create basic bundle structure
    bundle_path = os.path.join(os.getcwd(), app_name)
    contents_path = os.path.join(bundle_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    
    # Remove existing bundle if it exists
    if os.path.exists(bundle_path):
        shutil.rmtree(bundle_path)
    
    # Create directories
    os.makedirs(macos_path, exist_ok=True)
    os.makedirs(resources_path, exist_ok=True)
    
    # Create Info.plist
    info_plist = {
        'CFBundleName': 'TwoBlindMice',
        'CFBundleDisplayName': 'Two Blind Mice',
        'CFBundleIdentifier': 'com.game.twoblindmice',
        'CFBundleVersion': '1.0.0',
        'CFBundleExecutable': 'game_launcher',
        'CFBundleIconFile': 'AppIcon',
        'CFBundlePackageType': 'APPL',
        'LSMinimumSystemVersion': '10.10.0',
    }
    
    with open(os.path.join(contents_path, 'Info.plist'), 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # Create launcher script
    launcher_script = '''#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/../Resources"
./python/bin/python3 main.py
'''
    
    with open(os.path.join(macos_path, 'game_launcher'), 'w') as f:
        f.write(launcher_script)
    
    # Make launcher executable
    os.chmod(os.path.join(macos_path, 'game_launcher'), 0o755)
    
    # Copy game files to Resources
    game_files = [f for f in os.listdir('.') if f.endswith('.py')]
    game_files.append('requirements.txt')  # Add requirements.txt to files to copy
    for file in game_files:
        shutil.copy2(file, resources_path)
    
    # Copy resources folder
    shutil.copytree('resources', os.path.join(resources_path, 'resources'))
    
    # Create Python virtual environment in the bundle
    subprocess.run(['python3', '-m', 'venv', 
                   os.path.join(resources_path, 'python')], check=True)
    
    # Install dependencies in the bundled Python environment
    pip_path = os.path.join(resources_path, 'python', 'bin', 'pip')
    subprocess.run([pip_path, 'install', '-r', 
                   os.path.join(resources_path, 'requirements.txt')], check=True)
    
    print(f"Created app bundle at {bundle_path}")
    print("You can now run the game by double-clicking TwoBlindMice.app")

if __name__ == '__main__':
    create_app_bundle()