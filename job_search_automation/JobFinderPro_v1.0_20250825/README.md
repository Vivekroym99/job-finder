# Job Search Automation System

An intelligent job search automation tool that scrapes multiple job platforms, analyzes job postings against your resume, and ranks them by match percentage.

## Features

- **Multi-Platform Support**: Searches LinkedIn, Glassdoor, Pracuj.pl, and Google Jobs
- **Smart Matching**: Uses keyword extraction, skill matching, and experience alignment
- **Freshness Filter**: Only includes jobs posted within the last 14 days
- **Multiple Output Formats**: CSV, JSONL, and formatted console output
- **Audit Logging**: Tracks all search activities and results

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download NLTK data (first run only):
```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```

## Usage

### Basic Usage
```bash
python main.py
```

### Search All of Poland (Default)
```bash
python main.py
```

### Search Specific Cities
```bash
python main.py --location Warsaw
python main.py --location Krakow --min-match 60
python main.py --location Wroclaw --no-remote
```

### Custom Parameters
```bash
python main.py --location Poland --min-match 60 --max-age 7 --output-dir /custom/output
```

### Parameters
- `--resume`: Path to resume file (default: `/workspaces/job-finder/resume/resume.md`)
- `--location`: Search location - "Poland", "Warsaw", "Krakow", etc. (default: "Poland")
- `--radius`: Search radius in km (default: 100)
- `--no-remote`: Exclude remote jobs from search
- `--linkedin-basic`: Use basic LinkedIn scraper instead of enhanced version
- `--min-match`: Minimum match percentage (default: 70)
- `--max-age`: Maximum job age in days (default: 14)
- `--output-dir`: Output directory (default: `/tmp/job_search_results`)

## Configuration

Edit `config/settings.py` to customize:
- Resume file path
- Minimum match percentage
- Target locations
- Search keywords
- Platform settings

## Output Files

The system generates three output files:

1. **job_matches.csv**: Spreadsheet with job matches
   - Columns: match_pct, job_title, company, platform, job_url, skill_match

2. **job_matches.jsonl**: Detailed JSON Lines format with full job data

3. **job_search_audit.log**: Audit trail of all operations

## How It Works

1. **Resume Analysis**: Extracts skills, keywords, experience, and target roles from your resume
2. **Job Searching**: Scrapes configured platforms for relevant positions
3. **Matching Algorithm**: 
   - Keyword overlap analysis (25% weight)
   - Job title matching (20% weight)
   - Experience alignment (15% weight)
   - Skill matching (25% weight)
   - TF-IDF similarity (15% weight)
4. **Filtering**: Removes jobs older than 14 days and below minimum match percentage
5. **Output Generation**: Creates structured outputs and displays top matches

## Matching Score Calculation

The system calculates match scores based on:
- **Keywords**: How many resume keywords appear in the job description
- **Title Match**: Similarity between target roles and job title
- **Experience**: Whether your experience meets requirements
- **Skills**: Overlap between your skills and job requirements
- **Content Similarity**: TF-IDF based text similarity

## Dynamic Location Support

### Supported Locations:
- **Poland** (searches all major cities)
- **Warsaw** (Warszawa)
- **Krakow** (Kraków) 
- **Wroclaw** (Wrocław)
- **Poznan** (Poznań)
- **Gdansk** (Gdańsk)
- **Lodz** (Łódź)
- **Katowice**
- **Remote jobs** (optional, included by default)

### How Location Search Works:

1. **LinkedIn**: Searches multiple city variants + "Poland" + "Remote Poland"
2. **Glassdoor**: Uses location IDs for Polish cities
3. **Pracuj.pl**: Native Polish job board with Polish city names
4. **Google Jobs**: Searches with location modifiers + remote options

When you select "Poland", the system automatically searches:
- All major Polish cities individually
- Country-wide searches  
- Remote job opportunities
- Cross-references to avoid duplicates

## Platform Notes

- **LinkedIn**: Enhanced scraper with multiple approaches:
  - **Enhanced (Default)**: Uses Luminati-style techniques with LinkedIn's internal APIs
  - **Basic (Fallback)**: Traditional HTML scraping approach
  - **Auto-failover**: Falls back to basic if enhanced fails
- **Glassdoor**: Location-specific IDs for Polish regions  
- **Pracuj.pl**: Native Polish job board with salary information
- **Google Jobs**: Aggregates from multiple sources with location filtering

### LinkedIn Scraper Options

The system includes two LinkedIn scrapers:

1. **Enhanced LinkedIn Scraper (Recommended)**
   - Based on [Luminati LinkedIn Scraper](https://github.com/luminati-io/LinkedIn-Scraper)
   - Uses LinkedIn's Voyager API patterns
   - Better anti-bot protection handling
   - Multiple search strategies
   - Automatic fallback to basic scraper

2. **Basic LinkedIn Scraper**
   - Traditional HTML parsing approach
   - More reliable in restrictive environments
   - Use with `--linkedin-basic` flag

```bash
# Use enhanced scraper (default)
python main.py --location Warsaw

# Use basic scraper
python main.py --location Warsaw --linkedin-basic
```

## Troubleshooting

- If scraping fails, the system will continue with other platforms
- Check `job_search.log` for detailed error messages
- Some platforms may require additional headers or rate limiting

## Test the System

Run the test script to verify everything is working:
```bash
python test_system.py
```

## License

This tool is for personal use only. Please respect the terms of service of job platforms.