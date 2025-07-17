#!/usr/bin/env python3
"""
Install the required dependencies for Ollama integration
"""
import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

def main():
    print("Installing Ollama dependencies for FLASH...")
    
    # Remove langchain-openai if it exists
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "langchain-openai", "-y"])
        print("✓ Removed langchain-openai")
    except subprocess.CalledProcessError:
        print("✓ langchain-openai was not installed")
    
    # Install langchain-ollama
    success = install_package("langchain-ollama")
    
    if success:
        print("\n✓ All dependencies installed successfully!")
        print("\nMake sure you have Ollama running with the following models:")
        print("- cogito:32b (for LLM)")
        print("- snowflake-arctic-embed2:latest (for embeddings)")
        print("\nYou can pull them with:")
        print("  ollama pull cogito:32b")
        print("  ollama pull snowflake-arctic-embed2:latest")
    else:
        print("\n✗ Some dependencies failed to install")
        sys.exit(1)

if __name__ == "__main__":
    main()
