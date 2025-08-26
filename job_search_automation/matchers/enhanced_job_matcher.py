"""
Enhanced Job Matcher with weighted scoring system
- 60% weight from resume content
- 40% weight from user-provided data (skills + experience level)
"""

import re
from typing import Dict, List, Set, Tuple
from datetime import datetime, timedelta
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class EnhancedJobMatcher:
    def __init__(self, resume_profile: Dict, user_skills: List[str] = None, user_experience: int = 0):
        """
        Initialize enhanced matcher with resume profile and user-provided data
        
        Args:
            resume_profile: Parsed resume data
            user_skills: List of skills provided by user
            user_experience: Years of experience from user selection
        """
        self.resume_profile = resume_profile
        self.user_skills = set([s.lower().strip() for s in (user_skills or [])])
        self.user_experience = user_experience
        
        # Extract resume data
        self.resume_keywords = resume_profile.get('keywords', set())
        self.resume_skills = set([s.lower() for s in resume_profile.get('skills', [])])
        self.resume_experience = resume_profile.get('experience_years', 0)
        self.target_roles = [r.lower() for r in resume_profile.get('target_roles', [])]
        
        # Combine skills for comprehensive matching
        self.all_skills = self.resume_skills.union(self.user_skills)
        
        try:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
        
        # Weight distribution
        self.weights = {
            'resume': {
                'keywords': 0.15,      # 15% of 60% = 9% total
                'title': 0.15,         # 15% of 60% = 9% total
                'skills': 0.20,        # 20% of 60% = 12% total
                'tfidf': 0.10,         # 10% of 60% = 6% total
                'total': 0.60          # 60% total weight
            },
            'user': {
                'skills': 0.25,        # 25% of 40% = 10% total
                'experience': 0.15,    # 15% of 40% = 6% total
                'total': 0.40          # 40% total weight
            }
        }
    
    def calculate_enhanced_match_score(self, job: Dict) -> Tuple[float, Dict]:
        """
        Calculate match score with enhanced algorithm
        
        Returns:
            Tuple of (match_score, details_dict)
        """
        job_title = job.get('job_title', '').lower()
        job_description = job.get('description', '').lower()
        required_experience = job.get('required_experience', 0)
        job_skills = self._extract_job_skills(job_description)
        
        # RESUME-BASED SCORING (60% weight)
        resume_scores = {}
        
        # 1. Resume keyword matching
        resume_scores['keywords'] = self._calculate_keyword_match(job_description, self.resume_keywords)
        
        # 2. Resume title matching
        resume_scores['title'] = self._calculate_title_match(job_title, self.target_roles)
        
        # 3. Resume skills matching
        resume_skill_matches = self._find_skill_matches(job_skills, self.resume_skills)
        resume_scores['skills'] = len(resume_skill_matches) / max(len(self.resume_skills), 1) * 100
        
        # 4. Resume TF-IDF similarity
        resume_scores['tfidf'] = self._calculate_tfidf_similarity(
            job_description, 
            self.resume_keywords, 
            self.resume_skills,
            self.target_roles
        )
        
        # USER-PROVIDED DATA SCORING (40% weight)
        user_scores = {}
        
        # 1. User skills matching (25% of 40%)
        if self.user_skills:
            user_skill_matches = self._find_skill_matches(job_skills, self.user_skills)
            user_scores['skills'] = len(user_skill_matches) / max(len(self.user_skills), 1) * 100
        else:
            user_scores['skills'] = 0
        
        # 2. User experience matching (15% of 40%)
        user_scores['experience'] = self._calculate_experience_match(
            required_experience, 
            self.user_experience
        )
        
        # Calculate weighted final score
        resume_weighted_score = (
            resume_scores['keywords'] * self.weights['resume']['keywords'] +
            resume_scores['title'] * self.weights['resume']['title'] +
            resume_scores['skills'] * self.weights['resume']['skills'] +
            resume_scores['tfidf'] * self.weights['resume']['tfidf']
        )
        
        user_weighted_score = (
            user_scores['skills'] * self.weights['user']['skills'] +
            user_scores['experience'] * self.weights['user']['experience']
        )
        
        # Final score with 60% resume, 40% user data
        final_score = resume_weighted_score + user_weighted_score
        
        # Prepare detailed results
        details = {
            'resume_score': resume_weighted_score / self.weights['resume']['total'] * 100,
            'user_score': user_weighted_score / self.weights['user']['total'] * 100,
            'final_score': min(100, final_score),
            'matching_resume_skills': resume_skill_matches,
            'matching_user_skills': user_skill_matches if self.user_skills else [],
            'all_matching_skills': list(set(resume_skill_matches + (user_skill_matches if self.user_skills else []))),
            'breakdown': {
                'resume': resume_scores,
                'user': user_scores
            }
        }
        
        return min(100, final_score), details
    
    def _calculate_keyword_match(self, job_description: str, keywords: Set[str]) -> float:
        """Calculate keyword matching score"""
        if not keywords:
            return 0
        
        matches = 0
        for keyword in keywords:
            if keyword.lower() in job_description:
                matches += 1
        
        return (matches / len(keywords)) * 100
    
    def _calculate_title_match(self, job_title: str, target_roles: List[str]) -> float:
        """Calculate job title matching score"""
        if not target_roles:
            return 50  # Neutral score if no target roles specified
        
        max_score = 0
        for target_role in target_roles:
            # Word-level matching
            role_words = set(target_role.split())
            title_words = set(job_title.split())
            
            if role_words & title_words:
                overlap = len(role_words & title_words) / len(role_words)
                max_score = max(max_score, overlap * 100)
            
            # Substring matching
            if target_role in job_title or job_title in target_role:
                max_score = max(max_score, 85)
            
            # Partial matching for similar roles
            similarity_map = {
                'engineer': ['developer', 'specialist', 'analyst'],
                'developer': ['engineer', 'programmer', 'coder'],
                'manager': ['lead', 'supervisor', 'coordinator'],
                'analyst': ['specialist', 'engineer', 'scientist'],
                'senior': ['lead', 'principal', 'staff'],
                'junior': ['entry', 'graduate', 'associate']
            }
            
            for key, similar_terms in similarity_map.items():
                if key in target_role:
                    for term in similar_terms:
                        if term in job_title:
                            max_score = max(max_score, 70)
        
        return max_score
    
    def _calculate_experience_match(self, required_exp: float, user_exp: float) -> float:
        """Calculate experience matching score"""
        if required_exp == 0:
            return 100  # No requirement means perfect match
        
        exp_diff = user_exp - required_exp
        
        if exp_diff >= 0:
            # User has enough or more experience
            return 100
        elif exp_diff >= -1:
            # Within 1 year
            return 85
        elif exp_diff >= -2:
            # Within 2 years
            return 70
        elif exp_diff >= -3:
            # Within 3 years
            return 55
        else:
            # More than 3 years gap
            return max(0, 40 - abs(exp_diff) * 5)
    
    def _extract_job_skills(self, job_description: str) -> Set[str]:
        """Extract skills from job description"""
        skills = set()
        
        # Comprehensive skill list
        tech_skills = [
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "swift",
            "kotlin", "scala", "r", "matlab", "php", "perl", "objective-c", "dart", "lua", "bash",
            
            # Web Technologies
            "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask",
            "spring", "rails", "laravel", "asp.net", "jquery", "bootstrap", "sass", "webpack",
            
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "oracle", "redis", "cassandra", "dynamodb",
            "elasticsearch", "firebase", "neo4j", "sqlite", "mariadb",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab", "github", "git",
            "terraform", "ansible", "puppet", "chef", "circleci", "travis", "bamboo",
            
            # Data Science & AI
            "machine learning", "deep learning", "tensorflow", "pytorch", "keras", "scikit-learn",
            "pandas", "numpy", "data analysis", "statistics", "nlp", "computer vision",
            "artificial intelligence", "neural networks", "data mining", "big data",
            
            # Engineering Software
            "autocad", "solidworks", "catia", "ansys", "matlab", "simulink", "revit", "inventor",
            "creo", "nx", "abaqus", "comsol", "fluent", "star-ccm+", "labview",
            
            # Business Tools
            "excel", "powerpoint", "word", "outlook", "sharepoint", "teams", "slack", "jira",
            "confluence", "salesforce", "sap", "oracle", "tableau", "power bi", "qlik",
            
            # Methodologies
            "agile", "scrum", "kanban", "waterfall", "lean", "six sigma", "devops", "ci/cd",
            "tdd", "bdd", "microservices", "rest", "graphql", "soap",
            
            # Soft Skills
            "leadership", "communication", "teamwork", "problem solving", "analytical",
            "project management", "time management", "critical thinking", "creativity",
            "attention to detail", "collaboration", "presentation", "negotiation"
        ]
        
        # Check for each skill in description
        for skill in tech_skills:
            if skill in job_description:
                skills.add(skill)
        
        # Extract skills using patterns
        skill_patterns = [
            r'\b(?:proficient|experienced|knowledge|skills?|expertise)\s+(?:in|with)\s+([^,.;]+)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:experience|knowledge|skills?)',
            r'(?:technologies|tools|software|frameworks?):\s*([^.;]+)',
            r'(?:required|preferred)\s+(?:skills?|qualifications?):\s*([^.;]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            for match in matches:
                extracted = match.strip().lower()
                if len(extracted) < 50:  # Avoid long phrases
                    # Split by common delimiters
                    for delimiter in [',', 'and', 'or', '/']:
                        parts = extracted.split(delimiter)
                        for part in parts:
                            clean_skill = part.strip()
                            if 2 < len(clean_skill) < 30:
                                skills.add(clean_skill)
        
        return skills
    
    def _find_skill_matches(self, job_skills: Set[str], candidate_skills: Set[str]) -> List[str]:
        """Find matching skills between job and candidate"""
        matches = []
        
        for candidate_skill in candidate_skills:
            for job_skill in job_skills:
                # Exact match
                if candidate_skill == job_skill:
                    matches.append(candidate_skill)
                    break
                # Substring match
                elif len(candidate_skill) > 3 and (
                    candidate_skill in job_skill or job_skill in candidate_skill
                ):
                    matches.append(candidate_skill)
                    break
                # Similarity matching for common variations
                elif self._are_skills_similar(candidate_skill, job_skill):
                    matches.append(candidate_skill)
                    break
        
        return list(set(matches))
    
    def _are_skills_similar(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are similar/equivalent"""
        equivalents = {
            'js': 'javascript',
            'ts': 'typescript',
            'node': 'node.js',
            'nodejs': 'node.js',
            'react.js': 'react',
            'vue.js': 'vue',
            'angular.js': 'angular',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'dl': 'deep learning',
            'nlp': 'natural language processing',
            'k8s': 'kubernetes',
            'ci/cd': 'cicd',
            'nosql': 'mongodb',
            'rdbms': 'sql'
        }
        
        # Normalize skills
        s1 = skill1.lower().replace('-', '').replace('_', '').replace('.', '')
        s2 = skill2.lower().replace('-', '').replace('_', '').replace('.', '')
        
        # Direct normalized match
        if s1 == s2:
            return True
        
        # Check equivalents
        for key, value in equivalents.items():
            if (key in s1 and value in s2) or (key in s2 and value in s1):
                return True
        
        return False
    
    def _calculate_tfidf_similarity(self, job_description: str, keywords: Set, 
                                   skills: Set, roles: List) -> float:
        """Calculate TF-IDF similarity between resume and job description"""
        try:
            # Combine resume elements
            resume_text = ' '.join([
                ' '.join(keywords) if keywords else '',
                ' '.join(skills) if skills else '',
                ' '.join(roles) if roles else ''
            ]).strip()
            
            if not resume_text or not job_description.strip():
                return 0
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                stop_words='english', 
                max_features=200,
                ngram_range=(1, 2)  # Include bigrams
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity * 100
        except:
            return 0
    
    def extract_experience_requirement(self, job_description: str) -> float:
        """Extract years of experience requirement from job description"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\s*-\s*(\d+)\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'(\d+)\s*years?\s*minimum',
            r'requires?\s*(\d+)\s*years?'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    # For range patterns, take the minimum
                    return float(matches[0][0])
                else:
                    return float(matches[0])
        
        # Check for level indicators
        if any(term in job_description.lower() for term in 
               ['entry level', 'junior', 'graduate', 'intern', 'trainee', 'fresher']):
            return 0
        elif any(term in job_description.lower() for term in 
                 ['senior', 'lead', 'principal', 'staff', 'expert']):
            return 5
        elif any(term in job_description.lower() for term in 
                 ['mid-level', 'intermediate', 'mid-senior']):
            return 3
        
        return 0
    
    def is_job_recent(self, posted_date: str, max_days: int = 14) -> bool:
        """Check if job posting is within the specified time range"""
        try:
            posted_lower = posted_date.lower()
            
            # Handle relative time strings
            if any(term in posted_lower for term in ['today', 'just now', 'now', 'moments ago']):
                return True
            elif 'yesterday' in posted_lower:
                return max_days >= 1
            elif 'hour' in posted_lower:
                hours_match = re.search(r'(\d+)\s*hours?', posted_lower)
                if hours_match:
                    hours_ago = int(hours_match.group(1))
                    return hours_ago <= max_days * 24
                return True
            elif 'day' in posted_lower:
                days_match = re.search(r'(\d+)\s*days?', posted_lower)
                if days_match:
                    days_ago = int(days_match.group(1))
                    return days_ago <= max_days
                return max_days >= 1
            elif 'week' in posted_lower:
                weeks_match = re.search(r'(\d+)\s*weeks?', posted_lower)
                if weeks_match:
                    weeks_ago = int(weeks_match.group(1))
                    return weeks_ago * 7 <= max_days
                return max_days >= 7
            elif 'month' in posted_lower:
                months_match = re.search(r'(\d+)\s*months?', posted_lower)
                if months_match:
                    months_ago = int(months_match.group(1))
                    return months_ago * 30 <= max_days
                return max_days >= 30
            
            # Try to parse as date
            from dateutil import parser
            job_date = parser.parse(posted_date)
            cutoff_date = datetime.now() - timedelta(days=max_days)
            return job_date >= cutoff_date
        except:
            # If we can't parse, assume it's recent
            return True