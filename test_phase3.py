"""
Test Phase 3: Embeddings and Matching
Complete end-to-end test of the matching system
"""

import sys
import os
import json

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

# Import all modules
try:
    from src.preprocessing.pdf_parser import ResumeParser
    from src.preprocessing.skills_extractor import SkillsExtractor
    from src.preprocessing.jd_parser import JobDescriptionParser
    from src.models.embedding_engine import EmbeddingEngine
    from src.models.matching_engine import MatchingEngine
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all files are in the correct locations")
    sys.exit(1)


def load_sample_data():
    """Load sample resume and job description"""
    print("="*70)
    print("STEP 1: Loading Sample Data")
    print("="*70)
    
    # Load resume
    try:
        with open('data/sample_resumes/sample_resume_1.txt', 'r', encoding='utf-8') as f:
            resume_text = f.read()
        print("✓ Resume loaded")
    except FileNotFoundError:
        print("❌ Resume file not found")
        return None, None
    
    # Load job description
    try:
        with open('data/sample_jds/sample_job_1.txt', 'r', encoding='utf-8') as f:
            jd_text = f.read()
        print("✓ Job description loaded")
    except FileNotFoundError:
        print("❌ Job description file not found")
        return resume_text, None
    
    return resume_text, jd_text


def parse_data(resume_text, jd_text):
    """Parse resume and job description"""
    print("\n" + "="*70)
    print("STEP 2: Parsing Data")
    print("="*70)
    
    # Parse resume
    print("\n📄 Parsing Resume...")
    resume_parser = ResumeParser()
    skills_extractor = SkillsExtractor()
    
    cleaned_resume = resume_parser.clean_text(resume_text)
    contact_info = resume_parser.extract_contact_info(cleaned_resume)
    skills_data = skills_extractor.extract_all_skills(cleaned_resume)
    
    resume_data = {
        'cleaned_text': cleaned_resume,
        'name': resume_parser.extract_name(cleaned_resume),
        'email': contact_info['email'],
        'all_skills': skills_data['all_skills'],
        'experience_years': skills_data['experience']['total_years'],
        'categorized_skills': skills_data['categorized_skills']
    }
    
    print(f"  ✓ Candidate: {resume_data['name']}")
    print(f"  ✓ Skills found: {len(resume_data['all_skills'])}")
    print(f"  ✓ Experience: {resume_data['experience_years']} years")
    
    # Parse job description
    print("\n💼 Parsing Job Description...")
    jd_parser = JobDescriptionParser()
    jd_data = jd_parser.parse_job_description(jd_text)
    
    print(f"  ✓ Job Title: {jd_data['job_title']}")
    print(f"  ✓ Company: {jd_data['company']}")
    print(f"  ✓ Required Skills: {len(jd_data['all_required_skills'])}")
    print(f"  ✓ Experience Required: {jd_data['experience_required']['min_years']}+ years")
    
    return resume_data, jd_data


def create_embeddings(resume_data, jd_data):
    """Create embeddings"""
    print("\n" + "="*70)
    print("STEP 3: Creating AI Embeddings")
    print("="*70)
    
    embedding_engine = EmbeddingEngine()
    
    print("\n🤖 Generating embeddings...")
    resume_embedding = embedding_engine.create_resume_embedding(resume_data)
    jd_embedding = embedding_engine.create_jd_embedding(jd_data)
    
    print(f"  ✓ Resume embedding: {resume_embedding.shape}")
    print(f"  ✓ JD embedding: {jd_embedding.shape}")
    
    # Calculate semantic similarity
    semantic_similarity = embedding_engine.compute_similarity(resume_embedding, jd_embedding)
    print(f"\n  ✓ Semantic Similarity: {semantic_similarity:.3f}")
    
    return semantic_similarity, embedding_engine


