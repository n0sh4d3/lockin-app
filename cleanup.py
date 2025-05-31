#!/usr/bin/env python3
"""
Cleanup script to remove PyInstaller build files and directories
"""

import os
import shutil
import sys
import platform


def remove_if_exists(path):
    """Remove file or directory if it exists"""
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
            print(f"Removed file: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Removed directory: {path}")
    else:
        print(f"Not found (skipping): {path}")


def cleanup_pyinstaller():
    """Clean up all PyInstaller generated files and directories"""
    print("Cleaning up PyInstaller build files...")
    print("-" * 40)

    cleanup_items = [
        "build",
        "dist",
        "__pycache__",
        "main.spec",
        "lockin.spec",
        "*.spec",
    ]

    import glob

    for item in ["build", "dist", "__pycache__"]:
        remove_if_exists(item)

    spec_files = glob.glob("*.spec")
    for spec_file in spec_files:
        remove_if_exists(spec_file)

    for root, dirs, files in os.walk("."):
        dirs_to_remove = [d for d in dirs if d == "__pycache__"]
        for dir_name in dirs_to_remove:
            dir_path = os.path.join(root, dir_name)
            remove_if_exists(dir_path)

        for file in files:
            if file.endswith(".pyc") or file.endswith(".pyo"):
                file_path = os.path.join(root, file)
                remove_if_exists(file_path)

    print("-" * 40)
    print("Cleanup completed!")


def cleanup_all():
    """Clean up PyInstaller files and other common build artifacts"""
    print("Performing complete cleanup...")
    print("=" * 50)

    # PyInstaller cleanup
    cleanup_pyinstaller()

    print("\nCleaning additional build artifacts...")
    print("-" * 40)

    additional_items = [
        ".vscode",
        ".idea",
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        "app.log",
        "*.log",
    ]

    import glob

    log_files = glob.glob("*.log")
    for log_file in log_files:
        remove_if_exists(log_file)

    for item in [".DS_Store", "Thumbs.db", "desktop.ini", ".vscode", ".idea"]:
        remove_if_exists(item)

    print("-" * 40)
    print("Complete cleanup finished!")


def main():
    """Main function with user options"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--all", "-a"]:
            cleanup_all()
        elif sys.argv[1] in ["--help", "-h"]:
            print("PyInstaller Cleanup Script")
            print("Usage:")
            print("  python cleanup.py          # Clean PyInstaller files only")
            print("  python cleanup.py --all    # Clean all build artifacts")
            print("  python cleanup.py --help   # Show this help")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        cleanup_pyinstaller()


if __name__ == "__main__":
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    print(f"Platform: {platform.system()}")

    if len(sys.argv) > 1 and sys.argv[1] in ["--all", "-a"]:
        response = input(
            "\nThis will remove build files AND other artifacts. Continue? (y/N): "
        )
    else:
        response = input(
            "\nThis will remove PyInstaller build files (build/, dist/, *.spec). Continue? (y/N): "
        )

    if response.lower() in ["y", "yes"]:
        main()
    else:
        print("Cleanup cancelled.")
