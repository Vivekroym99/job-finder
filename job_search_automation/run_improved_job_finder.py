#!/usr/bin/env python3
"""
Launch script for the improved Job Finder with enhanced UI and matching algorithm
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import nltk
    except ImportError:
        missing.append('nltk')
    
    try:
        import sklearn
    except ImportError:
        missing.append('scikit-learn')
    
    try:
        import numpy
    except ImportError:
        missing.append('numpy')
    
    try:
        import requests
    except ImportError:
        missing.append('requests')
    
    try:
        import bs4
    except ImportError:
        missing.append('beautifulsoup4')
    
    if missing:
        return False, missing
    
    return True, []

def main():
    """Main entry point for the improved Job Finder"""
    
    # Check dependencies
    deps_ok, missing_deps = check_dependencies()
    
    if not deps_ok:
        root = tk.Tk()
        root.withdraw()
        
        msg = f"Missing required dependencies:\n{', '.join(missing_deps)}\n\n"
        msg += "Please install them using:\n"
        msg += f"pip install {' '.join(missing_deps)}"
        
        messagebox.showerror("Dependencies Missing", msg)
        
        response = messagebox.askyesno(
            "Install Dependencies",
            "Would you like to install the missing dependencies now?"
        )
        
        if response:
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_deps)
                messagebox.showinfo("Success", "Dependencies installed successfully!\nPlease restart the application.")
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to install dependencies.\nPlease install manually.")
        
        root.destroy()
        return
    
    # Import and run the improved GUI
    try:
        from job_finder_improved import ImprovedJobFinderGUI, main as gui_main
        gui_main()
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Import Error", f"Failed to import Job Finder modules:\n{str(e)}")
        root.destroy()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", f"Failed to start Job Finder Pro 2.0:\n{str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()