def perform_matching(resume_data, jd_data, semantic_similarity):
    """Perform comprehensive matching"""
    print("\n" + "="*70)
    print("STEP 4: Performing Match Analysis")
    print("="*70)
    
    matcher = MatchingEngine()
    
    # Skill matching
    print("\n🎯 Analyzing Skills...")
    skill_match = matcher.calculate_skill_match(
        resume_data['all_skills'],
        jd_data['all_required_skills']
    )
    
    print(f"  ✓ Skill Match: {skill_match['score']*100:.1f}%")
    print(f"  ✓ Matched Skills: {skill_match['matched_count']}/{skill_match['required_count']}")
    print(f"  ✓ Matched: {', '.join(skill_match['matched_skills'][:10])}")
    if skill_match['missing_skills']:
        print(f"  ✓ Missing: {', '.join(skill_match['missing_skills'][:5])}")
    
    # Experience matching
    print("\n⏱️  Analyzing Experience...")
    exp_match = matcher.calculate_experience_match(
        resume_data['experience_years'],
        jd_data['experience_required']
    )
    
    print(f"  ✓ Experience Match: {exp_match['score']*100:.1f}%")
    print(f"  ✓ Candidate: {exp_match['candidate_years']} years")
    print(f"  ✓ Required: {exp_match['required_years']}+ years")
    print(f"  ✓ Meets Requirement: {exp_match['meets_requirement']}")
    
    # Education matching
    print("\n🎓 Analyzing Education...")
    edu_match = matcher.calculate_education_match(
        resume_data['cleaned_text'],
        jd_data['education_requirements']
    )
    print(f"  ✓ Education Match: {edu_match['score']*100:.1f}%")
    
    # Keyword density
    print("\n📝 Analyzing Keywords...")
    keyword_density = matcher.calculate_keyword_density(
        resume_data['cleaned_text'],
        jd_data['cleaned_text']
    )
    print(f"  ✓ Keyword Density: {keyword_density*100:.1f}%")
    
    # Overall matching
    print("\n" + "="*70)
    print("STEP 5: Computing Overall Match Score")
    print("="*70)
    
    overall_match = matcher.calculate_overall_match(
        semantic_similarity,
        skill_match,
        exp_match,
        edu_match,
        keyword_density
    )
    
    print(f"\n🎯 OVERALL MATCH: {overall_match['match_percentage']:.1f}%")
    print(f"📊 Match Level: {overall_match['match_level']}")
    
    print("\n📈 Component Breakdown:")
    for component, score in overall_match['weighted_contributions'].items():
        bar_length = int(score / 2)
        bar = "█" * bar_length
        print(f"  {component:25} {bar} {score:.1f}%")
    
    # Generate recommendations
    recommendations = matcher.generate_recommendations(skill_match, exp_match)
    
    print("\n💡 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    return {
        'overall_match': overall_match,
        'skill_match': skill_match,
        'experience_match': exp_match,
        'education_match': edu_match,
        'keyword_density': keyword_density,
        'recommendations': recommendations
    }


def save_results(resume_data, jd_data, match_results):
    """Save complete results to JSON"""
    print("\n" + "="*70)
    print("STEP 6: Saving Results")
    print("="*70)
    
    output = {
        'candidate': {
            'name': resume_data['name'],
            'email': resume_data['email'],
            'experience_years': resume_data['experience_years'],
            'total_skills': len(resume_data['all_skills']),
            'skills': resume_data['all_skills']
        },
        'job': {
            'title': jd_data['job_title'],
            'company': jd_data['company'],
            'required_skills': jd_data['all_required_skills'],
            'experience_required': jd_data['experience_required']['min_years']
        },
        'match_analysis': {
            'overall_score': match_results['overall_match']['match_percentage'],
            'match_level': match_results['overall_match']['match_level'],
            'skill_match_percentage': match_results['skill_match']['score'] * 100,
            'experience_match_percentage': match_results['experience_match']['score'] * 100,
            'matched_skills': match_results['skill_match']['matched_skills'],
            'missing_skills': match_results['skill_match']['missing_skills'],
            'recommendations': match_results['recommendations']
        }
    }
    
    output_path = 'data/processed/match_results.json'
    os.makedirs('data/processed', exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Results saved to: {output_path}")


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("🚀 PHASE 3: COMPLETE MATCHING SYSTEM TEST")
    print("="*70 + "\n")
    
    try:
        # Step 1: Load data
        resume_text, jd_text = load_sample_data()
        if not resume_text or not jd_text:
            return
        
        # Step 2: Parse data
        resume_data, jd_data = parse_data(resume_text, jd_text)
        
        # Step 3: Create embeddings
        semantic_similarity, _ = create_embeddings(resume_data, jd_data)
        
        # Step 4: Perform matching
        match_results = perform_matching(resume_data, jd_data, semantic_similarity)
        
        # Step 5: Save results
        save_results(resume_data, jd_data, match_results)
        
        # Final summary
        print("\n" + "="*70)
        print("✅ PHASE 3 COMPLETE!")
        print("="*70)
        print("\nWhat you've built:")
        print("  ✓ Resume parsing and skills extraction")
        print("  ✓ Job description parsing")
        print("  ✓ AI-powered semantic matching")
        print("  ✓ Multi-factor scoring system")
        print("  ✓ Skill gap analysis")
        print("  ✓ Intelligent recommendations")
        
        print("\n📊 Next Steps:")
        print("  1. Build the Streamlit UI (Phase 4)")
        print("  2. Add ATS scoring system")
        print("  3. Deploy to Hugging Face Spaces")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()