#!/usr/bin/env python3
"""
Job Finder GUI - Windows Desktop Application
A user-friendly interface for the LinkedIn job search automation system
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import json
from datetime import datetime
import webbrowser
from pathlib import Path

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.settings import Config
    from utils.resume_parser import ResumeParser
    from main import JobSearchAutomation
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required files are in the same directory")

class JobFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Finder Pro - LinkedIn Job Search Automation")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.resume_text = tk.StringVar()
        self.location = tk.StringVar(value="Poland")
        self.min_match = tk.IntVar(value=70)
        self.max_age = tk.IntVar(value=14)
        self.include_remote = tk.BooleanVar(value=True)
        self.use_basic_linkedin = tk.BooleanVar(value=False)
        self.output_dir = tk.StringVar(value=os.path.expanduser("~/Desktop/JobSearchResults"))
        
        # Search state
        self.is_searching = False
        self.search_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Job Finder Pro", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        
        # Tab 1: Resume & Settings
        settings_frame = ttk.Frame(notebook, padding="10")
        notebook.add(settings_frame, text="Resume & Settings")
        
        # Tab 2: Search Results
        results_frame = ttk.Frame(notebook, padding="10")
        notebook.add(results_frame, text="Search Results")
        
        # Tab 3: About
        about_frame = ttk.Frame(notebook, padding="10")
        notebook.add(about_frame, text="About")
        
        self.setup_settings_tab(settings_frame)
        self.setup_results_tab(results_frame)
        self.setup_about_tab(about_frame)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.search_button = ttk.Button(button_frame, text="🚀 Start Job Search", command=self.start_search)
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop Search", command=self.stop_search, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_results_button = ttk.Button(button_frame, text="📁 Open Results Folder", command=self.open_results_folder)
        self.open_results_button.pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to search for jobs")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))
        
    def setup_settings_tab(self, parent):
        """Setup the settings tab with resume input and search options"""
        
        # Resume section
        resume_frame = ttk.LabelFrame(parent, text="📄 Resume", padding="10")
        resume_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        parent.columnconfigure(0, weight=1)
        resume_frame.columnconfigure(0, weight=1)
        
        # Resume input methods
        resume_method_frame = ttk.Frame(resume_frame)
        resume_method_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(resume_method_frame, text="📁 Load from File", command=self.load_resume_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(resume_method_frame, text="📋 Paste Resume Text", command=self.paste_resume_dialog).pack(side=tk.LEFT)
        
        # Resume preview
        self.resume_preview = scrolledtext.ScrolledText(resume_frame, height=8, wrap=tk.WORD)
        self.resume_preview.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        resume_frame.rowconfigure(1, weight=1)
        
        # Search settings
        settings_frame = ttk.LabelFrame(parent, text="🔍 Search Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Location
        ttk.Label(settings_frame, text="Location:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        location_combo = ttk.Combobox(settings_frame, textvariable=self.location, values=[
            "Poland", "Warsaw", "Krakow", "Wroclaw", "Poznan", "Gdansk", "Lodz", "Katowice", "Remote Poland"
        ])
        location_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        # Min match percentage
        ttk.Label(settings_frame, text="Min Match %:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        match_spin = ttk.Spinbox(settings_frame, from_=50, to=95, textvariable=self.min_match, width=10)
        match_spin.grid(row=0, column=3, sticky=tk.W)
        
        # Max job age
        ttk.Label(settings_frame, text="Max Age (days):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        age_spin = ttk.Spinbox(settings_frame, from_=1, to=30, textvariable=self.max_age, width=10)
        age_spin.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Checkboxes
        ttk.Checkbutton(settings_frame, text="Include Remote Jobs", variable=self.include_remote).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        ttk.Checkbutton(settings_frame, text="Use Basic LinkedIn Scraper", variable=self.use_basic_linkedin).grid(row=2, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Output directory
        output_frame = ttk.LabelFrame(parent, text="💾 Output Settings", padding="10")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Save Results To:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(output_frame, textvariable=self.output_dir).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=2)
        
    def setup_results_tab(self, parent):
        """Setup the results tab to display search results and logs"""
        
        # Results summary
        summary_frame = ttk.LabelFrame(parent, text="📊 Search Summary", padding="10")
        summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        parent.columnconfigure(0, weight=1)
        
        self.summary_text = tk.Text(summary_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        summary_frame.columnconfigure(0, weight=1)
        
        # Search log
        log_frame = ttk.LabelFrame(parent, text="📝 Search Log", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        parent.rowconfigure(1, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Results files
        files_frame = ttk.LabelFrame(parent, text="📁 Generated Files", padding="10")
        files_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.files_listbox = tk.Listbox(files_frame, height=4)
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.files_listbox.bind('<Double-1>', self.open_selected_file)
        
        files_button_frame = ttk.Frame(files_frame)
        files_button_frame.grid(row=0, column=1, sticky=(tk.N))
        
        ttk.Button(files_button_frame, text="Open", command=self.open_selected_file).grid(row=0, column=0, pady=(0, 5))
        ttk.Button(files_button_frame, text="Refresh", command=self.refresh_files).grid(row=1, column=0)
        
        files_frame.columnconfigure(0, weight=1)
        
    def setup_about_tab(self, parent):
        """Setup the about tab with information about the application"""
        
        about_text = """
