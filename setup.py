"""
Project Setup Script
Run this after creating virtual environment to set up folder structure
"""

import os

def create_project_structure():
    """Create the complete project folder structure"""
    
    folders = [
        'data/sample_resumes',
        'data/sample_jds',
        'data/processed',
        'data/skills_db',
        'src/preprocessing',
        'src/models',
        'src/utils',
        'notebooks',
        'demo/screenshots',
        'tests',
    ]
    
    files = {
        'src/__init__.py': '',
        'src/preprocessing/__init__.py': '',
        'src/models/__init__.py': '',
        'src/utils/__init__.py': '',
        'tests/__init__.py': '',
        '.gitignore': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Data
data/processed/*
!data/processed/.gitkeep

# Models
models/
*.pkl
*.pt
*.pth

# OS
.DS_Store
Thumbs.db
''',
        'README.md': '''# AI Resume Analyzer + Job Match System

🚀 An intelligent system that analyzes resumes, matches them with job descriptions, and provides ATS scoring.

## 🎯 Features
- PDF Resume Parsing
- Skills Extraction (Technical & Soft Skills)
- Job-Resume Matching with AI
- ATS Score Calculation
- Skill Gap Analysis
- Improvement Suggestions

## 🛠️ Tech Stack
- Python 3.8+
- Sentence Transformers (Embeddings)
- spaCy (NLP)
- FAISS (Vector Search)
- Streamlit (UI)

## 📦 Installation

\`\`\`bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
\`\`\`

## 🚀 Usage

\`\`\`bash
streamlit run app.py
\`\`\`

## 📊 Project Status
🚧 Under Development

## 👤 Author
Your Name - [GitHub](https://github.com/Kuldeep007Singh)
''',
        'data/processed/.gitkeep': '',
    }
    
    # Create folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Created: {folder}")
    
    # Create files
    for filepath, content in files.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created: {filepath}")
    
    print("\n✅ Project structure created successfully!")
    print("\n📁 Your project structure:")
    print("""
resume-job-matcher/
├── data/
│   ├── sample_resumes/
│   ├── sample_jds/
│   ├── processed/
│   └── skills_db/
├── src/
│   ├── preprocessing/
│   ├── models/
│   └── utils/
├── notebooks/
├── demo/
│   └── screenshots/
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
    """)

if __name__ == "__main__":
    create_project_structure()