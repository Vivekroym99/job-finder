#!/usr/bin/env python3
"""
Web-based Job Finder Application
Flask API backend for job search automation
"""

import os
import sys
import json
import sqlite3
import logging
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file, session
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
import uuid

# Add the job_search_automation directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'job_search_automation'))

from config.settings import Config
from main import JobSearchAutomation
from utils.resume_parser import ResumeParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('WebJobFinder')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'

# Create required directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Database setup
def init_db():
    """Initialize SQLite database for storing search results and user sessions"""
    conn = sqlite3.connect('job_search.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            location TEXT,
            min_match INTEGER,
            max_age_days INTEGER,
            include_remote BOOLEAN,
            total_jobs INTEGER DEFAULT 0,
            results_file TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            job_title TEXT,
            company TEXT,
            location TEXT,
            platform TEXT,
            match_score INTEGER,
            job_url TEXT,
            posted_date TEXT,
            description TEXT,
            FOREIGN KEY (session_id) REFERENCES search_sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

class WebJobSearchLogger:
    """Custom logger that emits messages via WebSocket"""
    def __init__(self, session_id):
        self.session_id = session_id
    
    def info(self, message):
        logger.info(f"[{self.session_id}] {message}")
        socketio.emit('log_message', {
            'message': message,
            'level': 'info',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }, room=self.session_id)
    
    def error(self, message):
        logger.error(f"[{self.session_id}] {message}")
        socketio.emit('log_message', {
            'message': message,
            'level': 'error',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }, room=self.session_id)
    
    def warning(self, message):
        logger.warning(f"[{self.session_id}] {message}")
        socketio.emit('log_message', {
            'message': message,
            'level': 'warning',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }, room=self.session_id)

# Store active search threads
active_searches = {}

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    """Handle resume file upload"""
    try:
        if 'resume' in request.files:
            file = request.files['resume']
            if file.filename != '':
                filename = secure_filename(file.filename)
                session_id = str(uuid.uuid4())
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
                file.save(file_path)
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'filename': filename,
                    'file_path': file_path
                })
        
        # Handle text resume
        if 'resume_text' in request.json:
            session_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_resume.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(request.json['resume_text'])
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'filename': 'resume.txt',
                'file_path': file_path
            })
        
        return jsonify({'success': False, 'error': 'No resume provided'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start_search', methods=['POST'])
def start_search():
    """Start job search process"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id or session_id in active_searches:
            return jsonify({'success': False, 'error': 'Invalid or busy session'})
        
        # Store search parameters in database
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_sessions (id, location, min_match, max_age_days, include_remote)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            data.get('location', 'Poland'),
            data.get('min_match', 70),
            data.get('max_age_days', 14),
            data.get('include_remote', True)
        ))
        
        conn.commit()
        conn.close()
        
        # Start search in background thread
        search_thread = threading.Thread(
            target=run_job_search,
            args=(session_id, data)
        )
        search_thread.daemon = True
        search_thread.start()
        
        active_searches[session_id] = search_thread
        
        return jsonify({'success': True, 'message': 'Search started'})
    
    except Exception as e:
        logger.error(f"Error starting search: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def run_job_search(session_id, search_params):
    """Run the actual job search process"""
    web_logger = WebJobSearchLogger(session_id)
    
    try:
        web_logger.info("🚀 Starting Job Search Automation...")
        
        # Update status to running
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE search_sessions SET status = ? WHERE id = ?', ('running', session_id))
        conn.commit()
        conn.close()
        
        # Configure job search
        config = Config()
        resume_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_resume.txt")
        
        # Find the actual resume file
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            if file.startswith(session_id):
                resume_file = os.path.join(app.config['UPLOAD_FOLDER'], file)
                break
        
        config.RESUME_FILE = resume_file
        config.SEARCH_LOCATION = search_params.get('location', 'Poland')
        config.MIN_MATCH_PCT = search_params.get('min_match', 70)
        config.MAX_JOB_AGE_DAYS = search_params.get('max_age_days', 14)
        config.INCLUDE_REMOTE = search_params.get('include_remote', True)
        config.USE_BASIC_LINKEDIN = search_params.get('use_basic_linkedin', False)
        
        # Set output directory
        results_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id)
        os.makedirs(results_dir, exist_ok=True)
        config.OUTPUT_DIR = results_dir
        config.CSV_OUTPUT = os.path.join(results_dir, "job_matches.csv")
        config.JSONL_OUTPUT = os.path.join(results_dir, "job_matches.jsonl")
        config.AUDIT_LOG = os.path.join(results_dir, "job_search_audit.log")
        
        web_logger.info(f"📍 Location: {config.SEARCH_LOCATION}")
        web_logger.info(f"🎯 Min Match: {config.MIN_MATCH_PCT}%")
        web_logger.info(f"📅 Max Age: {config.MAX_JOB_AGE_DAYS} days")
        
        # Initialize and run automation
        automation = JobSearchAutomation(config)
        
        # Monkey patch the logger to use our WebSocket logger
        automation.logger = web_logger
        for scraper_name, scraper in automation.scrapers.items():
            if hasattr(scraper, 'logger'):
                scraper.logger = web_logger
        
        web_logger.info("🔍 Searching LinkedIn, Glassdoor, Pracuj.pl, and Google Jobs...")
        
        # Run the search
        results = automation.run()
        
        # Store results in database
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        
        for job in results:
            cursor.execute('''
                INSERT INTO job_results (session_id, job_title, company, location, platform, 
                                       match_score, job_url, posted_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                job.get('job_title', ''),
                job.get('company', ''),
                job.get('location', ''),
                job.get('platform', ''),
                job.get('match_score', 0),
                job.get('job_url', ''),
                job.get('posted_date', ''),
                job.get('description', '')
            ))
        
        # Update session with results
        cursor.execute('''
            UPDATE search_sessions 
            SET status = ?, total_jobs = ?, results_file = ?
            WHERE id = ?
        ''', ('completed', len(results), config.CSV_OUTPUT, session_id))
        
        conn.commit()
        conn.close()
        
        web_logger.info(f"✅ Search completed! Found {len(results)} matching jobs")
        
        # Emit completion event
        socketio.emit('search_completed', {
            'session_id': session_id,
            'job_count': len(results),
            'csv_file': config.CSV_OUTPUT,
            'jsonl_file': config.JSONL_OUTPUT
        }, room=session_id)
        
    except Exception as e:
        web_logger.error(f"Search failed: {str(e)}")
        
        # Update status to failed
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE search_sessions SET status = ? WHERE id = ?', ('failed', session_id))
        conn.commit()
        conn.close()
        
        socketio.emit('search_error', {
            'session_id': session_id,
            'error': str(e)
        }, room=session_id)
    
    finally:
        # Remove from active searches
        if session_id in active_searches:
            del active_searches[session_id]

@app.route('/api/search_status/<session_id>')
def search_status(session_id):
    """Get current search status"""
    try:
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT status, total_jobs FROM search_sessions WHERE id = ?', (session_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'success': True,
                'status': result[0],
                'total_jobs': result[1]
            })
        else:
            return jsonify({'success': False, 'error': 'Session not found'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/results/<session_id>')
def get_results(session_id):
    """Get search results for a session"""
    try:
        conn = sqlite3.connect('job_search.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT job_title, company, location, platform, match_score, 
                   job_url, posted_date, description 
            FROM job_results 
            WHERE session_id = ? 
            ORDER BY match_score DESC
        ''', (session_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in results:
            jobs.append({
                'job_title': row[0],
                'company': row[1],
                'location': row[2],
                'platform': row[3],
                'match_score': row[4],
                'job_url': row[5],
                'posted_date': row[6],
                'description': row[7]
            })
        
        return jsonify({'success': True, 'jobs': jobs})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download/<session_id>/<file_type>')
def download_results(session_id, file_type):
    """Download results file (csv or jsonl)"""
    try:
        results_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id)
        
        if file_type == 'csv':
            file_path = os.path.join(results_dir, 'job_matches.csv')
            mimetype = 'text/csv'
            as_attachment = True
            filename = f'job_matches_{session_id}.csv'
        elif file_type == 'jsonl':
            file_path = os.path.join(results_dir, 'job_matches.jsonl')
            mimetype = 'application/json'
            as_attachment = True
            filename = f'job_matches_{session_id}.jsonl'
        else:
            return jsonify({'error': 'Invalid file type'})
        
        if os.path.exists(file_path):
            return send_file(file_path, mimetype=mimetype, as_attachment=as_attachment, 
                           download_name=filename)
        else:
            return jsonify({'error': 'File not found'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'message': 'Connected to Job Finder WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('join_session')
def handle_join_session(data):
    """Join a search session room for real-time updates"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('joined_session', {'session_id': session_id})

if __name__ == '__main__':
    logger.info("Starting Job Finder Web Application...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)