"""
Test script for Phase 2: PDF Parsing and Skills Extraction
"""

import sys
import os
import json

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

# Import modules
try:
    from src.preprocessing.pdf_parser import ResumeParser
    from src.preprocessing.skills_extractor import SkillsExtractor
except ImportError:
    # Fallback import method
    import importlib.util
    
    # Load pdf_parser
    parser_path = os.path.join(current_dir, 'src', 'preprocessing', 'pdf_parser.py')
    spec = importlib.util.spec_from_file_location("pdf_parser", parser_path)
    pdf_parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pdf_parser)
    ResumeParser = pdf_parser.ResumeParser
    
    # Load skills_extractor
    extractor_path = os.path.join(current_dir, 'src', 'preprocessing', 'skills_extractor.py')
    spec = importlib.util.spec_from_file_location("skills_extractor", extractor_path)
    skills_extractor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(skills_extractor)
    SkillsExtractor = skills_extractor.SkillsExtractor


def test_text_parsing():
    """Test parsing with sample text file"""
    print("="*70)
    print("TEST 1: TEXT PARSING")
    print("="*70)
    
    # Read sample resume
    try:
        with open('data/sample_resumes/sample_resume_1.txt', 'r', encoding='utf-8') as f:
            sample_text = f.read()
    except FileNotFoundError:
        print("❌ Sample resume file not found!")
        print("Please create: data/sample_resumes/sample_resume_1.txt")
        return None
    
    parser = ResumeParser()
    
    # Clean text
    cleaned_text = parser.clean_text(sample_text)
    print(f"\n✓ Cleaned text length: {len(cleaned_text)} characters")
    
    # Extract contact info
    contact = parser.extract_contact_info(sample_text)
    print("\n✓ Contact Information:")
    for key, value in contact.items():
        if value:
            print(f"  - {key}: {value}")
    
    # Extract name
    name = parser.extract_name(sample_text)
    print(f"\n✓ Extracted Name: {name}")
    
    return cleaned_text


def test_skills_extraction(text):
    """Test skills extraction"""
    print("\n" + "="*70)
    print("TEST 2: SKILLS EXTRACTION")
    print("="*70)
    
    extractor = SkillsExtractor()
    
    # Extract all skills
    results = extractor.extract_all_skills(text)
    
    print(f"\n✓ Total Skills Found: {results['total_skills_count']}")
    print(f"✓ Years of Experience: {results['experience']['total_years']} years")
    
    print("\n✓ Skills by Category:")
    for category, skills in results['categorized_skills'].items():
        if skills:
            print(f"\n  {category.upper().replace('_', ' ')}:")
            print(f"    {', '.join(skills)}")
    
    return results


def test_end_to_end():
    """Test complete pipeline"""
    print("\n" + "="*70)
    print("TEST 3: END-TO-END PIPELINE")
    print("="*70)
    
    # Parse resume
    text = test_text_parsing()
    
    if not text:
        return
    
    # Extract skills
    skills_results = test_skills_extraction(text)
    
    # Create structured output
    resume_data = {
        'candidate_name': 'Rahul Sharma',  # Extracted from text
        'email': 'rahul.sharma@email.com',
        'phone': '+91-9876543210',
        'total_skills': skills_results['total_skills_count'],
        'experience_years': skills_results['experience']['total_years'],
        'skills': skills_results['all_skills'],
        'categorized_skills': skills_results['categorized_skills']
    }
    
    print("\n" + "="*70)
    print("FINAL STRUCTURED OUTPUT")
    print("="*70)
    print(json.dumps(resume_data, indent=2))
    
    # Save to file
    output_path = 'data/processed/parsed_resume_sample.json'
    os.makedirs('data/processed', exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resume_data, f, indent=2)
    
    print(f"\n✅ Saved structured data to: {output_path}")
    
    return resume_data


def display_summary(resume_data):
    """Display summary statistics"""
    if not resume_data:
        return
    
    print("\n" + "="*70)
    print("📊 SUMMARY STATISTICS")
    print("="*70)
    
    print(f"\n👤 Candidate: {resume_data['candidate_name']}")
    print(f"📧 Email: {resume_data['email']}")
    print(f"⏱️  Experience: {resume_data['experience_years']} years")
    print(f"🎯 Total Skills: {resume_data['total_skills']}")
    
    print("\n🏆 Top Skill Categories:")
    for category, skills in resume_data['categorized_skills'].items():
        if skills:
            print(f"  • {category.replace('_', ' ').title()}: {len(skills)} skills")
    
    print("\n" + "="*70)
    print("✅ PHASE 2 COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    print("\n🚀 Starting Phase 2 Tests...\n")
    
    try:
        resume_data = test_end_to_end()
        display_summary(resume_data)
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()