import re
from typing import Dict, List, Set
from datetime import datetime

class ResumeParser:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path
        self.resume_text = self._load_resume()
        
    def _load_resume(self) -> str:
        with open(self.resume_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_profile(self) -> Dict:
        profile = {
            "name": self._extract_name(),
            "email": self._extract_email(),
            "phone": self._extract_phone(),
            "location": self._extract_location(),
            "skills": self._extract_skills(),
            "experience_years": self._calculate_experience_years(),
            "education": self._extract_education(),
            "keywords": self._extract_keywords(),
            "target_roles": self._extract_target_roles(),
            "certifications": self._extract_certifications(),
            "tools_software": self._extract_tools_software()
        }
        return profile
    
    def _extract_name(self) -> str:
        lines = self.resume_text.split('\n')
        if lines:
            return lines[0].strip()
        return ""
    
    def _extract_email(self) -> str:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, self.resume_text)
        return matches[0] if matches else ""
    
    def _extract_phone(self) -> str:
        phone_pattern = r'\+\d{1,3}[\s-]?\d{3,14}'
        matches = re.findall(phone_pattern, self.resume_text)
        return matches[0] if matches else ""
    
    def _extract_location(self) -> str:
        location_pattern = r'Warsaw[,\s]+(?:PL|Poland)'
        matches = re.findall(location_pattern, self.resume_text, re.IGNORECASE)
        return "Warsaw, Poland" if matches else ""
    
    def _extract_skills(self) -> List[str]:
        skills = []
        
        engineering_tools = [
            "AutoCAD", "Revit", "Revit MEP", "SolidWorks", "Inventor", 
            "Navisworks", "HAP", "Ansys", "Aspen HYSYS", "MATLAB",
            "CFD", "FEA", "FEM", "CAD", "CAM"
        ]
        
        programming_skills = [
            "Python", "SQL", "Excel VBA", "VBA", "SCADA"
        ]
        
        project_tools = [
            "MS Project", "MS Excel", "Excel", "Key CRM", "CRM"
        ]
        
        domain_skills = [
            "HVAC", "Heat Transfer", "Thermal Engineering", "Power Engineering",
            "Renewable Energy", "Wind Turbine", "Hydrogen Production",
            "Machine Learning", "ML", "Isolation Forest", "Random Forest",
            "Project Management", "Lean Six Sigma", "Six Sigma",
            "Sales", "B2B", "B2C", "Customer Service"
        ]
        
        for skill_list in [engineering_tools, programming_skills, project_tools, domain_skills]:
            for skill in skill_list:
                if skill.lower() in self.resume_text.lower():
                    skills.append(skill)
        
        return list(set(skills))
    
    def _calculate_experience_years(self) -> float:
        """Calculate total years of experience from resume text"""
        experience_entries = []
        
        # Pattern to match date ranges like "Mar 2021 - Sept 2021" or "Feb 2025 - Present"
        date_patterns = [
            r'(\w+\s+\d{4})\s*[–\-]\s*Present',
            r'(\w+\s+\d{4})\s*[–\-]\s*(\w+\s+\d{4})',
            r'(\d{4})\s*[–\-]\s*(\d{4})',
            r'(\w+\s+\d{4})\s*[–\-]\s*(\w+\s+\d{4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, self.resume_text, re.IGNORECASE)
            experience_entries.extend(matches)
        
        total_months = 0
        current_date = datetime.now()
        
        # Month name to number mapping
        month_map = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
            'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
            'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
            'aug': 8, 'august': 8, 'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        
        def parse_date(date_str):
            """Parse date string to (year, month) tuple"""
            parts = date_str.strip().split()
            if len(parts) == 2:
                month_name, year = parts
                month_num = month_map.get(month_name.lower(), 1)
                return (int(year), month_num)
            elif len(parts) == 1 and parts[0].isdigit():
                return (int(parts[0]), 1)
            return None
        
        for entry in experience_entries:
            try:
                if isinstance(entry, str):
                    # Single date with Present
                    start_date = parse_date(entry)
                    if start_date:
                        # Handle future dates by capping at current date
                        end_year, end_month = current_date.year, current_date.month
                        start_year, start_month = start_date
                        
                        # Skip if start date is in the future
                        if start_year > current_date.year or \
                           (start_year == current_date.year and start_month > current_date.month):
                            continue
                        
                        months = (end_year - start_year) * 12 + (end_month - start_month)
                        total_months += max(0, months)
                        
                elif isinstance(entry, tuple) and len(entry) == 2:
                    # Date range
                    start_str, end_str = entry
                    start_date = parse_date(start_str)
                    
                    if end_str.lower() == 'present':
                        end_date = (current_date.year, current_date.month)
                    else:
                        end_date = parse_date(end_str)
                    
                    if start_date and end_date:
                        start_year, start_month = start_date
                        end_year, end_month = end_date
                        
                        # Handle future dates
                        if end_year > current_date.year or \
                           (end_year == current_date.year and end_month > current_date.month):
                            end_year, end_month = current_date.year, current_date.month
                        
                        # Skip if start is after end
                        if start_year > end_year or \
                           (start_year == end_year and start_month > end_month):
                            continue
                        
                        months = (end_year - start_year) * 12 + (end_month - start_month)
                        total_months += max(0, months)
            except Exception as e:
                continue
        
        return round(total_months / 12, 1)
    
    def _extract_education(self) -> List[str]:
        education = []
        
        degrees = [
            "Master's in Power (Thermal) Engineering",
            "Bachelor's in Mechanical Engineering"
        ]
        
        for degree in degrees:
            if degree in self.resume_text:
                education.append(degree)
        
        return education
    
    def _extract_keywords(self) -> Set[str]:
        keywords = set()
        
        technical_keywords = [
            "engineering", "mechanical", "thermal", "power", "energy",
            "HVAC", "renewable", "wind", "solar", "hydrogen",
            "design", "analysis", "simulation", "modeling", "optimization",
            "AutoCAD", "Revit", "SolidWorks", "Ansys", "MATLAB",
            "Python", "SQL", "data", "analytics", "machine learning",
            "project management", "lean", "six sigma", "quality",
            "sales", "B2B", "B2C", "customer", "CRM",
            "CFD", "FEA", "FEM", "CAD", "CAM", "SCADA",
            "heat transfer", "fluid mechanics", "thermodynamics",
            "ASHRAE", "compliance", "standards", "specifications"
        ]
        
        for keyword in technical_keywords:
            if keyword.lower() in self.resume_text.lower():
                keywords.add(keyword.lower())
        
        return keywords
    
    def _extract_target_roles(self) -> List[str]:
        target_roles = [
            "Mechanical Engineer",
            "Thermal Engineer",
            "Power Engineer",
            "Energy Engineer",
            "HVAC Engineer",
            "Design Engineer",
            "Project Engineer",
            "Sales Engineer",
            "Technical Sales",
            "CAD Engineer",
            "Simulation Engineer",
            "CFD Engineer",
            "FEA Engineer",
            "Renewable Energy Engineer",
            "Engineering Analyst",
            "Graduate Engineer",
            "Junior Engineer"
        ]
        
        return target_roles
    
    def _extract_certifications(self) -> List[str]:
        certs = []
        cert_section = re.search(r'CERTIFICATION.*?(?=\n[A-Z]+|$)', self.resume_text, re.DOTALL)
        
        if cert_section:
            cert_text = cert_section.group()
            cert_lines = cert_text.split('\n')
            for line in cert_lines[1:]:
                if line.strip() and not line.startswith(' '):
                    certs.append(line.strip())
        
        return certs
    
    def _extract_tools_software(self) -> List[str]:
        tools = []
        skills_section = re.search(r'SKILLS.*?(?=\n[A-Z]+|$)', self.resume_text, re.DOTALL)
        
        if skills_section:
            skills_text = skills_section.group()
            tool_matches = re.findall(r':\s*([^:\n]+)', skills_text)
            for match in tool_matches:
                items = [item.strip() for item in match.split(',')]
                tools.extend(items)
        
        return tools