# Job Finder Pro - Web Edition 🌐

> **Clean Web Version**: All Windows-specific files have been removed. This is now a pure web application.

## Overview
Your Windows desktop job finder application has been successfully converted to a modern web-based application! This maintains all the powerful job searching and matching capabilities while providing a responsive web interface accessible from any device.

## 🚀 Quick Start

### Option 1: Local Development
```bash
# Install dependencies
pip install -r requirements_web.txt

# Run the application
python run_web_app.py
```

### Option 2: Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t jobfinder-web .
docker run -p 5000:5000 jobfinder-web
```

The web application will be available at: **http://localhost:5000**

## 🎯 Features

### Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Bootstrap 5 with custom styling and animations
- **Real-time Updates**: WebSocket connection for live search progress
- **File Upload**: Drag & drop or browse for resume files
- **Multiple Formats**: Support for .txt, .md, .docx resume files

### Job Search Capabilities
- **Multi-Platform Search**: LinkedIn, Glassdoor, Pracuj.pl, Google Jobs
- **AI-Powered Matching**: Smart resume analysis and job scoring
- **Location Flexibility**: Search across Polish cities or remote jobs
- **Customizable Filters**: Match percentage, job age, remote inclusion
- **Advanced LinkedIn Scraping**: Enhanced scraper with fallback options

### Results & Export
- **Interactive Results Table**: Sortable, filterable job listings
- **Match Scoring**: Visual indicators for job compatibility
- **Export Options**: Download results as CSV or JSON
- **Detailed Job Info**: Company, location, match score, direct links

## 📁 Project Structure

```
job-finder/
├── web_app.py              # Main Flask application
├── run_web_app.py          # Easy launcher script
├── templates/
│   └── index.html          # Web interface
├── static/                 # CSS, JS, images (auto-created)
├── uploads/                # Temporary resume storage
├── results/                # Search results output
├── job_search.db           # SQLite database
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Docker orchestration
├── requirements_web.txt    # Web app dependencies
└── job_search_automation/  # Original Python modules (reused)
    ├── config/
    ├── scrapers/
    ├── matchers/
    ├── utils/
    └── outputs/
```

## 🔧 Configuration

The web application reuses your existing configuration from `job_search_automation/config/settings.py` but allows runtime customization through the web interface:

- **Search Location**: Poland, Warsaw, Krakow, etc.
- **Match Threshold**: 50-95% minimum match score
- **Job Age Filter**: 1-30 days maximum age
- **Remote Jobs**: Include/exclude remote positions
- **LinkedIn Scraper**: Basic or enhanced scraping method

## 🌐 Web API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main application interface |
| POST | `/api/upload_resume` | Upload resume file or text |
| POST | `/api/start_search` | Start job search process |
| GET | `/api/search_status/<id>` | Check search progress |
| GET | `/api/results/<id>` | Retrieve search results |
| GET | `/api/download/<id>/<type>` | Download CSV/JSON files |

## 🔌 WebSocket Events

- `connect` - Client connects to server
- `join_session` - Join search session for updates
- `log_message` - Real-time search progress logs
- `search_completed` - Search finished successfully
- `search_error` - Search encountered an error

## 🚀 Deployment Options

### Local Development
Perfect for personal use or testing:
```bash
python run_web_app.py
```

### Docker Container
Ideal for consistent deployment:
```bash
docker-compose up -d
```

### Cloud Deployment
Deploy to cloud platforms:
- **Heroku**: Use `Dockerfile` with Heroku CLI
- **AWS ECS**: Container service deployment
- **Digital Ocean**: App Platform or Droplet
- **Google Cloud**: Cloud Run or Compute Engine

## 🔒 Security Features

- **Session Management**: Unique session IDs for each search
- **File Validation**: Secure file upload with type checking
- **Database Storage**: SQLite for local data persistence
- **CORS Protection**: Configured WebSocket security
- **Input Sanitization**: Secure file naming and content handling

## 📊 Database Schema

The application uses SQLite with two main tables:

### search_sessions
- `id` - Unique session identifier
- `created_at` - Search start timestamp
- `status` - pending/running/completed/failed
- `location` - Search location
- `min_match` - Minimum match percentage
- `max_age_days` - Maximum job age filter
- `include_remote` - Remote jobs inclusion flag
- `total_jobs` - Number of jobs found
- `results_file` - Path to results CSV

### job_results
- `session_id` - Link to search session
- `job_title` - Position title
- `company` - Company name
- `location` - Job location
- `platform` - Source platform (LinkedIn, etc.)
- `match_score` - Compatibility score
- `job_url` - Direct application link
- `posted_date` - When job was posted
- `description` - Job description

## 🛠 Customization

### Frontend Styling
Modify `templates/index.html` to customize:
- Colors and branding
- Layout and components  
- Additional form fields
- Results display format

### Backend Logic
Extend `web_app.py` to add:
- New API endpoints
- Additional job platforms
- Custom matching algorithms
- Database enhancements

### Search Parameters
Update the web form to include:
- Industry filters
- Salary range inputs
- Experience level settings
- Custom keyword lists

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

**Missing Dependencies**
```bash
pip install -r requirements_web.txt
```

**Permission Errors**
```bash
# Ensure directories are writable
chmod 755 uploads results
```

**Chrome/ChromeDriver Issues**
```bash
# Update ChromeDriver for Selenium
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
```

### Debug Mode
Enable debug logging by setting:
```python
app.run(debug=True)
```

## 📈 Performance Tips

1. **Database Optimization**: Regular cleanup of old sessions
2. **File Management**: Automatic cleanup of uploaded resumes
3. **Memory Usage**: Limit concurrent searches
4. **Caching**: Implement Redis for session storage
5. **Load Balancing**: Use nginx for production deployments

## 🔄 Migration from Windows App

Your existing resume files and configuration will work seamlessly:

1. **Resume Files**: Upload via web interface or place in `uploads/`
2. **Configuration**: Settings automatically applied from `config/settings.py`
3. **Output Format**: Same CSV/JSON structure as desktop version
4. **Search Logic**: Identical matching algorithms and scrapers

## 📞 Support

For issues with the web application:
1. Check the browser console for JavaScript errors
2. Review Flask logs for backend issues
3. Verify all dependencies are installed
4. Test with the original desktop version first

The web application maintains full compatibility with your existing job search automation while providing a modern, accessible interface for users on any device!

---

**🎉 Your Windows desktop app is now a powerful web application! 🎉**