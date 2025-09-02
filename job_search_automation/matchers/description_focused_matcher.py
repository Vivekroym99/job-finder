"""
Description-Focused Job Matcher

This matcher prioritizes job description content over job titles for more accurate matching.
It performs deep content analysis to find jobs that truly match the candidate's background.

Matching Algorithm:
- 35% Job Description Content Analysis (word overlap, phrase similarity, context relevance)
- 25% Semantic Similarity (TF-IDF cosine similarity)
- 20% Technical Skills Matching (extracted from description)
- 10% Keyword Overlap (resume keywords vs job description keywords)
- 5% Experience Compatibility
- 5% Role Relevance (job title - minimal weight)
"""

from typing import Dict, List, Set, Tuple, Optional
import re
import logging
from collections import Counter
from datetime import datetime, timedelta

import re
from typing import Dict, List, Set, Tuple
from datetime import datetime, timedelta
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter

class DescriptionFocusedMatcher:
    """
    Enhanced Job Matcher that focuses primarily on job description content
    rather than job titles. Uses advanced NLP techniques for better matching.
    """
    
    def __init__(self, resume_profile: Dict, user_experience_years: float = None, user_experience_level: str = None):
        self.resume_profile = resume_profile
        self.resume_text = resume_profile.get('raw_text', '').lower()
        self.resume_keywords = resume_profile.get('keywords', set())
        self.resume_skills = set([s.lower() for s in resume_profile.get('skills', [])])
        self.resume_experience = resume_profile.get('experience_years', 0)
        self.target_roles = [r.lower() for r in resume_profile.get('target_roles', [])]
        
        # Use user-provided experience if available, otherwise use resume-extracted
        self.user_experience_years = user_experience_years if user_experience_years is not None else self.resume_experience
        self.user_experience_level = user_experience_level if user_experience_level else 'mid'
        
        # Download NLTK data
        try:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            self.stop_words = set(stopwords.words('english'))
            self.tokenize = word_tokenize
        except:
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            self.tokenize = lambda x: x.split()
        
        # Prepare resume vector for similarity calculations
        self._prepare_resume_vector()
    
    def _prepare_resume_vector(self):
        """Prepare a comprehensive resume representation for matching"""
        self.resume_vector_text = ' '.join([
            self.resume_text,
            ' '.join(self.resume_keywords),
            ' '.join(self.resume_skills),
            ' '.join(self.target_roles)
        ])
    
    def calculate_match_score(self, job: Dict) -> Tuple[float, Dict[str, any]]:
        """
        Calculate comprehensive match score focusing on job description content.
        Returns score and detailed breakdown for transparency.
        """
        job_title = job.get('job_title', '').lower()
        job_description = job.get('description', '').lower()
        company = job.get('company', '').lower()
        location = job.get('location', '').lower()
        
        # Extract job requirements and skills
        job_skills = self._extract_comprehensive_skills(job_description)
        job_keywords = self._extract_job_keywords(job_description)
        required_experience = self._extract_experience_requirement(job_description)
        
        # Calculate different matching scores with focus on description
        scores = {
            'description_content': self._calculate_description_content_match(job_description),
            'semantic_similarity': self._calculate_semantic_similarity(job_description),
            'skills_match': self._calculate_skills_match(job_skills),
            'keywords_match': self._calculate_keywords_match(job_keywords),
            'experience_compatibility': self._calculate_experience_compatibility(required_experience),
            'role_relevance': self._calculate_role_relevance(job_title, job_description)
        }
        
        # Weight distribution focusing heavily on job description content
        weights = {
            'description_content': 0.35,    # Primary focus on description
            'semantic_similarity': 0.25,    # Semantic understanding of content  
            'skills_match': 0.20,          # Technical skills alignment
            'keywords_match': 0.10,        # Keyword matching
            'experience_compatibility': 0.05, # Experience fit
            'role_relevance': 0.05         # Title relevance (minimal weight)
        }
        
        # Calculate final weighted score
        final_score = sum(scores[key] * weights[key] for key in scores.keys())
        
        # Create detailed match info
        match_details = {
            'final_score': min(100, final_score),
            'component_scores': scores,
            'weights': weights,
            'matched_skills': self._find_skill_matches(job_skills),
            'matched_keywords': self._find_keyword_matches(job_keywords),
            'experience_gap': required_experience - self.resume_experience,
            'job_skills_found': list(job_skills)[:10],  # Limit for readability
            'relevance_indicators': self._find_relevance_indicators(job_description)
        }
        
        return min(100, final_score), match_details
    
    def _calculate_description_content_match(self, job_description: str) -> float:
        """
        Deep content analysis of job description against resume.
        This is the core matching logic focusing on description content.
        """
        if not job_description.strip():
            return 0
            
        # Clean and prepare job description
        job_desc_clean = self._clean_text_for_matching(job_description)
        resume_clean = self._clean_text_for_matching(self.resume_text)
        
        if not job_desc_clean or not resume_clean:
            return 0
        
        # Calculate multiple content similarity measures
        word_overlap_score = self._calculate_word_overlap(resume_clean, job_desc_clean)
        phrase_similarity_score = self._calculate_phrase_similarity(resume_clean, job_desc_clean)
        context_relevance_score = self._calculate_context_relevance(resume_clean, job_desc_clean)
        
        # Combine scores with weights
        content_score = (
            word_overlap_score * 0.4 +
            phrase_similarity_score * 0.35 +
            context_relevance_score * 0.25
        )
        
        return min(100, content_score)
    
    def _calculate_semantic_similarity(self, job_description: str) -> float:
        """Calculate semantic similarity using TF-IDF and cosine similarity"""
        try:
            if not self.resume_vector_text.strip() or not job_description.strip():
                return 0
            
            # Use TF-IDF with more sophisticated parameters
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=200,
                ngram_range=(1, 3),  # Include bigrams and trigrams
                min_df=1,
                lowercase=True
            )
            
            documents = [self.resume_vector_text, job_description]
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity * 100
        except Exception as e:
            return 0
    
    def _calculate_skills_match(self, job_skills: Set[str]) -> float:
        """Calculate how well resume skills match job requirements"""
        if not self.resume_skills or not job_skills:
            return 0
        
        matched_skills = set()
        
        # Exact matches
        exact_matches = self.resume_skills.intersection(job_skills)
        matched_skills.update(exact_matches)
        
        # Partial matches (e.g., "python" in "python programming")
        for resume_skill in self.resume_skills:
            for job_skill in job_skills:
                if resume_skill in job_skill or job_skill in resume_skill:
                    matched_skills.add(resume_skill)
        
        # Calculate score based on coverage
        if len(job_skills) == 0:
            return 0
            
        skill_coverage = len(matched_skills) / len(job_skills)
        resume_utilization = len(matched_skills) / len(self.resume_skills) if self.resume_skills else 0
        
        # Balanced score considering both coverage and utilization
        return min(100, (skill_coverage * 0.7 + resume_utilization * 0.3) * 100)
    
    def extract_experience_requirement(self, description: str) -> Dict[str, any]:
        """Extract experience requirements from job description"""
        import re
        
        # Common patterns for experience requirements
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s*(?:of\s+)?(?:professional\s+)?(?:work\s+)?experience',
            r'minimum\s*(?:of\s+)?(\d+)\+?\s*years?',
            r'at\s*least\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:in\s+|with\s+)',
            r'(\d+)-(\d+)\s*years?\s*(?:of\s+)?experience'
        ]
        
        years = []
        description_lower = description.lower()
        
        for pattern in patterns:
            matches = re.finditer(pattern, description_lower)
            for match in matches:
                if len(match.groups()) == 2:  # Range pattern
                    min_years = int(match.group(1))
                    max_years = int(match.group(2))
                    years.extend([min_years, max_years])
                else:
                    years.append(int(match.group(1)))
        
        if years:
            min_exp = min(years)
            max_exp = max(years)
            avg_exp = sum(years) / len(years)
            
            # Determine experience level
            if avg_exp <= 1:
                level = 'entry-level'
            elif avg_exp <= 3:
                level = 'junior'
            elif avg_exp <= 6:
                level = 'mid-level' 
            elif avg_exp <= 10:
                level = 'senior'
            else:
                level = 'expert'
                
            return {
                'min_years': min_exp,
                'max_years': max_exp if max_exp != min_exp else None,
                'avg_years': round(avg_exp, 1),
                'level': level
            }
        
        # Check for seniority level keywords
        seniority_keywords = {
            'entry-level': ['entry', 'graduate', 'junior', 'intern', 'trainee'],
            'junior': ['junior', 'jr', 'associate'],
            'mid-level': ['mid', 'intermediate', 'regular'],
            'senior': ['senior', 'sr', 'lead', 'principal'],
            'expert': ['expert', 'architect', 'director', 'principal', 'staff']
        }
        
        for level, keywords in seniority_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return {
                    'min_years': None,
                    'max_years': None,
                    'avg_years': None,
                    'level': level
                }
        
        return {
            'min_years': None,
            'max_years': None, 
            'avg_years': None,
            'level': 'not-specified'
        }
    
    def is_job_recent(self, posted_date: str, max_age_days: int) -> bool:
        """Check if job posting is recent enough"""
        from datetime import datetime, timedelta
        
        if not posted_date:
            return True  # Assume recent if no date provided
            
        try:
            # Handle various date formats
            date_patterns = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%d-%m-%Y'
            ]
            
            posted_dt = None
            for pattern in date_patterns:
                try:
                    posted_dt = datetime.strptime(posted_date, pattern)
                    break
                except ValueError:
                    continue
            
            if not posted_dt:
                # Handle relative dates like "2 days ago", "1 week ago"
                posted_lower = posted_date.lower()
                if 'day' in posted_lower:
                    import re
                    match = re.search(r'(\d+)\s*day', posted_lower)
                    if match:
                        days_ago = int(match.group(1))
                        return days_ago <= max_age_days
                elif 'week' in posted_lower:
                    import re
                    match = re.search(r'(\d+)\s*week', posted_lower)
                    if match:
                        weeks_ago = int(match.group(1))
                        return (weeks_ago * 7) <= max_age_days
                elif 'month' in posted_lower:
                    return False  # Assume too old
                elif any(word in posted_lower for word in ['today', 'yesterday', 'recently']):
                    return True
                    
                return True  # Default to recent if can't parse
            
            # Calculate age
            now = datetime.now()
            age = (now - posted_dt).days
            return age <= max_age_days
            
        except Exception:
            return True  # Default to recent on error
    
    def _calculate_keywords_match(self, job_keywords: Set[str]) -> float:
        """Calculate keyword matching between resume and job"""
        if not self.resume_keywords or not job_keywords:
            return 0
        
        matched_keywords = self.resume_keywords.intersection(job_keywords)
        return (len(matched_keywords) / len(job_keywords)) * 100 if job_keywords else 0
    
    def _calculate_experience_compatibility(self, required_experience: float) -> float:
        """Calculate experience compatibility score using user-provided experience"""
        # Special handling for interns
        if self.user_experience_level == 'intern':
            if required_experience == 0 or 'intern' in self.user_experience_level:
                return 100  # Perfect match for intern positions
            elif required_experience <= 1:
                return 75  # Good match for entry-level positions
            else:
                return 30  # Poor match for experienced positions
        
        # Use user-provided experience for calculation
        experience_diff = self.user_experience_years - required_experience
        
        if required_experience == 0:
            # No requirement - better score for less experienced candidates
            if self.user_experience_years <= 2:
                return 100
            elif self.user_experience_years <= 5:
                return 85
            else:
                return 70  # Might be overqualified
        
        if experience_diff >= 3:  # Significantly overqualified
            return 70  # Lower score for overqualification
        elif experience_diff >= 0:  # Meets or exceeds requirement
            return 100
        elif experience_diff >= -1:  # Slightly underqualified
            return 80
        elif experience_diff >= -2:  # Moderately underqualified
            return 60
        else:  # Significantly underqualified
            return max(20, 40 - abs(experience_diff) * 5)
    
    def _calculate_role_relevance(self, job_title: str, job_description: str) -> float:
        """Calculate role relevance - now with minimal weight"""
        if not self.target_roles:
            return 50  # Neutral score when no target roles specified
        
        max_score = 0
        combined_text = f"{job_title} {job_description}"
        
        for target_role in self.target_roles:
            if target_role in combined_text:
                max_score = max(max_score, 80)
            else:
                # Check for word overlap
                target_words = set(target_role.split())
                text_words = set(combined_text.split())
                overlap = len(target_words.intersection(text_words))
                if overlap > 0:
                    score = (overlap / len(target_words)) * 60
                    max_score = max(max_score, score)
        
        return max_score
    
    def _extract_comprehensive_skills(self, job_description: str) -> Set[str]:
        """Extract comprehensive list of skills from job description"""
        skills = set()
        
        # Expanded technical skills dictionary
        skill_categories = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'scala', 'kotlin'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'laravel'],
            'data': ['sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'spark', 'hadoop', 'tableau', 'powerbi'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'gitlab', 'github actions'],
            'ai_ml': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'teams', 'figma', 'sketch', 'photoshop', 'autocad']
        }
        
        # Search for skills in all categories
        for category, skill_list in skill_categories.items():
            for skill in skill_list:
                if skill.lower() in job_description.lower():
                    skills.add(skill.lower())
        
        # Pattern-based skill extraction
        skill_patterns = [
            r'(?:experience|proficient|knowledge|familiar)\s+(?:in|with)\s+([^,.;:]+)',
            r'(?:technologies|tools|skills?|languages?):\s*([^.;]+)',
            r'(?:must\s+(?:have|know)|required?):\s*([^.;]+)',
            r'(?:prefer|desired|bonus).*?(?:experience|knowledge).*?(?:in|with)\s+([^,.;:]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split and clean extracted skills
                skill_parts = re.split(r'[,;/&|]', match.strip().lower())
                for part in skill_parts:
                    part = part.strip()
                    if 3 <= len(part) <= 30 and not any(stop in part for stop in ['and', 'or', 'the', 'in', 'with']):
                        skills.add(part)
        
        return skills
    
    def _extract_job_keywords(self, job_description: str) -> Set[str]:
        """Extract important keywords from job description"""
        # Remove stop words and extract meaningful keywords
        words = self.tokenize(job_description.lower())
        keywords = set()
        
        for word in words:
            word = re.sub(r'[^\w]', '', word)  # Remove punctuation
            if (len(word) >= 3 and 
                word not in self.stop_words and 
                not word.isdigit() and
                word.isalnum()):
                keywords.add(word)
        
        return keywords
    
    def _extract_experience_requirement(self, job_description: str) -> float:
        """Extract experience requirement from job description content (not just title)"""
        job_desc_lower = job_description.lower()
        
        # First check for specific intern/student mentions
        intern_patterns = [
            r'\bintern\b', r'\binternship\b', r'\bstudent\b', r'\bco-op\b',
            r'\bworking student\b', r'\bgraduate trainee\b', r'\btraineeship\b'
        ]
        for pattern in intern_patterns:
            if re.search(pattern, job_desc_lower):
                return 0  # Intern position
        
        # Check for explicit year requirements in description
        experience_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:professional\s*)?(?:experience|exp)',
            r'(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'minimum\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)',
            r'at\s*least\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*minimum',
            r'requires?\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:or\s*more|plus|\+)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:relevant|related|similar)',
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, job_desc_lower)
            if matches:
                if isinstance(matches[0], tuple) and len(matches[0]) > 1:
                    # For range patterns (e.g., "3-5 years"), take the minimum
                    try:
                        return float(matches[0][0])
                    except (ValueError, IndexError):
                        continue
                else:
                    try:
                        return float(matches[0]) if not isinstance(matches[0], tuple) else float(matches[0][0])
                    except (ValueError, TypeError):
                        continue
        
        # Check for level-based keywords in the description (not just title)
        level_keywords = {
            # Entry level indicators (0-1 years)
            'entry level': 0,
            'entry-level': 0,
            'no experience required': 0,
            'no prior experience': 0,
            'fresh graduate': 0,
            'recent graduate': 0,
            'new graduate': 0,
            'junior position': 1,
            'junior developer': 1,
            'junior engineer': 1,
            'junior analyst': 1,
            'associate level': 1,
            'trainee': 0,
            'apprentice': 0,
            
            # Mid-level indicators (2-5 years)
            'mid-level': 3,
            'mid level': 3,
            'intermediate': 3,
            'experienced professional': 4,
            'proven experience': 3,
            'solid experience': 3,
            'hands-on experience': 3,
            
            # Senior level indicators (5+ years)
            'senior level': 6,
            'senior position': 6,
            'senior developer': 6,
            'senior engineer': 6,
            'senior analyst': 6,
            'lead developer': 7,
            'lead engineer': 7,
            'principal': 8,
            'staff engineer': 8,
            'expert level': 8,
            'architect': 8,
            
            # Management indicators (8+ years)
            'manager': 8,
            'director': 10,
            'head of': 10,
            'vp': 12,
            'vice president': 12,
            'executive': 12,
            'c-level': 15,
            'cto': 15,
            'ceo': 15,
        }
        
        # Search for level keywords in the description
        for keyword, years in level_keywords.items():
            if keyword in job_desc_lower:
                return years
        
        # Check for educational requirements that might indicate experience level
        if any(term in job_desc_lower for term in ['bachelor', 'bs degree', 'undergraduate']):
            if 'master' in job_desc_lower or 'phd' in job_desc_lower:
                return 3  # Advanced degree might indicate mid-level
            else:
                return 0  # Just bachelor's might be entry-level
        
        # Default to entry-level if no clear indicators
        return 0
    
    def _clean_text_for_matching(self, text: str) -> str:
        """Clean text for better matching"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.lower().strip()
    
    def _calculate_word_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap between two texts"""
        words1 = set(word for word in text1.split() if word not in self.stop_words and len(word) > 2)
        words2 = set(word for word in text2.split() if word not in self.stop_words and len(word) > 2)
        
        if not words1 or not words2:
            return 0
        
        overlap = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return (overlap / union) * 100 if union > 0 else 0
    
    def _calculate_phrase_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on common phrases (bigrams/trigrams)"""
        def get_ngrams(text, n):
            words = text.split()
            return set([' '.join(words[i:i+n]) for i in range(len(words)-n+1)])
        
        bigrams1 = get_ngrams(text1, 2)
        bigrams2 = get_ngrams(text2, 2)
        trigrams1 = get_ngrams(text1, 3)
        trigrams2 = get_ngrams(text2, 3)
        
        bigram_overlap = len(bigrams1.intersection(bigrams2))
        trigram_overlap = len(trigrams1.intersection(trigrams2))
        
        total_possible = len(bigrams1.union(bigrams2)) + len(trigrams1.union(trigrams2))
        total_overlap = bigram_overlap + trigram_overlap * 1.5  # Weight trigrams more
        
        return (total_overlap / total_possible) * 100 if total_possible > 0 else 0
    
    def _calculate_context_relevance(self, resume_text: str, job_description: str) -> float:
        """Calculate contextual relevance using important terms"""
        # Define important context indicators
        context_indicators = [
            'responsible for', 'experience in', 'worked with', 'developed', 'managed',
            'led', 'implemented', 'designed', 'built', 'created', 'maintained',
            'collaborated', 'analyzed', 'optimized', 'improved', 'delivered'
        ]
        
        resume_contexts = []
        job_contexts = []
        
        for indicator in context_indicators:
            if indicator in resume_text:
                resume_contexts.append(indicator)
            if indicator in job_description:
                job_contexts.append(indicator)
        
        if not resume_contexts or not job_contexts:
            return 0
        
        common_contexts = len(set(resume_contexts).intersection(set(job_contexts)))
        total_contexts = len(set(resume_contexts).union(set(job_contexts)))
        
        return (common_contexts / total_contexts) * 100 if total_contexts > 0 else 0
    
    def _find_skill_matches(self, job_skills: Set[str]) -> List[str]:
        """Find matching skills between resume and job"""
        matches = []
        
        for resume_skill in self.resume_skills:
            for job_skill in job_skills:
                if (resume_skill in job_skill or 
                    job_skill in resume_skill or
                    resume_skill == job_skill):
                    matches.append(resume_skill)
                    break
        
        return list(set(matches))
    
    def _find_keyword_matches(self, job_keywords: Set[str]) -> List[str]:
        """Find matching keywords between resume and job"""
        return list(self.resume_keywords.intersection(job_keywords))
    
    def _find_relevance_indicators(self, job_description: str) -> List[str]:
        """Find indicators that make this job relevant to the candidate"""
        indicators = []
        
        # Check for career growth indicators
        growth_terms = ['growth', 'advancement', 'development', 'learning', 'training']
        if any(term in job_description.lower() for term in growth_terms):
            indicators.append('career_growth_opportunity')
        
        # Check for remote work
        remote_terms = ['remote', 'work from home', 'telecommute', 'distributed']
        if any(term in job_description.lower() for term in remote_terms):
            indicators.append('remote_work_available')
        
        # Check for competitive benefits
        benefit_terms = ['benefits', 'insurance', 'vacation', 'pto', 'bonus', 'stock options']
        if any(term in job_description.lower() for term in benefit_terms):
            indicators.append('competitive_benefits')
        
        return indicators
    
    def is_job_recent(self, posted_date: str, max_days: int = 14) -> bool:
        """Check if job posting is recent"""
        try:
            if any(term in posted_date.lower() for term in ["today", "just now"]):
                return True
            elif "yesterday" in posted_date.lower():
                return True
            elif "day" in posted_date.lower():
                days_match = re.search(r'(\d+)\s*days?', posted_date, re.IGNORECASE)
                if days_match:
                    return int(days_match.group(1)) <= max_days
            elif "week" in posted_date.lower():
                weeks_match = re.search(r'(\d+)\s*weeks?', posted_date, re.IGNORECASE)
                if weeks_match:
                    return int(weeks_match.group(1)) * 7 <= max_days
                return True
            elif "month" in posted_date.lower():
                return False
            
            # Try to parse as actual date
            from dateutil import parser
            job_date = parser.parse(posted_date)
            cutoff_date = datetime.now() - timedelta(days=max_days)
            return job_date >= cutoff_date
        except:
            return True