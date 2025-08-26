#!/usr/bin/env python3
"""
Improved Job Finder GUI with enhanced UI and matching algorithm
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.settings import Config
    from utils.resume_parser import ResumeParser
    from main import JobSearchAutomation
    from matchers.enhanced_job_matcher import EnhancedJobMatcher
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required files are in the same directory")
    Config = None
    JobSearchAutomation = None

class ImprovedJobFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Finder Pro 2.0 - Enhanced Job Matching")
        self.root.geometry("1100x800")
        self.root.minsize(1000, 700)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Subheader.TLabel', font=('Arial', 10, 'bold'))
        
        # Variables for the new UI
        self.resume_content = ""
        self.location = tk.StringVar(value="Poland")
        self.experience_level = tk.StringVar(value="Junior")
        self.time_posted = tk.StringVar(value="1 week")
        self.skills_text = tk.StringVar()
        self.min_match = tk.IntVar(value=50)  # Changed to 50% minimum
        self.include_remote = tk.BooleanVar(value=True)
        self.output_dir = tk.StringVar(value=os.path.expanduser("~/Desktop/JobSearchResults"))
        
        # Search state
        self.is_searching = False
        self.search_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the enhanced user interface"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🎯 Job Finder Pro 2.0", font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame, text="Enhanced Matching Algorithm", font=('Arial', 10), foreground='gray')
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Create main notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        main_frame.rowconfigure(1, weight=1)
        
        # Tab 1: Job Search Form
        search_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(search_frame, text="🔍 Job Search")
        
        # Tab 2: Results
        results_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(results_frame, text="📊 Results")
        
        # Tab 3: Settings
        settings_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        self.setup_search_tab(search_frame)
        self.setup_results_tab(results_frame)
        self.setup_settings_tab(settings_frame)
        
        # Control buttons
        self.setup_control_buttons(main_frame)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready to search for jobs")
        self.status_label.pack(side=tk.LEFT)
        
        self.match_info_label = ttk.Label(status_frame, text="Matching: 60% Resume + 40% User Data", foreground='blue')
        self.match_info_label.pack(side=tk.RIGHT)
        
    def setup_search_tab(self, parent):
        """Setup the enhanced search tab with all input fields"""
        
        # Create a scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 1. Resume Input Section
        self.create_resume_section(scrollable_frame)
        
        # 2. Location Section
        self.create_location_section(scrollable_frame)
        
        # 3. Experience Level Section
        self.create_experience_section(scrollable_frame)
        
        # 4. Time Posted Section
        self.create_time_posted_section(scrollable_frame)
        
        # 5. Skills Section (Main Matching Criteria)
        self.create_skills_section(scrollable_frame)
        
    def create_resume_section(self, parent):
        """Create resume input section"""
        resume_frame = ttk.LabelFrame(parent, text="📄 Resume / CV", padding="15")
        resume_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Instructions
        ttk.Label(resume_frame, text="Paste your resume or load from file (60% weight in matching)", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(resume_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="📋 Paste Resume", 
                  command=self.paste_resume_dialog, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📁 Load from File", 
                  command=self.load_resume_file, width=20).pack(side=tk.LEFT)
        
        # Resume preview
        preview_label = ttk.Label(resume_frame, text="Resume Preview:", style='Subheader.TLabel')
        preview_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.resume_preview = scrolledtext.ScrolledText(resume_frame, height=10, wrap=tk.WORD, width=80)
        self.resume_preview.pack(fill=tk.BOTH, expand=True)
        
    def create_location_section(self, parent):
        """Create location input section"""
        location_frame = ttk.LabelFrame(parent, text="📍 Location", padding="15")
        location_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(location_frame, text="Where are you looking for jobs?", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        # Location input
        input_frame = ttk.Frame(location_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Location:").pack(side=tk.LEFT, padx=(0, 10))
        
        location_combo = ttk.Combobox(input_frame, textvariable=self.location, width=30, values=[
            "Poland", "Warsaw", "Krakow", "Wroclaw", "Poznan", "Gdansk", "Lodz", "Katowice",
            "Remote Poland", "Germany", "Netherlands", "United Kingdom", "United States", "Canada",
            "Remote Worldwide"
        ])
        location_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Checkbutton(input_frame, text="Include Remote Jobs", 
                       variable=self.include_remote).pack(side=tk.LEFT)
        
    def create_experience_section(self, parent):
        """Create experience level section"""
        exp_frame = ttk.LabelFrame(parent, text="💼 Experience Level", padding="15")
        exp_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(exp_frame, text="Select your experience level (contributes to 40% user data weight)", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        # Radio buttons for experience level
        exp_levels = [
            ("Internship / Entry Level", "Intern"),
            ("Junior (0-2 years)", "Junior"),
            ("Mid-level (2-5 years)", "Mid"),
            ("Senior (5-10 years)", "Senior"),
            ("Expert / Lead (10+ years)", "Expert")
        ]
        
        for text, value in exp_levels:
            ttk.Radiobutton(exp_frame, text=text, variable=self.experience_level, 
                           value=value).pack(anchor=tk.W, pady=2)
        
    def create_time_posted_section(self, parent):
        """Create time posted filter section"""
        time_frame = ttk.LabelFrame(parent, text="🕐 Job Posting Age", padding="15")
        time_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(time_frame, text="Show jobs posted within:", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        # Radio buttons for time posted
        time_options = [
            ("Past 24 hours", "1 day"),
            ("Past week", "1 week"),
            ("Past 2 weeks", "2 weeks"),
            ("Past month", "4 weeks"),
            ("Past 2 months", "8 weeks")
        ]
        
        for text, value in time_options:
            ttk.Radiobutton(time_frame, text=text, variable=self.time_posted, 
                           value=value).pack(anchor=tk.W, pady=2)
        
    def create_skills_section(self, parent):
        """Create skills input section - main matching criteria"""
        skills_frame = ttk.LabelFrame(parent, text="🎯 Skills (Main Matching Criteria)", padding="15")
        skills_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Instructions
        instruction_text = """Enter your key skills separated by commas (contributes to 40% user data weight).
