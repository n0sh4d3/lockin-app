#!/usr/bin/env python3
"""
Cross-platform build script for the lockin app using PyInstaller
"""

import os
import sys
import platform
import subprocess


def get_data_separator():
    """Get the correct separator for --add-data based on platform"""
    return ";" if platform.system() == "Windows" else ":"


def get_icon_path():
    """Get the correct icon file based on platform"""
    if platform.system() == "Darwin":  # macOS
        return "icon.icns" if os.path.exists("icon.icns") else None
    else:
        return "icon.ico" if os.path.exists("icon.ico") else None


def build_app():
    """Build the application using PyInstaller"""
    sep = get_data_separator()
    icon_path = get_icon_path()

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name",
        "lockin",
    ]

    if platform.system() == "Windows":
        cmd.extend(["--uac-admin"])
        print("Added Windows UAC admin request")

    data_files = [
        f"fokus_settings.json{sep}.",
        f"sites.json{sep}.",
        f"sessions.json{sep}.",
        f"data.txt{sep}.",
        f"quotes{sep}quotes",
    ]

    for data_file in data_files:
        source = data_file.split(sep)[0]
        if os.path.exists(source):
            cmd.extend(["--add-data", data_file])
        else:
            print(f"Warning: {source} not found, skipping...")

    if icon_path:
        cmd.extend(["--icon", icon_path])
        print(f"Using icon: {icon_path}")
    else:
        print(
            "No icon file found (looking for icon.ico on Windows/Linux or icon.icns on macOS)"
        )

    cmd.append("main.py")

    print(f"Building on {platform.system()}...")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print("\nBuild completed successfully!")

        if platform.system() == "Windows":
            print("Executable created: dist\\lockin.exe")
        else:
            print("Executable created: dist/lockin")

    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("PyInstaller not found. Install it with: pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    build_app()
