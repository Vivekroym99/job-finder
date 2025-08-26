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
        experience_entries = []
        
        date_patterns = [
            r'(\w+\s+\d{4})\s*[–-]\s*Present',
            r'(\w+\s+\d{4})\s*[–-]\s*(\w+\s+\d{4})',
            r'(\d{4})\s*[–-]\s*(\d{4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, self.resume_text)
            experience_entries.extend(matches)
        
        total_months = 0
        current_year = datetime.now().year
        
        for entry in experience_entries:
            try:
                if isinstance(entry, tuple):
                    if "Present" in str(entry):
                        start_date = entry[0]
                        end_months = current_year * 12 + datetime.now().month
                        if "2025" in start_date:
                            start_months = 2025 * 12 + 2
                        elif "2024" in start_date:
                            start_months = 2024 * 12 + 3
                        elif "2021" in start_date:
                            start_months = 2021 * 12 + 3
                        elif "2017" in start_date:
                            start_months = 2017 * 12 + 6
                        else:
                            continue
                        total_months += max(0, end_months - start_months)
            except:
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