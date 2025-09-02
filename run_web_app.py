#!/usr/bin/env python3
"""
Simple Flask app without SocketIO to test job search functionality
"""

from flask import Flask, render_template, request, jsonify, session
import os
import sys
import json
from datetime import datetime
import uuid
import sqlite3
import threading

# Add the job search automation to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'job_search_automation'))

from config.settings import Config
from main import JobSearchAutomation

app = Flask(__name__)
app.secret_key = 'job-finder-secret-key-2025'

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Database setup
def init_db():
    """Initialize SQLite database for storing search results and user sessions"""
    conn = sqlite3.connect('job_finder.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            search_params TEXT,
            status TEXT DEFAULT 'pending',
            results_count INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            job_title TEXT,
            company TEXT,
            location TEXT,
            match_score REAL,
            platform TEXT,
            job_url TEXT,
            salary TEXT,
            posted_date TEXT,
            matched_keywords TEXT,
            original_language TEXT,
            translated BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES search_sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def start_search():
    """Start job search process"""
    try:
        data = request.get_json()
        
        # Create search session
        session_id = str(uuid.uuid4())
        
        # Map experience levels
        experience_levels = data.get('experience_levels', [])
        
        # Map to years for compatibility
        experience_mapping = {
            'intern': 0,
            'entry': 0.5,
            'junior': 1.5,
            'mid': 4,
            'senior': 8,
            'lead': 12,
            'manager': 15
        }
        
        # Calculate average experience or use highest
        if experience_levels:
            experience_years = max(experience_mapping.get(level, 0) for level in experience_levels)
            # Determine main experience level
            if 'manager' in experience_levels or 'lead' in experience_levels:
                user_experience_level = 'senior'
            elif 'senior' in experience_levels:
                user_experience_level = 'senior'
            elif 'mid' in experience_levels:
                user_experience_level = 'mid-level'
            elif 'junior' in experience_levels:
                user_experience_level = 'junior'
            else:
                user_experience_level = 'entry-level'
        else:
            experience_years = 2
            user_experience_level = 'mid-level'
        
        # Store search parameters
        search_params = {
            'keywords': data.get('keywords', ''),
            'location': data.get('location', 'Poland'),
            'experience_levels': experience_levels,
            'include_remote': data.get('include_remote', True)
        }
        
        # Save session to database
        conn = sqlite3.connect('job_finder.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO search_sessions (id, search_params, status)
            VALUES (?, ?, ?)
        ''', (session_id, json.dumps(search_params), 'running'))
        conn.commit()
        conn.close()
        
        # Run search in background
        def run_search():
            try:
                # Configure job search
                config = Config()
                config.JOB_SEARCH_KEYWORDS = [kw.strip() for kw in data.get('keywords', '').split(',')]
                config.SEARCH_LOCATION = data.get('location', 'Poland')
                config.INCLUDE_REMOTE = data.get('include_remote', True)
                config.MIN_MATCH_PCT = 60
                config.MAX_JOB_AGE_DAYS = 14
                
                # Set matcher type to description-focused
                config.MATCHER_TYPE = 'description_focused'
                config.USER_EXPERIENCE_YEARS = experience_years
                config.USER_EXPERIENCE_LEVEL = user_experience_level
                
                # Run job search
                automation = JobSearchAutomation(config)
                jobs = automation.run()
                
                # Save results to database
                conn = sqlite3.connect('job_finder.db')
                cursor = conn.cursor()
                
                for job in jobs:
                    cursor.execute('''
                        INSERT INTO job_results (
                            session_id, job_title, company, location, match_score,
                            platform, job_url, salary, posted_date, matched_keywords,
                            original_language, translated
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session_id,
                        job.get('job_title', ''),
                        job.get('company', ''),
                        job.get('location', ''),
                        job.get('match_score', 0),
                        job.get('platform', ''),
                        job.get('job_url', ''),
                        job.get('salary', ''),
                        job.get('posted_date', ''),
                        ', '.join(job.get('matched_keywords', [])),
                        job.get('original_language', 'en'),
                        job.get('translated', False)
                    ))
                
                # Update session status
                cursor.execute('''
                    UPDATE search_sessions 
                    SET status = ?, results_count = ?
                    WHERE id = ?
                ''', ('completed', len(jobs), session_id))
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                # Update session with error
                conn = sqlite3.connect('job_finder.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE search_sessions 
                    SET status = ?
                    WHERE id = ?
                ''', (f'error: {str(e)}', session_id))
                conn.commit()
                conn.close()
        
        # Start search in background thread
        thread = threading.Thread(target=run_search)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Job search started successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/status/<session_id>')
def get_status(session_id):
    """Get search status and results"""
    try:
        conn = sqlite3.connect('job_finder.db')
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT status, results_count, created_at, search_params
            FROM search_sessions 
            WHERE id = ?
        ''', (session_id,))
        
        session_info = cursor.fetchone()
        
        if not session_info:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        status, results_count, created_at, search_params = session_info
        
        # Get results if completed
        results = []
        if status == 'completed':
            cursor.execute('''
                SELECT job_title, company, location, match_score, platform,
                       job_url, salary, posted_date, matched_keywords,
                       original_language, translated
                FROM job_results
                WHERE session_id = ?
                ORDER BY match_score DESC
            ''', (session_id,))
            
            results = [{
                'job_title': row[0],
                'company': row[1], 
                'location': row[2],
                'match_score': row[3],
                'platform': row[4],
                'job_url': row[5],
                'salary': row[6],
                'posted_date': row[7],
                'matched_keywords': row[8].split(', ') if row[8] else [],
                'original_language': row[9],
                'translated': bool(row[10])
            } for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'status': status,
            'results_count': results_count or 0,
            'created_at': created_at,
            'search_params': json.loads(search_params) if search_params else {},
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Job Finder Web Application...")
    print("Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)