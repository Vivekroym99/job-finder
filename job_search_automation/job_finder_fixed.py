#!/usr/bin/env python3
"""
Fixed Job Finder GUI with enhanced UI and matching algorithm
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

# Import check with better error handling
JobSearchAutomation = None
Config = None
try:
    from config.settings import Config
    from main import JobSearchAutomation
    print("✅ All core modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Some features may not be available")

class JobFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Finder Pro 2.0 - Enhanced")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Variables
        self.resume_content = ""
        self.location = tk.StringVar(value="Poland")
        self.experience_level = tk.StringVar(value="Junior")
        self.time_posted = tk.StringVar(value="1 week")
        self.min_match = tk.IntVar(value=50)
        self.include_remote = tk.BooleanVar(value=True)
        self.output_dir = tk.StringVar(value=os.path.expanduser("~/Desktop/JobSearchResults"))
        
        # Search state
        self.is_searching = False
        self.search_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 Job Finder Pro 2.0 - Enhanced", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        
        # Tab 1: Search
        search_frame = ttk.Frame(notebook, padding="10")
        notebook.add(search_frame, text="🔍 Job Search")
        
        # Tab 2: Results
        results_frame = ttk.Frame(notebook, padding="10")
        notebook.add(results_frame, text="📊 Results")
        
        self.setup_search_tab(search_frame)
        self.setup_results_tab(results_frame)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.search_button = ttk.Button(button_frame, text="🚀 Start Job Search", 
                                       command=self.start_search)
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop Search", 
                                     command=self.stop_search, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📁 Open Results", 
                  command=self.open_results_folder).pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to search for jobs")
        self.status_label.grid(row=4, column=0, pady=(5, 0))
        
    def setup_search_tab(self, parent):
        """Setup the search tab with input fields"""
        
        # Make parent scrollable
        canvas = tk.Canvas(parent, height=400)
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
        
        # 1. Resume Section
        resume_frame = ttk.LabelFrame(scrollable_frame, text="📄 Resume (60% weight)", padding="10")
        resume_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        button_frame = ttk.Frame(resume_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="📋 Paste Resume", 
                  command=self.paste_resume_dialog).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📁 Load File", 
                  command=self.load_resume_file).pack(side=tk.LEFT)
        
        self.resume_preview = scrolledtext.ScrolledText(resume_frame, height=6, wrap=tk.WORD)
        self.resume_preview.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 2. Location Section
        location_frame = ttk.LabelFrame(scrollable_frame, text="📍 Location", padding="10")
        location_frame.pack(fill=tk.X, pady=(0, 10))
        
        loc_input_frame = ttk.Frame(location_frame)
        loc_input_frame.pack(fill=tk.X)
        
        ttk.Label(loc_input_frame, text="Location:").pack(side=tk.LEFT, padx=(0, 10))
        
        location_combo = ttk.Combobox(loc_input_frame, textvariable=self.location, values=[
            "Poland", "Warsaw", "Krakow", "Wroclaw", "Poznan", "Germany", "Netherlands", 
            "United Kingdom", "United States", "Remote Worldwide"
        ])
        location_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Checkbutton(loc_input_frame, text="Include Remote Jobs", 
                       variable=self.include_remote).pack(side=tk.LEFT)
        
        # 3. Experience Section
        exp_frame = ttk.LabelFrame(scrollable_frame, text="💼 Experience Level", padding="10")
        exp_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(exp_frame, text="Select your experience level:", 
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 5))
        
        exp_levels = [
            ("Internship / Entry Level", "Intern"),
            ("Junior (0-2 years)", "Junior"),
            ("Mid-level (2-5 years)", "Mid"),
            ("Senior (5-10 years)", "Senior"),
            ("Expert / Lead (10+ years)", "Expert")
        ]
        
        for text, value in exp_levels:
            ttk.Radiobutton(exp_frame, text=text, variable=self.experience_level, 
                           value=value).pack(anchor=tk.W, pady=1)
        
        # 4. Time Posted Section
        time_frame = ttk.LabelFrame(scrollable_frame, text="🕐 Job Age", padding="10")
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(time_frame, text="Show jobs posted within:", 
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 5))
        
        time_options = [
            ("Past 24 hours", "1 day"),
            ("Past week", "1 week"), 
            ("Past 2 weeks", "2 weeks"),
            ("Past month", "4 weeks"),
            ("Past 2 months", "8 weeks")
        ]
        
        for text, value in time_options:
            ttk.Radiobutton(time_frame, text=text, variable=self.time_posted, 
                           value=value).pack(anchor=tk.W, pady=1)
        
        # 5. SKILLS SECTION - This is the important one!
        skills_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Your Skills (40% weight - IMPORTANT)", padding="10")
        skills_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Instructions
        instruction_text = """Enter your key skills separated by commas. These are crucial for matching!
