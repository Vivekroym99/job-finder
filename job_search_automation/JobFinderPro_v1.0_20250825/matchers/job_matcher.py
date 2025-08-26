import re
from typing import Dict, List, Set, Tuple
from datetime import datetime, timedelta
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class JobMatcher:
    def __init__(self, resume_profile: Dict):
        self.resume_profile = resume_profile
        self.resume_keywords = resume_profile.get('keywords', set())
        self.resume_skills = set([s.lower() for s in resume_profile.get('skills', [])])
        self.resume_experience = resume_profile.get('experience_years', 0)
        self.target_roles = [r.lower() for r in resume_profile.get('target_roles', [])]
        
        try:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
    
    def calculate_match_score(self, job: Dict) -> Tuple[float, List[str]]:
        job_title = job.get('job_title', '').lower()
        job_description = job.get('description', '').lower()
        required_experience = job.get('required_experience', 0)
        job_skills = self._extract_job_skills(job_description)
        
        keyword_score = self._calculate_keyword_match(job_description)
        
        title_score = self._calculate_title_match(job_title)
        
        experience_score = self._calculate_experience_match(required_experience)
        
        skill_matches = self._find_skill_matches(job_skills)
        skill_score = len(skill_matches) / max(len(self.resume_skills), 1) * 100
        
        tfidf_score = self._calculate_tfidf_similarity(job_description)
        
        weights = {
            'keyword': 0.25,
            'title': 0.20,
            'experience': 0.15,
            'skills': 0.25,
            'tfidf': 0.15
        }
        
        final_score = (
            keyword_score * weights['keyword'] +
            title_score * weights['title'] +
            experience_score * weights['experience'] +
            skill_score * weights['skills'] +
            tfidf_score * weights['tfidf']
        )
        
        return min(100, final_score), skill_matches
    
    def _calculate_keyword_match(self, job_description: str) -> float:
        if not self.resume_keywords:
            return 0
        
        matches = 0
        for keyword in self.resume_keywords:
            if keyword in job_description:
                matches += 1
        
        return (matches / len(self.resume_keywords)) * 100
    
    def _calculate_title_match(self, job_title: str) -> float:
        if not self.target_roles:
            return 0
        
        max_score = 0
        for target_role in self.target_roles:
            role_words = set(target_role.split())
            title_words = set(job_title.split())
            
            if role_words & title_words:
                overlap = len(role_words & title_words) / len(role_words)
                max_score = max(max_score, overlap * 100)
            
            if target_role in job_title or job_title in target_role:
                max_score = max(max_score, 80)
        
        return max_score
    
    def _calculate_experience_match(self, required_experience: float) -> float:
        if required_experience == 0:
            return 100
        
        experience_diff = self.resume_experience - required_experience
        
        if experience_diff >= 0:
            return 100
        elif experience_diff >= -1:
            return 80
        elif experience_diff >= -2:
            return 60
        else:
            return max(0, 40 - abs(experience_diff) * 10)
    
    def _extract_job_skills(self, job_description: str) -> Set[str]:
        skills = set()
        
        common_skills = [
            "python", "java", "javascript", "c++", "sql", "matlab", "r",
            "autocad", "revit", "solidworks", "ansys", "catia", "inventor",
            "excel", "vba", "powerpoint", "word", "project",
            "sap", "oracle", "salesforce", "crm",
            "machine learning", "deep learning", "data analysis", "statistics",
            "cfd", "fea", "fem", "cad", "cam", "plc", "scada",
            "hvac", "thermal", "mechanical", "electrical", "renewable",
            "lean", "six sigma", "agile", "scrum", "project management",
            "leadership", "communication", "teamwork", "problem solving"
        ]
        
        for skill in common_skills:
            if skill in job_description:
                skills.add(skill)
        
        skill_patterns = [
            r'\b(?:proficient|experienced|knowledge|skills?)\s+(?:in|with)\s+([^,.;]+)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:experience|knowledge|skills?)',
            r'(?:technologies|tools|software):\s*([^.;]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            for match in matches:
                extracted = match.strip().lower()
                if len(extracted) < 30:
                    skills.add(extracted)
        
        return skills
    
    def _find_skill_matches(self, job_skills: Set[str]) -> List[str]:
        matches = []
        
        for resume_skill in self.resume_skills:
            for job_skill in job_skills:
                if resume_skill in job_skill or job_skill in resume_skill:
                    matches.append(resume_skill)
                    break
        
        return list(set(matches))
    
    def _calculate_tfidf_similarity(self, job_description: str) -> float:
        try:
            resume_text = ' '.join([
                ' '.join(self.resume_keywords),
                ' '.join(self.resume_skills),
                ' '.join(self.target_roles)
            ])
            
            if not resume_text.strip() or not job_description.strip():
                return 0
            
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity * 100
        except:
            return 0
    
    def extract_experience_requirement(self, job_description: str) -> float:
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\s*-\s*(\d+)\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'(\d+)\s*years?\s*minimum'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    return float(matches[0][0])
                else:
                    return float(matches[0])
        
        if any(term in job_description.lower() for term in ['entry level', 'junior', 'graduate', 'intern']):
            return 0
        elif any(term in job_description.lower() for term in ['senior', 'lead', 'principal']):
            return 5
        elif any(term in job_description.lower() for term in ['mid-level', 'intermediate']):
            return 3
        
        return 0
    
    def is_job_recent(self, posted_date: str, max_days: int = 14) -> bool:
        try:
            if "today" in posted_date.lower() or "just now" in posted_date.lower():
                return True
            elif "yesterday" in posted_date.lower():
                return True
            elif "day" in posted_date.lower():
                days_match = re.search(r'(\d+)\s*days?', posted_date, re.IGNORECASE)
                if days_match:
                    days_ago = int(days_match.group(1))
                    return days_ago <= max_days
            elif "week" in posted_date.lower():
                weeks_match = re.search(r'(\d+)\s*weeks?', posted_date, re.IGNORECASE)
                if weeks_match:
                    weeks_ago = int(weeks_match.group(1))
                    return weeks_ago * 7 <= max_days
                return True
            elif "month" in posted_date.lower():
                return False
            
            from dateutil import parser
            job_date = parser.parse(posted_date)
            cutoff_date = datetime.now() - timedelta(days=max_days)
            return job_date >= cutoff_date
        except:
            return True