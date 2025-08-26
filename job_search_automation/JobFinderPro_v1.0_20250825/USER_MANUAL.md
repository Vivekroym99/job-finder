# 📋 Job Finder Pro - User Manual

## 🎯 What is Job Finder Pro?

**Job Finder Pro** is an intelligent Windows desktop application that automates job searching across multiple platforms and matches jobs to your resume using AI-powered analysis.

### ✨ Key Features:
- 🔍 **Multi-Platform Search**: LinkedIn, Glassdoor, Pracuj.pl, Google Jobs
- 🤖 **AI Resume Matching**: Intelligent job-to-resume matching with scoring
- 🇵🇱 **Poland-Focused**: Optimized for Polish job market with major city coverage
- 📊 **Excel Output**: Professional spreadsheet reports with job matches
- 🚀 **Advanced Scraping**: Enterprise-grade LinkedIn scraping with fallback protection

---

## 🚀 Quick Start Guide

### Step 1: Launch the Application
- **Option A**: Double-click `JobFinderPro.bat`
- **Option B**: Run `python run_job_finder_gui.py`
- **Option C**: Use the built executable `JobFinderPro.exe`

### Step 2: Add Your Resume
1. Click **"📋 Paste Resume Text"** button
2. Paste your resume content in the dialog
3. Click **"Save Resume"**

*Alternative: Use **"📁 Load from File"** to load from a text/Word file*

### Step 3: Configure Search Settings
- **Location**: Choose from Poland, Warsaw, Krakow, etc.
- **Min Match %**: Set minimum job match percentage (70% recommended)
- **Max Age**: Set maximum job posting age (14 days recommended)
- **Include Remote**: Enable/disable remote job searches
- **Output Folder**: Choose where to save results (default: Desktop/JobSearchResults)

### Step 4: Start Search
1. Click **"🚀 Start Job Search"**
2. Wait 2-5 minutes for completion
3. View results in the generated Excel file

---

## 🖥️ Application Interface

### 📑 Tab 1: Resume & Settings

#### Resume Section:
- **Load from File**: Import resume from .txt, .md, or .docx files
- **Paste Resume Text**: Manually input resume content
- **Preview Area**: Shows loaded resume content for verification

#### Search Settings:
- **Location**: Target job location
  - `Poland` - Searches all major Polish cities
  - `Warsaw` - Focuses on Warsaw area + remote
  - `Krakow` - Focuses on Krakow area + remote
  - `Remote Poland` - Remote jobs only
  
- **Min Match %**: Minimum match score to include jobs (50-95%)
  - `70%+` - High-quality matches only
  - `60-69%` - Good matches with broader coverage
  - `50-59%` - Includes more experimental matches

- **Max Age (days)**: Maximum age of job postings (1-30 days)
  - `7 days` - Very fresh jobs only
  - `14 days` - Balanced freshness (recommended)
  - `30 days` - Maximum coverage

- **Include Remote Jobs**: Whether to include remote work positions
- **Use Basic LinkedIn Scraper**: Fallback option if advanced scraping fails

#### Output Settings:
- **Save Results To**: Directory where Excel files will be saved

### 📊 Tab 2: Search Results

#### Search Summary:
- Shows job count, search parameters, and file list
- Displays completion status and timing

#### Search Log:
- Real-time progress updates
- Platform-by-platform search status
- Error messages and debugging information

#### Generated Files:
- **job_matches.csv** - Excel-compatible spreadsheet (main output)
- **job_matches.jsonl** - Detailed JSON data for advanced users
- **job_search_audit.log** - Complete search activity log

### ℹ️ Tab 3: About
- Application information and technical details

---

## 📈 Understanding Results

### Excel Output (`job_matches.csv`)

The main output file contains these columns:

| Column | Description | Example |
|--------|-------------|---------|
| **match_pct** | Match percentage score | 87.3% |
| **job_title** | Job position title | "Mechanical Engineer" |
| **company** | Company name | "ABC Engineering" |
| **platform** | Source job board | "LinkedIn" |
| **job_url** | Direct link to job posting | https://linkedin.com/jobs/view/... |
| **skill_match** | Matching skills found | "AutoCAD;Python;HVAC" |
| **location** | Job location | "Warsaw, Poland" |
| **posted_date** | When job was posted | "2024-01-15" |

### Match Score Calculation

The AI matching algorithm considers:
- **Keywords** (25%): Resume keywords vs job description
- **Job Title** (20%): Target roles vs actual job title  
- **Experience** (15%): Years of experience alignment
- **Skills** (25%): Technical/soft skills overlap
- **Content Similarity** (15%): Overall text similarity

### Quality Indicators:
- **90%+ Match**: Excellent fit, definitely apply
- **80-89% Match**: Very good fit, strong candidate
- **70-79% Match**: Good fit, worth considering
- **60-69% Match**: Reasonable fit, review carefully
- **50-59% Match**: Marginal fit, apply selectively

---

## ⚙️ Advanced Features

### Dynamic Location Search

When you select **"Poland"**, the system automatically:
1. Searches major Polish cities individually
2. Includes country-wide job postings
3. Adds remote work opportunities
4. Deduplicates results across all sources