Example: Python, Machine Learning, SQL, AWS, Docker, JavaScript"""
        
        ttk.Label(skills_frame, text=instruction_text, 
                 font=('Arial', 9), foreground='blue', wraplength=600).pack(anchor=tk.W, pady=(0, 10))
        
        # Skills input - THIS IS THE MISSING PIECE!
        ttk.Label(skills_frame, text="Your Skills:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 5))
        
        # Create the skills input text area
        self.skills_input = scrolledtext.ScrolledText(skills_frame, height=4, wrap=tk.WORD)
        self.skills_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Add placeholder text
        placeholder_text = "Python, JavaScript, SQL, Machine Learning, Data Analysis, AWS, Docker..."
        self.skills_input.insert(1.0, placeholder_text)
        self.skills_input.bind("<FocusIn>", self.clear_placeholder)
        
        # Quick add buttons
        quick_frame = ttk.Frame(skills_frame)
        quick_frame.pack(fill=tk.X)
        
        ttk.Label(quick_frame, text="Quick add:", font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 5))
        
        skills_buttons = [
            ["Python", "JavaScript", "Java", "SQL", "React"],
            ["Machine Learning", "Data Analysis", "AWS", "Docker", "Git"],
            ["Project Management", "Leadership", "Communication", "Excel", "PowerBI"]
        ]
        
        for row in skills_buttons:
            btn_frame = ttk.Frame(quick_frame)
            btn_frame.pack(anchor=tk.W, pady=2)
            for skill in row:
                ttk.Button(btn_frame, text=f"+ {skill}", width=15,
                          command=lambda s=skill: self.add_skill(s)).pack(side=tk.LEFT, padx=2)
        
        # 6. Settings Section
        settings_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Match threshold
        match_frame = ttk.Frame(settings_frame)
        match_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(match_frame, text="Minimum Match Threshold:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Scale(match_frame, from_=50, to=90, orient=tk.HORIZONTAL, 
                 variable=self.min_match, length=200).pack(side=tk.LEFT, padx=(0, 10))
        self.threshold_label = ttk.Label(match_frame, text="50%")
        self.threshold_label.pack(side=tk.LEFT)
        
        # Update threshold label
        def update_threshold(*args):
            self.threshold_label.config(text=f"{self.min_match.get()}%")
        self.min_match.trace('w', update_threshold)
        
        # Output directory
        ttk.Label(settings_frame, text="Results will be saved to:", 
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(10, 5))
        
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X)
        
        ttk.Entry(dir_frame, textvariable=self.output_dir, width=50).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(dir_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.LEFT)
        
    def clear_placeholder(self, event):
        """Clear placeholder text when user clicks on skills field"""
        current_text = self.skills_input.get(1.0, tk.END).strip()
        if "Python, JavaScript" in current_text:  # Check if it's still placeholder
            self.skills_input.delete(1.0, tk.END)
    
    def add_skill(self, skill):
        """Add a skill to the skills input field"""
        current_text = self.skills_input.get(1.0, tk.END).strip()
        
        # Clear placeholder if present
        if "Python, JavaScript" in current_text:
            self.skills_input.delete(1.0, tk.END)
            current_text = ""
        
        if current_text and not current_text.endswith(','):
            self.skills_input.insert(tk.END, f", {skill}")
        else:
            self.skills_input.insert(tk.END, skill if not current_text else f", {skill}")
    
    def setup_results_tab(self, parent):
        """Setup the results tab"""
        # Results summary
        summary_frame = ttk.LabelFrame(parent, text="📊 Search Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.summary_text = tk.Text(summary_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.X)
        
        # Job matches table
        matches_frame = ttk.LabelFrame(parent, text="💼 Job Matches", padding="10")
        matches_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('Match %', 'Job Title', 'Company', 'Location', 'Platform')
        self.matches_tree = ttk.Treeview(matches_frame, columns=columns, show='tree headings')
        
        # Define column headings
        self.matches_tree.heading('#0', text='#')
        self.matches_tree.column('#0', width=40)
        
        for col in columns:
            self.matches_tree.heading(col, text=col)
            if col == 'Match %':
                self.matches_tree.column(col, width=80)
            elif col == 'Job Title':
                self.matches_tree.column(col, width=200)
            else:
                self.matches_tree.column(col, width=120)
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(matches_frame, orient=tk.VERTICAL, command=self.matches_tree.yview)
        self.matches_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.matches_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def paste_resume_dialog(self):
        """Open dialog to paste resume text"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Paste Resume Text")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
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
        
        ttk.Button(button_frame, text="✅ Save Resume", command=save_resume).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        text_widget.focus_set()
    
    def load_resume_file(self):
        """Load resume from file"""
        file_path = filedialog.askopenfilename(
            title="Select Resume File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
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
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_search(self):
        """Start the job search"""
        # Validate inputs
        resume_text = self.resume_preview.get(1.0, tk.END).strip()
        if not resume_text:
            messagebox.showerror("Error", "Please paste your resume or load from file!")
            return
        
        skills_text = self.skills_input.get(1.0, tk.END).strip()
        # Remove placeholder text
        if "Python, JavaScript" in skills_text:
            skills_text = ""
        
        if not skills_text:
            response = messagebox.askyesno("No Skills", 
                                          "No skills entered. Continue anyway?\n(Note: Skills contribute 40% to matching)")
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
        self.update_status("Starting job search...")
        
        # Clear previous results
        self.matches_tree.delete(*self.matches_tree.get_children())
        
        # Start search thread
        self.search_thread = threading.Thread(target=self.run_search, args=(resume_text, skills_text))
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def run_search(self, resume_text, skills_text):
        """Run the job search"""
        try:
            # Check if modules are available
            if Config is None or JobSearchAutomation is None:
                self.root.after(0, self.search_error, "Required modules not available. Please check installation.")
                return
            
            # Prepare parameters
            user_skills = [s.strip() for s in skills_text.split(',') if s.strip()] if skills_text else []
            
            print(f"🎯 Starting search with {len(user_skills)} skills: {user_skills}")
            
            # Time mapping
            time_map = {
                "1 day": 1, "1 week": 7, "2 weeks": 14, "4 weeks": 30, "8 weeks": 60
            }
            max_days = time_map.get(self.time_posted.get(), 14)
            
            # Experience mapping
            exp_map = {"Intern": 0, "Junior": 1, "Mid": 3, "Senior": 7, "Expert": 12}
            experience_years = exp_map.get(self.experience_level.get(), 1)
            
            # Save resume temporarily
            resume_path = os.path.join(self.output_dir.get(), "temp_resume.md")
            with open(resume_path, 'w', encoding='utf-8') as f:
                f.write(resume_text)
            
            # Configure search
            config = Config()
            config.RESUME_FILE = resume_path
            config.SEARCH_LOCATION = self.location.get()
            config.MIN_MATCH_PCT = self.min_match.get()
            config.MAX_JOB_AGE_DAYS = max_days
            config.INCLUDE_REMOTE = self.include_remote.get()
            config.OUTPUT_DIR = self.output_dir.get()
            config.CSV_OUTPUT = os.path.join(self.output_dir.get(), "job_matches_enhanced.csv")
            config.JSONL_OUTPUT = os.path.join(self.output_dir.get(), "job_matches_enhanced.jsonl")
            
            # Enhanced parameters
            if user_skills:
                config.USER_SKILLS = user_skills
                config.USER_EXPERIENCE = experience_years
                config.ENHANCED_MATCHING = True
                print("✅ Enhanced matching enabled")
            else:
                print("⚠️ Using standard matching (no skills provided)")
            
            # Run search
            automation = JobSearchAutomation(config)
            results = automation.run()
            
            print(f"✅ Search completed with {len(results) if results else 0} results")
            
            # Update UI
            self.root.after(0, self.display_results, results or [])
            
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.root.after(0, self.search_error, str(e))
    
    def display_results(self, results):
        """Display search results"""
        self.is_searching = False
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        
        # Sort by match score
        if results:
            results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Clear and populate tree
        self.matches_tree.delete(*self.matches_tree.get_children())
        
        for idx, job in enumerate(results, 1):
            match_score = job.get('match_score', 0)
            
            # Color coding
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
                                           job.get('job_title', 'N/A')[:50],
                                           job.get('company', 'N/A')[:30],
                                           job.get('location', 'N/A')[:30],
                                           job.get('platform', 'N/A')),
                                    tags=(tag,))
        
        # Configure colors
        self.matches_tree.tag_configure('excellent', background='#90EE90')
        self.matches_tree.tag_configure('good', background='#ADD8E6')
        self.matches_tree.tag_configure('fair', background='#FFFFE0')
        self.matches_tree.tag_configure('low', background='#FFE4E1')
        
        # Update summary
        summary = f"Enhanced Job Search Results\n"
        summary += "=" * 40 + "\n"
        summary += f"Total Jobs Found: {len(results)}\n"
        summary += f"Location: {self.location.get()}\n"
        summary += f"Experience: {self.experience_level.get()}\n"
        summary += f"Min Match: {self.min_match.get()}%\n"
        summary += f"Search completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if results:
            excellent = sum(1 for j in results if j.get('match_score', 0) >= 80)
            good = sum(1 for j in results if 70 <= j.get('match_score', 0) < 80)
            fair = sum(1 for j in results if 60 <= j.get('match_score', 0) < 70)
            low = sum(1 for j in results if 50 <= j.get('match_score', 0) < 60)
            
            summary += f"Match Distribution:\n"
            summary += f"  🟢 Excellent (≥80%): {excellent} jobs\n"
            summary += f"  🔵 Good (70-79%): {good} jobs\n"
            summary += f"  🟡 Fair (60-69%): {fair} jobs\n"
            summary += f"  🔴 Low (50-59%): {low} jobs\n"
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state=tk.DISABLED)
        
        self.update_status(f"Search completed - {len(results)} jobs found")
        
        # Show results in messagebox
        if results:
            messagebox.showinfo("Search Complete", 
                              f"Found {len(results)} matching jobs!\n\n"
                              f"Results saved to:\n{self.output_dir.get()}")
        else:
            messagebox.showinfo("No Results", 
                              "No jobs found matching your criteria.\n\n"
                              "Try:\n"
                              "• Lowering the match threshold\n"
                              "• Expanding the time range\n"
                              "• Using broader location settings")
    
    def search_error(self, error_msg):
        """Handle search error"""
        self.is_searching = False
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.update_status("Search failed")
        messagebox.showerror("Search Error", f"Search failed:\n{error_msg}")
    
    def stop_search(self):
        """Stop the search"""
        self.is_searching = False
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.update_status("Search stopped")
    
    def open_results_folder(self):
        """Open results folder"""
        output_path = self.output_dir.get()
        if os.path.exists(output_path):
            if sys.platform == "win32":
                os.startfile(output_path)
            elif sys.platform == "darwin":
                os.system(f"open '{output_path}'")
            else:
                os.system(f"xdg-open '{output_path}'")
        else:
            messagebox.showwarning("Warning", f"Directory not found:\n{output_path}")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = JobFinderGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")

if __name__ == "__main__":
    main()