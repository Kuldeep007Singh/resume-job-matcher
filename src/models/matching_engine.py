"""
Matching Engine
Matches resumes with job descriptions using multiple signals
"""

import numpy as np
from typing import Dict, List, Tuple
from collections import Counter


class MatchingEngine:
    """Match resumes with job descriptions"""
    
    def __init__(self):
        """Initialize matching engine"""
        self.weights = {
            'semantic_similarity': 0.40,
            'skill_match': 0.30,
            'experience_match': 0.15,
            'education_match': 0.10,
            'keyword_density': 0.05
        }
    
    def calculate_skill_match(self, resume_skills: List[str], jd_skills: List[str]) -> Dict:
        """
        Calculate skill matching score
        
        Args:
            resume_skills: List of candidate skills
            jd_skills: List of required skills
            
        Returns:
            Dictionary with match details
        """
        if not jd_skills:
            return {
                'score': 1.0,
                'matched_skills': [],
                'missing_skills': [],
                'additional_skills': resume_skills,
                'match_ratio': 1.0
            }
        
        # Convert to lowercase for comparison
        resume_skills_lower = [s.lower() for s in resume_skills]
        jd_skills_lower = [s.lower() for s in jd_skills]
        
        # Find matches
        matched = [s for s in jd_skills if s.lower() in resume_skills_lower]
        missing = [s for s in jd_skills if s.lower() not in resume_skills_lower]
        additional = [s for s in resume_skills if s.lower() not in jd_skills_lower]
        
        # Calculate match ratio
        match_ratio = len(matched) / len(jd_skills) if jd_skills else 0
        
        return {
            'score': match_ratio,
            'matched_skills': matched,
            'missing_skills': missing,
            'additional_skills': additional,
            'match_ratio': match_ratio,
            'matched_count': len(matched),
            'required_count': len(jd_skills)
        }
    
    def calculate_experience_match(self, candidate_years: int, required_years: Dict) -> Dict:
        """
        Calculate experience matching score
        
        Args:
            candidate_years: Candidate's years of experience
            required_years: Required experience dictionary
            
        Returns:
            Dictionary with match details
        """
        if not required_years.get('mentioned'):
            return {'score': 1.0, 'meets_requirement': True, 'difference': 0}
        
        min_required = required_years.get('min_years', 0)
        
        # Calculate score
        if candidate_years >= min_required:
            score = 1.0
            meets_requirement = True
            difference = candidate_years - min_required
        else:
            # Partial credit for being close
            score = candidate_years / min_required if min_required > 0 else 0
            meets_requirement = False
            difference = candidate_years - min_required
        
        return {
            'score': score,
            'meets_requirement': meets_requirement,
            'candidate_years': candidate_years,
            'required_years': min_required,
            'difference': difference
        }
    
    def calculate_education_match(self, candidate_education: str, required_education: List[str]) -> Dict:
        """
        Calculate education matching score
        
        Args:
            candidate_education: Candidate's education level
            required_education: Required education levels
            
        Returns:
            Dictionary with match details
        """
        if not required_education:
            return {'score': 1.0, 'meets_requirement': True}
        
        # Education hierarchy
        education_levels = {
            'phd': 3,
            'masters': 2,
            'bachelors': 1
        }
        
        # Get candidate level (from text)
        candidate_level = 0
        candidate_text_lower = candidate_education.lower()
        for level, value in education_levels.items():
            if level in candidate_text_lower:
                candidate_level = max(candidate_level, value)
        
        # Get required level
        required_level = 0
        for level in required_education:
            level_value = education_levels.get(level, 0)
            required_level = max(required_level, level_value)
        
        # Calculate score
        meets_requirement = candidate_level >= required_level
        score = 1.0 if meets_requirement else (candidate_level / required_level if required_level > 0 else 0)
        
        return {
            'score': score,
            'meets_requirement': meets_requirement,
            'candidate_level': candidate_level,
            'required_level': required_level
        }
    
    def calculate_keyword_density(self, resume_text: str, jd_text: str) -> float:
        """
        Calculate how many JD keywords appear in resume
        
        Args:
            resume_text: Resume text
            jd_text: Job description text
            
        Returns:
            Keyword density score
        """
        # Extract important words from JD (longer than 3 chars)
        jd_words = set([
            word.lower() 
            for word in jd_text.split() 
            if len(word) > 3 and word.isalnum()
        ])
        
        resume_words = set([
            word.lower() 
            for word in resume_text.split() 
            if len(word) > 3 and word.isalnum()
        ])
        
        # Calculate overlap
        common_words = jd_words.intersection(resume_words)
        density = len(common_words) / len(jd_words) if jd_words else 0
        
        return density
    
    def calculate_overall_match(
        self,
        semantic_similarity: float,
        skill_match: Dict,
        experience_match: Dict,
        education_match: Dict,
        keyword_density: float
    ) -> Dict:
        """
        Calculate overall matching score
        
        Args:
            semantic_similarity: Embedding similarity score
            skill_match: Skill matching results
            experience_match: Experience matching results
            education_match: Education matching results
            keyword_density: Keyword density score
            
        Returns:
            Overall match details
        """
        # Calculate weighted score
        overall_score = (
            self.weights['semantic_similarity'] * semantic_similarity +
            self.weights['skill_match'] * skill_match['score'] +
            self.weights['experience_match'] * experience_match['score'] +
            self.weights['education_match'] * education_match['score'] +
            self.weights['keyword_density'] * keyword_density
        )
        
        # Convert to percentage
        match_percentage = overall_score * 100
        
        # Determine match level
        if match_percentage >= 80:
            match_level = "Excellent Match"
        elif match_percentage >= 60:
            match_level = "Good Match"
        elif match_percentage >= 40:
            match_level = "Fair Match"
        else:
            match_level = "Poor Match"
        
        return {
            'overall_score': overall_score,
            'match_percentage': match_percentage,
            'match_level': match_level,
            'component_scores': {
                'semantic_similarity': semantic_similarity,
                'skill_match': skill_match['score'],
                'experience_match': experience_match['score'],
                'education_match': education_match['score'],
                'keyword_density': keyword_density
            },
            'weighted_contributions': {
                'semantic_similarity': self.weights['semantic_similarity'] * semantic_similarity * 100,
                'skill_match': self.weights['skill_match'] * skill_match['score'] * 100,
                'experience_match': self.weights['experience_match'] * experience_match['score'] * 100,
                'education_match': self.weights['education_match'] * education_match['score'] * 100,
                'keyword_density': self.weights['keyword_density'] * keyword_density * 100
            }
        }
    
    def generate_recommendations(self, skill_match: Dict, experience_match: Dict) -> List[str]:
        """
        Generate recommendations for improvement
        
        Args:
            skill_match: Skill matching results
            experience_match: Experience matching results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Skill recommendations
        if skill_match['missing_skills']:
            top_missing = skill_match['missing_skills'][:5]
            recommendations.append(f"Add these key skills: {', '.join(top_missing)}")
        
        # Experience recommendations
        if not experience_match['meets_requirement']:
            diff = abs(experience_match['difference'])
            recommendations.append(f"Highlight {diff} more years of relevant experience or equivalent projects")
        
        # General recommendations
        if skill_match['match_ratio'] < 0.5:
            recommendations.append("Consider adding more relevant technical skills")
        
        if not recommendations:
            recommendations.append("Great profile! Consider highlighting specific achievements with metrics")
        
        return recommendations


# Test function
def test_matching_engine():
    """Test matching engine"""
    
    print("Testing Matching Engine")
    print("="*60)
    
    engine = MatchingEngine()
    
    # Test data
    resume_skills = ["Python", "TensorFlow", "AWS", "Docker", "PostgreSQL"]
    jd_skills = ["Python", "TensorFlow", "PyTorch", "AWS", "Kubernetes"]
    
    # Test skill matching
    skill_match = engine.calculate_skill_match(resume_skills, jd_skills)
    print(f"\n✓ Skill Match Score: {skill_match['score']:.2f}")
    print(f"  Matched: {skill_match['matched_count']}/{skill_match['required_count']}")
    print(f"  Missing: {', '.join(skill_match['missing_skills'])}")
    
    # Test experience matching
    exp_match = engine.calculate_experience_match(5, {'mentioned': True, 'min_years': 3})
    print(f"\n✓ Experience Match Score: {exp_match['score']:.2f}")
    print(f"  Meets requirement: {exp_match['meets_requirement']}")
    
    # Test overall matching
    overall = engine.calculate_overall_match(
        semantic_similarity=0.85,
        skill_match=skill_match,
        experience_match=exp_match,
        education_match={'score': 1.0},
        keyword_density=0.60
    )
    
    print(f"\n✓ Overall Match: {overall['match_percentage']:.1f}%")
    print(f"  Level: {overall['match_level']}")
    
    print("\n✅ Matching engine working correctly!")


if __name__ == "__main__":
    test_matching_engine()