Job Finder Pro - LinkedIn Job Search Automation

🎯 Features:
• Multi-platform job search (LinkedIn, Glassdoor, Pracuj.pl, Google Jobs)
• AI-powered resume matching and scoring
• Dynamic location search across Poland
• Advanced LinkedIn scraping with Luminati techniques
• Automated Excel and JSON report generation
• Smart filtering by job age and match percentage

🚀 How to Use:
1. Paste your resume text or load from file
2. Select your preferred location and search settings
3. Click "Start Job Search" and wait for results
4. Review generated Excel sheet with matched jobs

🔧 Technical Details:
• Uses enhanced LinkedIn scraper with fallback mechanisms
• Searches 4 major job platforms simultaneously
• Generates match scores based on skills and experience
• Creates CSV and JSONL output files
• Includes audit logging for transparency

📊 Output Files:
• job_matches.csv - Excel-compatible spreadsheet
• job_matches.jsonl - Detailed JSON data
• job_search_audit.log - Search activity log

Made with ❤️ for job seekers everywhere!
        """
        
        about_label = ttk.Label(parent, text=about_text, justify=tk.LEFT, wraplength=600)
        about_label.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=10, pady=10)
        
    def load_resume_file(self):
        """Load resume from file"""
        file_path = filedialog.askopenfilename(
            title="Select Resume File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("Word documents", "*.docx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.resume_preview.delete(1.0, tk.END)
                self.resume_preview.insert(1.0, content)
                self.log(f"Loaded resume from: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load resume file:\n{str(e)}")
    
    def paste_resume_dialog(self):
        """Open dialog to paste resume text"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Paste Resume Text")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        ttk.Label(dialog, text="Paste your resume text below:", font=('Arial', 10, 'bold')).pack(pady=10)
        
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_resume():
            content = text_widget.get(1.0, tk.END).strip()
            if content:
                self.resume_preview.delete(1.0, tk.END)
                self.resume_preview.insert(1.0, content)
                self.log("Resume text pasted successfully")
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please enter some resume text")
        
        ttk.Button(button_frame, text="Save Resume", command=save_resume).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        text_widget.focus_set()
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Also print to console for debugging
        print(f"[GUI] {message}")
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_search(self):
        """Start the job search in a separate thread"""
        
        # Validate inputs
        resume_text = self.resume_preview.get(1.0, tk.END).strip()
        if not resume_text:
            messagebox.showerror("Error", "Please load a resume or paste resume text first!")
            return
        
        if not os.path.exists(self.output_dir.get()):
            try:
                os.makedirs(self.output_dir.get(), exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output directory:\n{str(e)}")
                return
        
        # Save resume to temporary file
        resume_path = os.path.join(self.output_dir.get(), "temp_resume.md")
        try:
            with open(resume_path, 'w', encoding='utf-8') as f:
                f.write(resume_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save resume:\n{str(e)}")
            return
        
        # Update UI for search state
        self.is_searching = True
        self.search_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        self.update_status("Starting job search...")
        
        # Clear previous results
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Start search thread
        self.search_thread = threading.Thread(target=self.run_search, args=(resume_path,))
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def run_search(self, resume_path):
        """Run the actual job search"""
        try:
            self.log("🚀 Starting Job Search Automation...")
            self.log(f"📄 Resume loaded from: {resume_path}")
            self.log(f"📍 Location: {self.location.get()}")
            self.log(f"🎯 Min Match: {self.min_match.get()}%")
            self.log(f"📅 Max Age: {self.max_age.get()} days")
            self.log(f"🌐 Include Remote: {self.include_remote.get()}")
            
            # Configure the job search
            config = Config()
            config.RESUME_FILE = resume_path
            config.SEARCH_LOCATION = self.location.get()
            config.MIN_MATCH_PCT = self.min_match.get()
            config.MAX_JOB_AGE_DAYS = self.max_age.get()
            config.INCLUDE_REMOTE = self.include_remote.get()
            config.USE_BASIC_LINKEDIN = self.use_basic_linkedin.get()
            config.OUTPUT_DIR = self.output_dir.get()
            config.CSV_OUTPUT = os.path.join(self.output_dir.get(), "job_matches.csv")
            config.JSONL_OUTPUT = os.path.join(self.output_dir.get(), "job_matches.jsonl")
            config.AUDIT_LOG = os.path.join(self.output_dir.get(), "job_search_audit.log")
            
            self.update_status("Initializing job search automation...")
            automation = JobSearchAutomation(config)
            
            self.update_status("Searching job platforms...")
            self.log("🔍 Searching LinkedIn, Glassdoor, Pracuj.pl, and Google Jobs...")
            
            # Run the search
            results = automation.run()
            
            # Update UI with results
            self.root.after(0, self.search_completed, len(results))
            
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.root.after(0, self.search_error, error_msg)
    
    def search_completed(self, job_count):
        """Handle search completion"""
        self.is_searching = False
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        
        self.log(f"✅ Search completed! Found {job_count} matching jobs")
        self.update_status(f"Search completed - {job_count} jobs found")
        
        # Update summary
        summary = f"Job Search Results\n"
        summary += f"=" * 30 + "\n"
        summary += f"Jobs Found: {job_count}\n"
        summary += f"Location: {self.location.get()}\n"
        summary += f"Min Match: {self.min_match.get()}%\n"
        summary += f"Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"\nFiles generated:\n"
        summary += f"• job_matches.csv (Excel compatible)\n"
        summary += f"• job_matches.jsonl (JSON data)\n"
        summary += f"• job_search_audit.log (Search log)\n"
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state=tk.DISABLED)
        
        # Refresh files list
        self.refresh_files()
        
        # Show success message
        messagebox.showinfo("Success", f"Job search completed!\n\n{job_count} matching jobs found.\n\nResults saved to:\n{self.output_dir.get()}")
    
    def search_error(self, error_msg):
        """Handle search error"""
        self.is_searching = False
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.update_status("Search failed")
        messagebox.showerror("Search Error", error_msg)
    
    def stop_search(self):
        """Stop the current search"""
        if self.is_searching:
            self.is_searching = False
            self.log("🛑 Search stopped by user")
            self.update_status("Search stopped")
        
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
    
    def open_results_folder(self):
        """Open the results folder in file explorer"""
        output_path = self.output_dir.get()
        if os.path.exists(output_path):
            if sys.platform == "win32":
                os.startfile(output_path)
            elif sys.platform == "darwin":
                os.system(f"open '{output_path}'")
            else:
                os.system(f"xdg-open '{output_path}'")
        else:
            messagebox.showwarning("Warning", f"Output directory does not exist:\n{output_path}")
    
    def refresh_files(self):
        """Refresh the files list"""
        self.files_listbox.delete(0, tk.END)
        output_path = self.output_dir.get()
        
        if os.path.exists(output_path):
            try:
                files = [f for f in os.listdir(output_path) if f.endswith(('.csv', '.jsonl', '.log'))]
                for file in sorted(files):
                    self.files_listbox.insert(tk.END, file)
            except Exception as e:
                self.log(f"Error refreshing files: {str(e)}")
    
    def open_selected_file(self, event=None):
        """Open the selected file"""
        selection = self.files_listbox.curselection()
        if selection:
            filename = self.files_listbox.get(selection[0])
            filepath = os.path.join(self.output_dir.get(), filename)
            
            if os.path.exists(filepath):
                if sys.platform == "win32":
                    os.startfile(filepath)
                elif sys.platform == "darwin":
                    os.system(f"open '{filepath}'")
                else:
                    os.system(f"xdg-open '{filepath}'")
            else:
                messagebox.showwarning("Warning", f"File not found:\n{filepath}")

def main():
    """Main function to run the GUI application"""
    try:
        root = tk.Tk()
        app = JobFinderGUI(root)
        
        # Set window icon (if available)
        try:
            root.iconbitmap("icon.ico")  # Add icon file if available
        except:
            pass
        
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Startup Error", f"Failed to start Job Finder Pro:\n{str(e)}")

if __name__ == "__main__":
    main()