These skills will be matched against job descriptions to find the best opportunities for you.
Example: Python, Machine Learning, Data Analysis, SQL, AWS, Docker"""
        
        ttk.Label(skills_frame, text=instruction_text, 
                 font=('Arial', 9), foreground='gray', wraplength=600).pack(anchor=tk.W, pady=(0, 10))
        
        # Skills text area
        ttk.Label(skills_frame, text="Your Skills:", style='Subheader.TLabel').pack(anchor=tk.W, pady=(5, 5))
        
        self.skills_input = scrolledtext.ScrolledText(skills_frame, height=4, wrap=tk.WORD, width=80)
        self.skills_input.pack(fill=tk.BOTH, expand=True)
        
        # Pre-populate with common skills buttons
        common_skills_frame = ttk.Frame(skills_frame)
        common_skills_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(common_skills_frame, text="Quick add common skills:", 
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 5))
        
        skills_categories = {
            "Programming": ["Python", "Java", "JavaScript", "C++", "SQL", "R"],
            "Engineering": ["AutoCAD", "SolidWorks", "MATLAB", "ANSYS", "Revit"],
            "Data": ["Machine Learning", "Data Analysis", "Statistics", "Excel", "Power BI"],
            "Soft Skills": ["Leadership", "Project Management", "Communication", "Teamwork"]
        }
        
        for category, skills in skills_categories.items():
            cat_frame = ttk.Frame(common_skills_frame)
            cat_frame.pack(anchor=tk.W, pady=2)
            
            ttk.Label(cat_frame, text=f"{category}:", width=15).pack(side=tk.LEFT)
            
            for skill in skills[:5]:  # Show first 5 skills per category
                ttk.Button(cat_frame, text=f"+ {skill}", width=12,
                          command=lambda s=skill: self.add_skill(s)).pack(side=tk.LEFT, padx=2)
        
    def add_skill(self, skill):
        """Add a skill to the skills input field"""
        current_text = self.skills_input.get(1.0, tk.END).strip()
        if current_text:
            if skill not in current_text:
                self.skills_input.insert(tk.END, f", {skill}")
        else:
            self.skills_input.insert(1.0, skill)
    
    def setup_results_tab(self, parent):
        """Setup the results tab"""
        # Results summary
        summary_frame = ttk.LabelFrame(parent, text="📊 Search Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.summary_text = tk.Text(summary_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Job matches table
        matches_frame = ttk.LabelFrame(parent, text="💼 Job Matches (Sorted by Match %)", padding="10")
        matches_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview for job matches
        columns = ('Match %', 'Job Title', 'Company', 'Location', 'Posted', 'Platform')
        self.matches_tree = ttk.Treeview(matches_frame, columns=columns, show='tree headings', height=15)
        
        # Define column headings
        self.matches_tree.heading('#0', text='#')
        for col in columns:
            self.matches_tree.heading(col, text=col)
            if col == 'Match %':
                self.matches_tree.column(col, width=80)
            elif col == 'Job Title':
                self.matches_tree.column(col, width=250)
            elif col == 'Company':
                self.matches_tree.column(col, width=150)
            else:
                self.matches_tree.column(col, width=100)
        
        self.matches_tree.column('#0', width=40)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(matches_frame, orient=tk.VERTICAL, command=self.matches_tree.yview)
        self.matches_tree.configure(yscrollcommand=scrollbar.set)
        
        self.matches_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double click to view job details
        self.matches_tree.bind('<Double-1>', self.view_job_details)
        
        # Export buttons
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill=tk.X)
        
        ttk.Button(export_frame, text="📥 Export to Excel", 
                  command=self.export_to_excel).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="📄 Export to JSON", 
                  command=self.export_to_json).pack(side=tk.LEFT)
        
    def setup_settings_tab(self, parent):
        """Setup the settings tab"""
        # Matching algorithm settings
        algo_frame = ttk.LabelFrame(parent, text="🎯 Matching Algorithm", padding="15")
        algo_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(algo_frame, text="Current Configuration:", style='Subheader.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        settings_text = """• Resume Content Weight: 60%
