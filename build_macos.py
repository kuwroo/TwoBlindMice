#!/usr/bin/env python3
import os
import shutil
import subprocess
import plistlib
from PIL import Image

def create_icns(png_path, icns_path):
    """Convert PNG to ICNS file with multiple sizes"""
    if not os.path.exists(png_path):
        print(f"Warning: Icon file {png_path} not found")
        return False
        
    # Create temporary iconset directory
    iconset_path = os.path.join(os.path.dirname(icns_path), 'icon.iconset')
    if os.path.exists(iconset_path):
        shutil.rmtree(iconset_path)
    os.makedirs(iconset_path)
    
    # Generate different icon sizes
    sizes = [
        (16, 16), (32, 32), (64, 64), (128, 128),
        (256, 256), (512, 512), (1024, 1024)
    ]
    
    try:
        for size in sizes:
            img = Image.open(png_path)
            # Regular size
            icon_path = os.path.join(iconset_path, f'icon_{size[0]}x{size[0]}.png')
            img.resize(size, Image.Resampling.LANCZOS).save(icon_path)
            # @2x size
            icon_path = os.path.join(iconset_path, f'icon_{size[0]}x{size[0]}@2x.png')
            img.resize((size[0]*2, size[1]*2), Image.Resampling.LANCZOS).save(icon_path)
            
        # Use iconutil to convert iconset to icns
        subprocess.run(['iconutil', '-c', 'icns', iconset_path], check=True)
        
        # Move the generated icns file to desired location
        generated_icns = os.path.join(os.path.dirname(iconset_path), 'icon.icns')
        if os.path.exists(generated_icns):
            shutil.move(generated_icns, icns_path)
            
        # Clean up
        shutil.rmtree(iconset_path)
        return True
    except Exception as e:
        print(f"Error creating icon: {e}")
        if os.path.exists(iconset_path):
            shutil.rmtree(iconset_path)
        return False

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
    
    # Create and add application icon
    print("You can now run the game by double-clicking TwoBlindMice.app")

if __name__ == '__main__':
    create_app_bundle()