"""
Language Detection and Translation Utility
Handles multi-language job postings, primarily Polish to English
"""

import re
import logging
from typing import Dict, Tuple, Optional
from googletrans import Translator
import langdetect
from langdetect import detect, detect_langs

class JobTranslator:
    def __init__(self):
        self.translator = Translator()
        self.logger = logging.getLogger('JobTranslator')
        
        # Common Polish characters for quick detection
        self.polish_chars = set('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')
        
        # Cache for translations to avoid repeated API calls
        self.translation_cache = {}
        
        # Common Polish job terms and their translations
        self.polish_terms = {
            # Job titles
            'programista': 'programmer',
            'deweloper': 'developer',
            'inżynier': 'engineer',
            'specjalista': 'specialist',
            'kierownik': 'manager',
            'analityk': 'analyst',
            'konsultant': 'consultant',
            'architekt': 'architect',
            'administrator': 'administrator',
            'tester': 'tester',
            
            # Seniority levels
            'młodszy': 'junior',
            'starszy': 'senior',
            'główny': 'lead',
            'praktykant': 'intern',
            'stażysta': 'trainee',
            
            # Skills and technologies
            'wymagania': 'requirements',
            'umiejętności': 'skills',
            'doświadczenie': 'experience',
            'wykształcenie': 'education',
            'języki': 'languages',
            'znajomość': 'knowledge',
            'biegła': 'fluent',
            'podstawowa': 'basic',
            'zaawansowana': 'advanced',
            
            # Employment terms
            'umowa o pracę': 'employment contract',
            'umowa zlecenie': 'contract work',
            'b2b': 'b2b',
            'pełny etat': 'full-time',
            'część etatu': 'part-time',
            'zdalnie': 'remote',
            'hybrydowo': 'hybrid',
            'stacjonarnie': 'on-site',
            
            # Benefits
            'benefity': 'benefits',
            'wynagrodzenie': 'salary',
            'pensja': 'salary',
            'premie': 'bonuses',
            'urlop': 'vacation',
            'szkolenia': 'training',
            'rozwój': 'development'
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text
        Returns ISO 639-1 language code (e.g., 'en', 'pl')
        """
        if not text or len(text.strip()) < 10:
            return 'unknown'
        
        try:
            # Quick check for Polish characters
            if any(char in self.polish_chars for char in text):
                return 'pl'
            
            # Use langdetect for more accurate detection
            detected = detect(text)
            return detected
            
        except Exception as e:
            self.logger.warning(f"Language detection failed: {str(e)}")
            # Fallback: check for Polish characters
            if any(char in self.polish_chars for char in text):
                return 'pl'
            return 'en'  # Default to English
    
    def translate_text(self, text: str, source_lang: str = None, target_lang: str = 'en') -> Tuple[str, str]:
        """
        Translate text to target language
        Returns tuple of (translated_text, detected_language)
        """
        if not text or len(text.strip()) < 3:
            return text, 'unknown'
        
        # Check cache first
        cache_key = f"{text[:100]}_{source_lang}_{target_lang}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        try:
            # Detect source language if not provided
            if not source_lang:
                source_lang = self.detect_language(text)
            
            # Skip translation if already in target language
            if source_lang == target_lang:
                result = (text, source_lang)
                self.translation_cache[cache_key] = result
                return result
            
            # Translate using Google Translate
            translation = self.translator.translate(
                text, 
                src=source_lang, 
                dest=target_lang
            )
            
            translated_text = translation.text
            detected_lang = translation.src
            
            result = (translated_text, detected_lang)
            self.translation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Translation failed: {str(e)}")
            # Fallback: return original text with detected language
            return text, source_lang or 'unknown'
    
    def translate_job(self, job: Dict) -> Dict:
        """
        Translate job posting to English if needed
        Adds 'original_language' and 'translated' fields
        """
        # Fields to translate
        translatable_fields = ['job_title', 'description', 'company', 'location']
        
        # Detect language from description or title
        sample_text = f"{job.get('job_title', '')} {job.get('description', '')[:200]}"
        detected_lang = self.detect_language(sample_text)
        
        job['original_language'] = detected_lang
        job['translated'] = False
        
        # If not in English, translate
        if detected_lang != 'en' and detected_lang != 'unknown':
            job['translated'] = True
            
            for field in translatable_fields:
                if field in job and job[field]:
                    original_value = job[field]
                    translated_value, _ = self.translate_text(original_value, detected_lang, 'en')
                    
                    # Store both original and translated
                    job[f'{field}_original'] = original_value
                    job[field] = translated_value
            
            # Translate skills if present
            if 'required_skills' in job and isinstance(job['required_skills'], list):
                translated_skills = []
                for skill in job['required_skills']:
                    if isinstance(skill, str):
                        translated_skill, _ = self.translate_text(skill, detected_lang, 'en')
                        translated_skills.append(translated_skill)
                    else:
                        translated_skills.append(skill)
                
                job['required_skills_original'] = job['required_skills']
                job['required_skills'] = translated_skills
        
        return job
    
    def quick_translate_polish_terms(self, text: str) -> str:
        """
        Quick translation of common Polish job terms
        Faster than full translation for known terms
        """
        text_lower = text.lower()
        
        for polish, english in self.polish_terms.items():
            if polish in text_lower:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(polish), re.IGNORECASE)
                text = pattern.sub(english, text)
        
        return text
    
    def is_polish_text(self, text: str) -> bool:
        """
        Quick check if text contains Polish characters
        """
        return any(char in self.polish_chars for char in text)
    
    def get_language_confidence(self, text: str) -> Dict[str, float]:
        """
        Get confidence scores for detected languages
        """
        if not text or len(text.strip()) < 10:
            return {'unknown': 1.0}
        
        try:
            langs = detect_langs(text)
            return {lang.lang: lang.prob for lang in langs}
        except Exception as e:
            self.logger.warning(f"Language confidence detection failed: {str(e)}")
            
            # Fallback
            if self.is_polish_text(text):
                return {'pl': 0.8, 'en': 0.2}
            return {'en': 0.8}
    
    def translate_batch(self, texts: list, source_lang: str = None, target_lang: str = 'en') -> list:
        """
        Translate multiple texts efficiently
        """
        translations = []
        
        for text in texts:
            translated, detected = self.translate_text(text, source_lang, target_lang)
            translations.append({
                'original': text,
                'translated': translated,
                'original_language': detected
            })
        
        return translations