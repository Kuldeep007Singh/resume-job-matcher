"""
Skills Extractor
Extracts technical and soft skills from resume text
"""

import json
import re
from typing import List, Dict, Set
import spacy
from pathlib import Path

class SkillsExtractor:
    """Extract skills from resume text using multiple methods"""
    
    def __init__(self, skills_db_path: str = "data/skills_db/skills_database.json"):
        """
        Initialize skills extractor
        
        Args:
            skills_db_path: Path to skills database JSON
        """
        self.skills_db = self._load_skills_database(skills_db_path)
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("⚠️  spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Flatten all skills for quick lookup
        self.all_skills = self._flatten_skills()
    
    def _load_skills_database(self, path: str) -> Dict:
        """Load skills database from JSON"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Skills database not found at {path}")
            return {
                "programming_languages": [],
                "ml_frameworks": [],
                "web_frameworks": [],
                "databases": [],
                "cloud_platforms": [],
                "devops_tools": [],
                "data_tools": [],
                "soft_skills": [],
                "domains": []
            }
    
    def _flatten_skills(self) -> Set[str]:
        """Create a flat set of all skills (lowercased)"""
        all_skills = set()
        for category, skills in self.skills_db.items():
            all_skills.update([skill.lower() for skill in skills])
        return all_skills
    
    def extract_skills_keyword_matching(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills using keyword matching
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with categorized skills
        """
        text_lower = text.lower()
        found_skills = {category: [] for category in self.skills_db.keys()}
        
        for category, skills in self.skills_db.items():
            for skill in skills:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)
        
        return found_skills
    
    def extract_skills_fuzzy(self, text: str) -> List[str]:
        """
        Extract skills with fuzzy matching (handles variations)
        
        Args:
            text: Resume text
            
        Returns:
            List of found skills
        """
        text_lower = text.lower()
        found_skills = []
        
        # Split text into tokens
        tokens = re.findall(r'\b\w+(?:\.\w+)*\b', text_lower)
        bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)]
        trigrams = [f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}" for i in range(len(tokens)-2)]
        
        # Check all n-grams
        all_ngrams = tokens + bigrams + trigrams
        
        for ngram in all_ngrams:
            if ngram in self.all_skills:
                # Find original case from database
                for category, skills in self.skills_db.items():
                    for skill in skills:
                        if skill.lower() == ngram:
                            if skill not in found_skills:
                                found_skills.append(skill)
        
        return found_skills
    
    def extract_skills_spacy(self, text: str) -> List[str]:
        """
        Extract skills using spaCy NER (for additional context)
        
        Args:
            text: Resume text
            
        Returns:
            List of potential skills from named entities
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        skills = []
        
        # Extract entities that might be skills
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
                # Check if entity is a known skill
                if ent.text.lower() in self.all_skills:
                    skills.append(ent.text)
        
        return skills
    
    def extract_years_of_experience(self, text: str) -> Dict[str, int]:
        """
        Extract years of experience mentioned in text
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with experience estimates
        """
        experience = {
            'total_years': 0,
            'mentions': []
        }
        
        # Patterns for experience mentions
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s+of\s+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s+in',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                years = int(match)
                experience['mentions'].append(years)
        
        # Take maximum mentioned years
        if experience['mentions']:
            experience['total_years'] = max(experience['mentions'])
        
        return experience
    
    def extract_all_skills(self, text: str) -> Dict:
        """
        Extract skills using all methods and combine results
        
        Args:
            text: Resume text
            
        Returns:
            Comprehensive dictionary of extracted skills
        """
        # Method 1: Keyword matching (categorized)
        categorized_skills = self.extract_skills_keyword_matching(text)
        
        # Method 2: Fuzzy matching
        fuzzy_skills = self.extract_skills_fuzzy(text)
        
        # Method 3: spaCy NER
        spacy_skills = self.extract_skills_spacy(text)
        
        # Combine and deduplicate
        all_found_skills = set(fuzzy_skills + spacy_skills)
        
        # Add to categorized results
        for category, skills in categorized_skills.items():
            all_found_skills.update(skills)
        
        # Extract experience
        experience = self.extract_years_of_experience(text)
        
        result = {
            'categorized_skills': categorized_skills,
            'all_skills': sorted(list(all_found_skills)),
            'total_skills_count': len(all_found_skills),
            'experience': experience
        }
        
        return result
    
    def get_skill_categories(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize a list of skills
        
        Args:
            skills: List of skill names
            
        Returns:
            Dictionary with categorized skills
        """
        categorized = {category: [] for category in self.skills_db.keys()}
        
        for skill in skills:
            for category, db_skills in self.skills_db.items():
                if skill in db_skills:
                    categorized[category].append(skill)
                    break
        
        return categorized


# Test function
def test_skills_extractor():
    """Test skills extraction"""
    
    sample_text = """
    John Doe
    Software Engineer with 5 years of experience
    
    Skills:
    - Programming: Python, Java, JavaScript
    - ML/AI: TensorFlow, PyTorch, Scikit-learn, NLP
    - Web: React, Node.js, Django, FastAPI
    - Cloud: AWS, Docker, Kubernetes
    - Database: PostgreSQL, MongoDB, Redis
    - Tools: Git, Jenkins, Tableau
    
    Strong communication and leadership skills.
    """
    
    extractor = SkillsExtractor()
    
    print("Testing Skills Extraction...")
    print("="*50)
    
    results = extractor.extract_all_skills(sample_text)
    
    print(f"\n✓ Total Skills Found: {results['total_skills_count']}")
    print(f"\n✓ Experience: {results['experience']['total_years']} years")
    
    print("\n✓ Categorized Skills:")
    for category, skills in results['categorized_skills'].items():
        if skills:
            print(f"  - {category}: {', '.join(skills)}")
    
    print("\n✓ All Skills:")
    print(f"  {', '.join(results['all_skills'][:20])}")  # Show first 20


if __name__ == "__main__":
    test_skills_extractor()