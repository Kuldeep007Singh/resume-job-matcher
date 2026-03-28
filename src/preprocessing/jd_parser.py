"""
Job Description Parser
Extracts structured information from job descriptions
"""

import re
from typing import Dict, List, Optional
import json


class JobDescriptionParser:
    """Parse and structure job descriptions"""
    
    def __init__(self):
        self.jd_text = ""
        self.structured_data = {}
    
    def clean_text(self, text: str) -> str:
        """Clean job description text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s@.+\-,():/•\n]', '', text)
        return text.strip()
    
    def extract_experience_required(self, text: str) -> Dict[str, int]:
        """
        Extract required years of experience
        
        Args:
            text: Job description text
            
        Returns:
            Dictionary with min and max years
        """
        experience = {
            'min_years': 0,
            'max_years': 0,
            'mentioned': False
        }
        
        # Patterns for experience
        patterns = [
            r'(\d+)\s*\+?\s*(?:to|\-)\s*(\d+)\s*years',  # 3-5 years
            r'(\d+)\s*\+?\s*years',  # 3+ years
            r'minimum\s+(\d+)\s+years',
            r'at least\s+(\d+)\s+years',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                experience['mentioned'] = True
                if isinstance(matches[0], tuple):
                    # Range found (e.g., 3-5 years)
                    experience['min_years'] = int(matches[0][0])
                    experience['max_years'] = int(matches[0][1])
                else:
                    # Single value found
                    experience['min_years'] = int(matches[0])
                    experience['max_years'] = int(matches[0])
                break
        
        return experience
    
    def extract_required_skills(self, text: str, skills_db_path: str = "data/skills_db/skills_database.json") -> Dict[str, List[str]]:
        """
        Extract required skills from job description
        
        Args:
            text: Job description text
            skills_db_path: Path to skills database
            
        Returns:
            Dictionary with categorized skills
        """
        # Load skills database
        try:
            with open(skills_db_path, 'r') as f:
                skills_db = json.load(f)
        except:
            skills_db = {}
        
        found_skills = {category: [] for category in skills_db.keys()}
        text_lower = text.lower()
        
        for category, skills in skills_db.items():
            for skill in skills:
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)
        
        return found_skills
    
    def extract_education_requirements(self, text: str) -> List[str]:
        """
        Extract education requirements
        
        Args:
            text: Job description text
            
        Returns:
            List of education requirements
        """
        education = []
        text_lower = text.lower()
        
        degree_patterns = {
            'phd': r'\b(?:ph\.?d\.?|doctorate|doctoral)\b',
            'masters': r'\b(?:master\'?s?|m\.tech|m\.sc|mca|mba)\b',
            'bachelors': r'\b(?:bachelor\'?s?|b\.tech|b\.e\.?|b\.sc|bca)\b',
        }
        
        for degree, pattern in degree_patterns.items():
            if re.search(pattern, text_lower):
                education.append(degree)
        
        return education
    
    def extract_job_title(self, text: str) -> Optional[str]:
        """
        Extract job title (usually in first few lines)
        
        Args:
            text: Job description text
            
        Returns:
            Job title
        """
        lines = text.split('\n')
        
        # Common job title keywords
        title_keywords = [
            'engineer', 'developer', 'scientist', 'analyst', 'manager',
            'architect', 'lead', 'senior', 'junior', 'intern', 'consultant'
        ]
        
        for line in lines[:10]:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in title_keywords):
                # Clean and return
                title = line.strip()
                if len(title) < 100:  # Reasonable title length
                    return title
        
        return None
    
    def extract_company_name(self, text: str) -> Optional[str]:
        """
        Extract company name (heuristic-based)
        
        Args:
            text: Job description text
            
        Returns:
            Company name
        """
        # Look for common patterns
        patterns = [
            r'(?:Company|Organization|About us):\s*([A-Z][A-Za-z\s&]+)',
            r'^([A-Z][A-Za-z\s&]+(?:Inc|Ltd|Corp|LLC|Pvt))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def identify_must_have_vs_nice_to_have(self, text: str) -> Dict[str, List[str]]:
        """
        Identify must-have vs nice-to-have requirements
        
        Args:
            text: Job description text
            
        Returns:
            Dictionary separating requirements
        """
        requirements = {
            'must_have': [],
            'nice_to_have': []
        }
        
        text_lower = text.lower()
        
        # Split by sections
        must_have_section = re.search(
            r'(?:required|must have|mandatory|essential)(?:\s+skills)?:?\s*(.*?)(?=\n\n|nice to have|preferred|$)',
            text_lower,
            re.DOTALL
        )
        
        nice_to_have_section = re.search(
            r'(?:nice to have|preferred|bonus|plus)(?:\s+skills)?:?\s*(.*?)(?=\n\n|$)',
            text_lower,
            re.DOTALL
        )
        
        if must_have_section:
            must_have_text = must_have_section.group(1)
            requirements['must_have'] = [
                item.strip() 
                for item in re.split(r'[•\-\n]', must_have_text) 
                if item.strip() and len(item.strip()) > 3
            ][:10]  # Limit to 10 items
        
        if nice_to_have_section:
            nice_to_have_text = nice_to_have_section.group(1)
            requirements['nice_to_have'] = [
                item.strip() 
                for item in re.split(r'[•\-\n]', nice_to_have_text) 
                if item.strip() and len(item.strip()) > 3
            ][:10]
        
        return requirements
    
    def parse_job_description(self, text: str) -> Dict:
        """
        Complete job description parsing pipeline
        
        Args:
            text: Job description text
            
        Returns:
            Structured job description data
        """
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Extract all components
        job_title = self.extract_job_title(cleaned_text)
        company = self.extract_company_name(cleaned_text)
        experience = self.extract_experience_required(cleaned_text)
        skills = self.extract_required_skills(cleaned_text)
        education = self.extract_education_requirements(cleaned_text)
        requirements = self.identify_must_have_vs_nice_to_have(cleaned_text)
        
        # Get all skills as flat list
        all_skills = []
        for category_skills in skills.values():
            all_skills.extend(category_skills)
        
        result = {
            'raw_text': text,
            'cleaned_text': cleaned_text,
            'job_title': job_title,
            'company': company,
            'experience_required': experience,
            'required_skills': skills,
            'all_required_skills': list(set(all_skills)),
            'education_requirements': education,
            'must_have_requirements': requirements['must_have'],
            'nice_to_have_requirements': requirements['nice_to_have'],
            'total_skills_required': len(all_skills)
        }
        
        return result


# Test function
def test_jd_parser():
    """Test job description parser"""
    
    sample_jd = """
    Senior Machine Learning Engineer
    TechCorp India Pvt. Ltd.
    
    About the Role:
    We are looking for an experienced ML Engineer to join our AI team.
    
    Required Skills:
    • 5+ years of experience in machine learning
    • Strong proficiency in Python, TensorFlow, PyTorch
    • Experience with AWS, Docker, Kubernetes
    • Knowledge of NLP and Computer Vision
    • Bachelor's or Master's in Computer Science
    
    Nice to Have:
    • Experience with MLOps
    • Knowledge of React and FastAPI
    • Publications in AI conferences
    
    Responsibilities:
    - Design and deploy ML models
    - Lead a team of 3-4 engineers
    - Collaborate with product teams
    """
    
    parser = JobDescriptionParser()
    result = parser.parse_job_description(sample_jd)
    
    print("Job Description Parsing Test")
    print("="*60)
    print(f"\n✓ Job Title: {result['job_title']}")
    print(f"✓ Company: {result['company']}")
    print(f"✓ Experience Required: {result['experience_required']['min_years']}+ years")
    print(f"✓ Total Skills Required: {result['total_skills_required']}")
    print(f"\n✓ Required Skills: {', '.join(result['all_required_skills'][:10])}")
    print(f"\n✓ Must Have: {len(result['must_have_requirements'])} requirements")
    print(f"✓ Nice to Have: {len(result['nice_to_have_requirements'])} requirements")


if __name__ == "__main__":
    test_jd_parser()