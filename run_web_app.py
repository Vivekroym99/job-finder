#!/usr/bin/env python3
"""
Quick launcher for the web-based Job Finder application
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_socketio
        import requests
        import beautifulsoup4
        import pandas
        print("✅ All required packages found")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\nInstalling required packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"
            ])
            print("✅ Packages installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)  # Wait for server to start
    print("🌐 Opening browser...")
    webbrowser.open('http://localhost:5000')

def main():
    """Main function to start the web application"""
    print("🚀 Starting Job Finder Pro Web Application")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        input("Press Enter to exit...")
        return
    
    # Start browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the web application
    print("🔥 Starting web server...")
    print("📱 Web interface will open at: http://localhost:5000")
    print("⏹  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the web app
        from web_app import app, socketio
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n👋 Job Finder Web App stopped")
    except Exception as e:
        print(f"❌ Error starting web app: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()