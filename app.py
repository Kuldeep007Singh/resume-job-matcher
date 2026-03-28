"""
AI Resume Analyzer - Streamlit UI
Main application interface
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'src'))

# Import modules
from src.preprocessing.pdf_parser import ResumeParser
from src.preprocessing.skills_extractor import SkillsExtractor
from src.preprocessing.jd_parser import JobDescriptionParser
from src.models.embedding_engine import EmbeddingEngine
from src.models.matching_engine import MatchingEngine

import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_models():
    """Load all models (cached for performance)"""
    with st.spinner("🔄 Loading AI models..."):
        embedding_engine = EmbeddingEngine()
        matcher = MatchingEngine()
    return embedding_engine, matcher


def create_gauge_chart(score, title):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#ffcccc'},
                {'range': [40, 60], 'color': '#fff4cc'},
                {'range': [60, 80], 'color': '#cce5ff'},
                {'range': [80, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_skills_chart(matched, missing, additional):
    """Create skills comparison chart"""
    fig = go.Figure(data=[
        go.Bar(name='Matched', x=['Skills'], y=[len(matched)], marker_color='#28a745'),
        go.Bar(name='Missing', x=['Skills'], y=[len(missing)], marker_color='#dc3545'),
        go.Bar(name='Additional', x=['Skills'], y=[len(additional)], marker_color='#17a2b8')
    ])
    
    fig.update_layout(
        title="Skills Breakdown",
        barmode='group',
        height=300,
        xaxis_title="",
        yaxis_title="Number of Skills"
    )
    
    return fig


def create_component_scores_chart(scores):
    """Create component scores breakdown"""
    components = list(scores.keys())
    values = [scores[comp] for comp in components]
    
    # Clean up names
    components = [c.replace('_', ' ').title() for c in components]
    
    fig = go.Figure(data=[
        go.Bar(
            x=components,
            y=values,
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            text=[f'{v:.1f}%' for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Match Score Breakdown",
        xaxis_title="Component",
        yaxis_title="Contribution (%)",
        height=400,
        showlegend=False
    )
    
    return fig


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">📄 AI Resume Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Match resumes with job descriptions using AI</div>', unsafe_allow_html=True)
    
    # Load models
    embedding_engine, matcher = load_models()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/200/resume.png", width=150)
        st.title("⚙️ Configuration")
        
        analysis_mode = st.radio(
            "Select Mode:",
            ["📄 Resume + Job Description", "📄 Resume Only (ATS Score)"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.info(
            "This tool uses AI to analyze resumes and match them with job descriptions. "
            "Upload a resume and job description to get detailed insights!"
        )
        
        st.markdown("### 🎯 Features")
        st.markdown("""
        - ✅ AI-powered semantic matching
        - ✅ Skill gap analysis
        - ✅ ATS score calculation
        - ✅ Personalized recommendations
        - ✅ Visual dashboards
        """)
    
    # Main content
    if "📄 Resume + Job Description" in analysis_mode:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Upload Resume")
            resume_file = st.file_uploader(
                "Choose a PDF or paste text",
                type=['pdf', 'txt'],
                key="resume"
            )
            
            resume_text_input = st.text_area(
                "Or paste resume text here:",
                height=200,
                key="resume_text"
            )
        
        with col2:
            st.subheader("💼 Job Description")
            jd_text = st.text_area(
                "Paste job description here:",
                height=300,
                key="jd_text"
            )
        
        # Analyze button
        if st.button("🚀 Analyze Match", type="primary"):
            # Get resume text
            resume_text = None
            
            if resume_file is not None:
                if resume_file.type == "application/pdf":
                    # Save temporarily
                    temp_path = f"temp_{resume_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(resume_file.getbuffer())
                    
                    # Parse PDF
                    with st.spinner("📖 Reading resume..."):
                        parser = ResumeParser()
                        try:
                            resume_text = parser.parse_pdf(temp_path)
                            os.remove(temp_path)
                        except Exception as e:
                            st.error(f"Error reading PDF: {e}")
                            os.remove(temp_path)
                            return
                else:
                    resume_text = resume_file.read().decode('utf-8')
            
            elif resume_text_input:
                resume_text = resume_text_input
            
            # Validate inputs
            if not resume_text:
                st.error("❌ Please upload a resume or paste resume text!")
                return
            
            if not jd_text:
                st.error("❌ Please paste a job description!")
                return
            
            # Process
            with st.spinner("🤖 Analyzing with AI..."):
                # Parse resume
                resume_parser = ResumeParser()
                skills_extractor = SkillsExtractor()
                
                cleaned_resume = resume_parser.clean_text(resume_text)
                contact_info = resume_parser.extract_contact_info(cleaned_resume)
                skills_data = skills_extractor.extract_all_skills(cleaned_resume)
                
                resume_data = {
                    'cleaned_text': cleaned_resume,
                    'name': resume_parser.extract_name(cleaned_resume) or "Candidate",
                    'email': contact_info['email'],
                    'all_skills': skills_data['all_skills'],
                    'experience_years': skills_data['experience']['total_years'],
                    'categorized_skills': skills_data['categorized_skills']
                }
                
                # Parse JD
                jd_parser = JobDescriptionParser()
                jd_data = jd_parser.parse_job_description(jd_text)
                
                # Create embeddings
                resume_embedding = embedding_engine.create_resume_embedding(resume_data)
                jd_embedding = embedding_engine.create_jd_embedding(jd_data)
                semantic_similarity = embedding_engine.compute_similarity(resume_embedding, jd_embedding)
                
                # Perform matching
                skill_match = matcher.calculate_skill_match(
                    resume_data['all_skills'],
                    jd_data['all_required_skills']
                )
                
                exp_match = matcher.calculate_experience_match(
                    resume_data['experience_years'],
                    jd_data['experience_required']
                )
                
                edu_match = matcher.calculate_education_match(
                    resume_data['cleaned_text'],
                    jd_data['education_requirements']
                )
                
                keyword_density = matcher.calculate_keyword_density(
                    resume_data['cleaned_text'],
                    jd_data['cleaned_text']
                )
                
                overall_match = matcher.calculate_overall_match(
                    semantic_similarity,
                    skill_match,
                    exp_match,
                    edu_match,
                    keyword_density
                )
                
                recommendations = matcher.generate_recommendations(skill_match, exp_match)
            
            # Display results
            st.success("✅ Analysis Complete!")
            
            st.markdown("---")
            
            # Overall score
            st.subheader("🎯 Overall Match Score")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.plotly_chart(
                    create_gauge_chart(overall_match['match_percentage'], "Match Score"),
                    use_container_width=True
                )
            
            with col2:
                st.metric(
                    "Match Level",
                    overall_match['match_level'],
                    delta=None
                )
                st.metric(
                    "Skills Matched",
                    f"{skill_match['matched_count']}/{skill_match['required_count']}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Experience",
                    f"{resume_data['experience_years']} years",
                    delta=None
                )
                st.metric(
                    "Required",
                    f"{jd_data['experience_required']['min_years']}+ years",
                    delta=None
                )
            
            # Component breakdown
            st.markdown("---")
            st.subheader("📊 Detailed Breakdown")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(
                    create_component_scores_chart(overall_match['weighted_contributions']),
                    use_container_width=True
                )
            
            with col2:
                st.plotly_chart(
                    create_skills_chart(
                        skill_match['matched_skills'],
                        skill_match['missing_skills'],
                        skill_match['additional_skills']
                    ),
                    use_container_width=True
                )
            
            # Skills details
            st.markdown("---")
            st.subheader("🎯 Skills Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**✅ Matched Skills**")
                if skill_match['matched_skills']:
                    for skill in skill_match['matched_skills'][:10]:
                        st.markdown(f"- {skill}")
                else:
                    st.info("No matched skills")
            
            with col2:
                st.markdown("**❌ Missing Skills**")
                if skill_match['missing_skills']:
                    for skill in skill_match['missing_skills'][:10]:
                        st.markdown(f"- {skill}")
                else:
                    st.success("No missing skills!")
            
            with col3:
                st.markdown("**➕ Additional Skills**")
                if skill_match['additional_skills']:
                    for skill in skill_match['additional_skills'][:10]:
                        st.markdown(f"- {skill}")
                else:
                    st.info("No additional skills")
            
            # Recommendations
            st.markdown("---")
            st.subheader("💡 Recommendations")
            
            for i, rec in enumerate(recommendations, 1):
                st.info(f"**{i}.** {rec}")
            
            # Download report
            st.markdown("---")
            
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'candidate_name': resume_data['name'],
                'job_title': jd_data['job_title'],
                'overall_score': overall_match['match_percentage'],
                'match_level': overall_match['match_level'],
                'matched_skills': skill_match['matched_skills'],
                'missing_skills': skill_match['missing_skills'],
                'recommendations': recommendations
            }
            
            st.download_button(
                label="📥 Download Report (JSON)",
                data=json.dumps(report_data, indent=2),
                file_name=f"match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    else:
        # ATS Score mode (Resume only)
        st.subheader("📄 Upload Resume for ATS Analysis")
        
        resume_file = st.file_uploader(
            "Choose a PDF or paste text",
            type=['pdf', 'txt'],
            key="resume_ats"
        )
        
        resume_text_input = st.text_area(
            "Or paste resume text here:",
            height=300,
            key="resume_text_ats"
        )
        
        if st.button("🚀 Analyze Resume", type="primary"):
            st.info("🚧 ATS-only mode coming soon! For now, use Resume + Job Description mode.")


if __name__ == "__main__":
    main()