**City Coverage**: Warsaw, Krakow, Wroclaw, Poznan, Gdansk, Lodz, Katowice, Szczecin, Lublin, Bydgoszcz

### Multi-Strategy LinkedIn Scraping

The LinkedIn scraper uses 4 different approaches:
1. **Guest API**: LinkedIn's internal job endpoint
2. **Public Search**: Traditional job page scraping
3. **RSS Feeds**: Alternative XML data sources
4. **Basic Fallback**: Simple HTML parsing as safety net

This ensures maximum job discovery even if LinkedIn changes their anti-bot measures.

### Platform-Specific Optimizations

- **LinkedIn**: Uses advanced Luminati-based techniques with rotating headers
- **Glassdoor**: Leverages location-specific IDs for Polish regions
- **Pracuj.pl**: Native Polish language and location handling
- **Google Jobs**: Country-specific search with Polish job board aggregation

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### "No jobs found"
**Causes & Solutions:**
- Lower the minimum match percentage to 60% or 50%
- Ensure your resume contains relevant keywords for your target role
- Try a broader location like "Poland" instead of specific cities
- Check that your internet connection is working

#### "LinkedIn scraping blocked"
**Solutions:**
- Enable "Use Basic LinkedIn Scraper" in settings
- Wait 30 minutes and try again
- Use a VPN if available
- The system will automatically try other platforms

#### "Application won't start"
**Solutions:**
- Ensure Python 3.8+ is installed
- Run `pip install -r requirements.txt` to install dependencies
- Try running `python run_job_finder_gui.py` directly
- Check Windows antivirus isn't blocking the application

#### "Search takes too long"
**Expected timing:**
- Small searches (1 city): 1-2 minutes
- Large searches (all Poland): 3-5 minutes
- Very comprehensive searches: 5-10 minutes

**If stuck:**
- Click "⏹ Stop Search" and try with fewer locations
- Check the search log for error messages
- Reduce the maximum job age to speed up processing

#### "Excel file won't open"
**Solutions:**
- Ensure Microsoft Excel or LibreOffice is installed
- Try opening with a text editor first to verify content
- Check file permissions in the output directory

### Performance Optimization

#### For Faster Searches:
- Use specific cities instead of "Poland"
- Set higher minimum match percentage (80%+)
- Reduce maximum job age to 7 days
- Disable remote jobs if not needed

#### For Maximum Coverage:
- Use "Poland" location
- Set minimum match to 60%
- Enable remote jobs
- Set maximum age to 14+ days

---

## 📋 Best Practices

### Resume Optimization

**For Best Results, Your Resume Should Include:**
- Clear job titles and role descriptions
- Relevant technical skills and tools
- Years of experience information
- Education and certifications
- Industry-specific keywords

**Resume Format Tips:**
- Use standard section headers (Experience, Education, Skills)
- Include company names and job titles
- List specific technologies and tools
- Mention programming languages if applicable
- Add soft skills and domain expertise

### Search Strategy

#### For Job Seekers New to Poland:
1. Start with "Poland" location for maximum coverage
2. Use 60% minimum match for broader results
3. Enable remote jobs for more opportunities
4. Review results to understand local job market

#### For Experienced Professionals:
1. Use specific cities where you want to work
2. Set 75%+ minimum match for quality results
3. Focus on recent jobs (7-14 days)
4. Look for senior/lead positions in results

#### For Career Changers:
1. Lower minimum match to 50-60%
2. Focus on transferable skills in resume
3. Include relevant coursework or certifications
4. Consider broader location search initially

---

## 🔒 Privacy & Data

### What Data is Processed:
- Your resume content (processed locally)
- Job posting information (from public sources)
- Search preferences and settings

### What Data is NOT Collected:
- No personal data sent to external servers
- No tracking or analytics
- No account creation required
- All processing happens on your computer

### Data Storage:
- Resume temporarily saved locally during search
- Results saved to your chosen output directory
- No cloud storage or external data transmission

---

## 🆘 Support & Updates

### Getting Help:
1. Check the "Search Results" tab for detailed logs
2. Review the `job_search_audit.log` file
3. Try different search settings
4. Update Python packages: `pip install --upgrade -r requirements.txt`

### Keeping Updated:
- Download latest version from the original source
- Update Python packages periodically
- Check for new features and improvements

---

## 🏆 Success Tips

### Maximize Your Job Discovery:
1. **Keep Resume Updated**: Regularly update with new skills and experience
2. **Use Multiple Searches**: Try different locations and match percentages
3. **Monitor Regularly**: Run searches weekly to catch new postings
4. **Customize Settings**: Adjust parameters based on results quality
5. **Review All Matches**: Don't ignore lower percentage matches completely

### Application Strategy:
1. **Prioritize High Matches**: Apply to 90%+ matches first
2. **Customize Applications**: Use job description keywords in cover letters  
3. **Track Applications**: Keep spreadsheet of applications sent
4. **Follow Up**: Use the direct job URLs for easy application access
5. **Network**: Use company names to research and find connections

**Good luck with your job search! 🍀**

---

*Job Finder Pro - Making job hunting smarter and more efficient*