• User-Provided Data Weight: 40%
  - Skills: 25%
  - Experience Level: 15%
  
• Minimum Match Threshold: 50%
• Results sorted by match percentage (highest first)
• Jobs below 50% match are automatically filtered out"""
        
        ttk.Label(algo_frame, text=settings_text, font=('Arial', 10)).pack(anchor=tk.W)
        
        # Match threshold adjustment
        threshold_frame = ttk.Frame(algo_frame)
        threshold_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(threshold_frame, text="Minimum Match Threshold:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Scale(threshold_frame, from_=50, to=90, orient=tk.HORIZONTAL, 
                 variable=self.min_match, length=200).pack(side=tk.LEFT, padx=(0, 10))
        self.threshold_label = ttk.Label(threshold_frame, text="50%")
        self.threshold_label.pack(side=tk.LEFT)
        
        # Update threshold label when slider changes
        def update_threshold_label(value):
            self.threshold_label.config(text=f"{int(float(value))}%")
        
        self.min_match.trace('w', lambda *args: update_threshold_label(self.min_match.get()))
        
        # Output settings
        output_frame = ttk.LabelFrame(parent, text="💾 Output Settings", padding="15")
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(output_frame, text="Save Results To:").pack(anchor=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X)
        
        ttk.Entry(dir_frame, textvariable=self.output_dir, width=50).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(dir_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.LEFT)
        
    def setup_control_buttons(self, parent):
        """Setup control buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # Search button with larger size and color
        self.search_button = ttk.Button(button_frame, text="🚀 Start Job Search", 
                                       command=self.start_search)
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop Search", 
                                     command=self.stop_search, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        ttk.Button(button_frame, text="🔄 Clear All", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=(0, 10))
        
        # Results folder button
        self.open_results_button = ttk.Button(button_frame, text="📁 Open Results Folder", 
                                             command=self.open_results_folder)
        self.open_results_button.pack(side=tk.RIGHT)
        
    def paste_resume_dialog(self):
        """Open dialog to paste resume text"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Paste Resume Text")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        ttk.Label(dialog, text="Paste your resume text below:", 
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_resume():
            content = text_widget.get(1.0, tk.END).strip()
            if content:
                self.resume_content = content
                self.resume_preview.delete(1.0, tk.END)
                self.resume_preview.insert(1.0, content)
                self.update_status("Resume loaded successfully")
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please enter resume text")
        
        ttk.Button(button_frame, text="✅ Save Resume", command=save_resume, 
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, 
                  width=20).pack(side=tk.LEFT)
        
        text_widget.focus_set()
    
    def load_resume_file(self):
        """Load resume from file"""
        file_path = filedialog.askopenfilename(
            title="Select Resume File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("Word documents", "*.docx"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.resume_content = content
                self.resume_preview.delete(1.0, tk.END)
                self.resume_preview.insert(1.0, content)
                self.update_status(f"Resume loaded from: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load resume:\n{str(e)}")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def clear_all(self):
        """Clear all inputs and results"""
        self.resume_preview.delete(1.0, tk.END)
        self.skills_input.delete(1.0, tk.END)
        self.matches_tree.delete(*self.matches_tree.get_children())
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.config(state=tk.DISABLED)
        self.resume_content = ""
        self.update_status("All fields cleared")
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_search(self):
        """Start the job search with validation"""
        # Get and validate inputs
        resume_text = self.resume_preview.get(1.0, tk.END).strip()
        if not resume_text:
            messagebox.showerror("Error", "Please paste your resume or load from file!")
            return
        
        skills_text = self.skills_input.get(1.0, tk.END).strip()
        if not skills_text:
            response = messagebox.askyesno("No Skills", 
                                          "No skills entered. Continue with resume-only matching?")
            if not response:
                return
        
        # Create output directory
        if not os.path.exists(self.output_dir.get()):
            try:
                os.makedirs(self.output_dir.get(), exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output directory:\n{str(e)}")
                return
        
        # Update UI for search state
        self.is_searching = True
        self.search_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        self.update_status("Starting enhanced job search...")
        
        # Clear previous results
        self.matches_tree.delete(*self.matches_tree.get_children())
        
        # Start search thread
        self.search_thread = threading.Thread(target=self.run_enhanced_search, 
                                             args=(resume_text, skills_text))
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def run_enhanced_search(self, resume_text, skills_text):
        """Run the enhanced job search with new algorithm"""
        try:
            # Check if imports are available
            if Config is None or JobSearchAutomation is None:
                raise ImportError("Required modules not available. Please check installation.")
            
            # Prepare search parameters
            user_skills = [s.strip() for s in skills_text.split(',') if s.strip()]
            
            print(f"🎯 Starting enhanced search with {len(user_skills)} skills")
            print(f"📊 User skills: {user_skills}")
            
            # Convert time posted to days
            time_map = {
                "1 day": 1,
                "1 week": 7,
                "2 weeks": 14,
                "4 weeks": 30,
                "8 weeks": 60
            }
            max_days = time_map.get(self.time_posted.get(), 14)
            
            # Experience level mapping
            exp_map = {
                "Intern": 0,
                "Junior": 1,
                "Mid": 3,
                "Senior": 7,
                "Expert": 12
            }
            experience_years = exp_map.get(self.experience_level.get(), 1)
            
            # Save resume temporarily
            resume_path = os.path.join(self.output_dir.get(), "temp_resume.md")
            with open(resume_path, 'w', encoding='utf-8') as f:
                f.write(resume_text)
            
            print(f"💾 Resume saved to: {resume_path}")
            
            # Configure job search
            config = Config()
            config.RESUME_FILE = resume_path
            config.SEARCH_LOCATION = self.location.get()
            config.MIN_MATCH_PCT = self.min_match.get()
            config.MAX_JOB_AGE_DAYS = max_days
            config.INCLUDE_REMOTE = self.include_remote.get()
            config.OUTPUT_DIR = self.output_dir.get()
            config.CSV_OUTPUT = os.path.join(self.output_dir.get(), "job_matches_enhanced.csv")
            config.JSONL_OUTPUT = os.path.join(self.output_dir.get(), "job_matches_enhanced.jsonl")
            
            # Add enhanced parameters
            config.USER_SKILLS = user_skills
            config.USER_EXPERIENCE = experience_years
            config.ENHANCED_MATCHING = True
            
            print(f"⚙️ Config setup complete")
            self.update_status("Initializing enhanced matching algorithm...")
            
            # Run the search (this would use the enhanced matcher)
            print("🔍 Starting JobSearchAutomation...")
            automation = JobSearchAutomation(config)
            results = automation.run()
            
            print(f"✅ Search completed with {len(results) if results else 0} results")
            
            # Update UI with results
            self.root.after(0, self.display_enhanced_results, results)
            
        except Exception as e:
            print(f"❌ Error in run_enhanced_search: {str(e)}")
            import traceback
            traceback.print_exc()
            error_msg = f"Search failed: {str(e)}"
            self.root.after(0, self.search_error, error_msg)
    
    def display_enhanced_results(self, results):
        """Display enhanced search results sorted by match percentage"""
        self.is_searching = False
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        
        # Sort results by match score (highest first)
        if results:
            results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Clear and populate tree
        self.matches_tree.delete(*self.matches_tree.get_children())
        
        for idx, job in enumerate(results, 1):
            match_score = job.get('match_score', 0)
            
            # Color code by match percentage
            if match_score >= 80:
                tag = 'excellent'
            elif match_score >= 70:
                tag = 'good'
            elif match_score >= 60:
                tag = 'fair'
            else:
                tag = 'low'
            
            self.matches_tree.insert('', 'end', text=str(idx),
                                    values=(f"{match_score:.1f}%",
                                           job.get('job_title', 'N/A'),
                                           job.get('company', 'N/A'),
                                           job.get('location', 'N/A'),
                                           job.get('posted_date', 'N/A'),
                                           job.get('platform', 'N/A')),
                                    tags=(tag,))
        
        # Configure tags for color coding
        self.matches_tree.tag_configure('excellent', background='#90EE90')
        self.matches_tree.tag_configure('good', background='#ADD8E6')
        self.matches_tree.tag_configure('fair', background='#FFFFE0')
        self.matches_tree.tag_configure('low', background='#FFE4E1')
        
        # Update summary
        summary = f"Enhanced Job Search Results\n"
        summary += f"=" * 40 + "\n"
        summary += f"Total Jobs Found: {len(results)}\n"
        summary += f"Location: {self.location.get()}\n"
        summary += f"Experience Level: {self.experience_level.get()}\n"
        summary += f"Time Posted: {self.time_posted.get()}\n"
        summary += f"Minimum Match: {self.min_match.get()}%\n"
        summary += f"\nMatch Distribution:\n"
        
        # Calculate distribution
        excellent = sum(1 for j in results if j.get('match_score', 0) >= 80)
        good = sum(1 for j in results if 70 <= j.get('match_score', 0) < 80)
        fair = sum(1 for j in results if 60 <= j.get('match_score', 0) < 70)
        low = sum(1 for j in results if 50 <= j.get('match_score', 0) < 60)
        
        summary += f"  • Excellent (≥80%): {excellent} jobs\n"
        summary += f"  • Good (70-79%): {good} jobs\n"
        summary += f"  • Fair (60-69%): {fair} jobs\n"
        summary += f"  • Low (50-59%): {low} jobs\n"
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state=tk.DISABLED)
        
        self.update_status(f"Search completed - {len(results)} jobs found (≥{self.min_match.get()}% match)")
        
        # Switch to results tab
        self.notebook.select(1)
        
        # Show success message
        messagebox.showinfo("Search Complete", 
                          f"Found {len(results)} matching jobs!\n\n"
                          f"Excellent matches: {excellent}\n"
                          f"Good matches: {good}\n\n"
                          f"Results saved to:\n{self.output_dir.get()}")
    
    def view_job_details(self, event):
        """View details of selected job"""
        selection = self.matches_tree.selection()
        if selection:
            item = self.matches_tree.item(selection[0])
            values = item['values']
            
            details = f"Job Details\n"
            details += "=" * 40 + "\n"
            details += f"Match Score: {values[0]}\n"
            details += f"Title: {values[1]}\n"
            details += f"Company: {values[2]}\n"
            details += f"Location: {values[3]}\n"
            details += f"Posted: {values[4]}\n"
            details += f"Platform: {values[5]}\n"
            
            messagebox.showinfo("Job Details", details)
    
    def export_to_excel(self):
        """Export results to Excel"""
        messagebox.showinfo("Export", f"Results exported to:\n{self.output_dir.get()}/job_matches_enhanced.csv")
    
    def export_to_json(self):
        """Export results to JSON"""
        messagebox.showinfo("Export", f"Results exported to:\n{self.output_dir.get()}/job_matches_enhanced.jsonl")
    
    def stop_search(self):
        """Stop the current search"""
        if self.is_searching:
            self.is_searching = False
            self.update_status("Search stopped by user")
        
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
    
    def open_results_folder(self):
        """Open the results folder"""
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
    
    def search_error(self, error_msg):
        """Handle search error"""
        self.is_searching = False
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.update_status("Search failed")
        messagebox.showerror("Search Error", error_msg)

def main():
    """Main function to run the improved GUI"""
    try:
        root = tk.Tk()
        app = ImprovedJobFinderGUI(root)
        
        # Try to set window icon
        try:
            root.iconbitmap("icon.ico")
        except:
            pass
        
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Startup Error", f"Failed to start Job Finder Pro 2.0:\n{str(e)}")

if __name__ == "__main__":
    main()