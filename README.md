# 📄 AI Resume Analyzer + Job Match System

An intelligent AI-powered system that analyzes resumes, matches them with job descriptions, and provides comprehensive insights using semantic understanding and multi-factor scoring.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🎯 Features

- **AI-Powered Matching**: Uses sentence transformers for semantic understanding
- **Multi-Factor Scoring**: Combines 5 different signals for accurate matching
- **Skills Analysis**: Extracts and categorizes technical and soft skills
- **Skill Gap Analysis**: Identifies matched, missing, and additional skills
- **Experience Matching**: Compares candidate experience with job requirements
- **Visual Dashboards**: Interactive charts and metrics
- **ATS Score**: Keyword density and formatting analysis
- **Recommendations**: Personalized suggestions for improvement
- **PDF Support**: Parses resume PDFs automatically
- **Export Reports**: Download analysis results as JSON

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.8+**: Main programming language
- **Streamlit**: Web UI framework
- **Sentence Transformers**: AI embeddings (all-MiniLM-L6-v2)
- **spaCy**: NLP and entity extraction
- **FAISS**: Vector similarity search

### Libraries
- **PDF Processing**: PyPDF2, pdfplumber
- **Data**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib, Seaborn
- **ML/AI**: Transformers, Scikit-learn

## 📊 How It Works

### 1. **Resume Processing**
```
PDF/Text → Parse → Clean → Extract Skills/Contact → Structure Data
```

### 2. **Job Description Analysis**
```
JD Text → Parse → Extract Requirements → Identify Must-Haves
```

### 3. **AI Embedding**
```
Resume + JD → Sentence Transformer → 384D Vectors → Cosine Similarity
```

### 4. **Multi-Factor Scoring**
```python
Overall Score = 
  40% Semantic Similarity (AI understanding)
  30% Skill Match (exact matches)
  15% Experience Match (years)
  10% Education Match (degree)
  05% Keyword Density (ATS)
```

### 5. **Results & Recommendations**
```
Match Score → Skill Gaps → Recommendations → Visual Dashboard
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 2GB free disk space (for models)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/resume-job-matcher.git
cd resume-job-matcher
```

2. **Create virtual environment**
```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. **Run the app**
```bash
streamlit run app.py
```

5. **Open browser**
```
Navigate to: http://localhost:8501
```

## 📁 Project Structure

```
resume-job-matcher/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
├── data/
│   ├── sample_resumes/        # Sample resume files
│   ├── sample_jds/            # Sample job descriptions
│   ├── processed/             # Processed outputs
│   └── skills_db/             # Skills database
│       └── skills_database.json
├── src/
│   ├── preprocessing/
│   │   ├── pdf_parser.py     # PDF extraction
│   │   ├── skills_extractor.py # Skills extraction
│   │   └── jd_parser.py      # JD parsing
│   └── models/
│       ├── embedding_engine.py # AI embeddings
│       └── matching_engine.py  # Matching logic
├── tests/
│   ├── test_phase2.py
│   └── test_phase3.py
└── demo/
    └── screenshots/           # Demo images
```

## 💻 Usage

### Basic Usage

1. **Launch the app**
```bash
streamlit run app.py
```

2. **Upload Resume**
   - Click "Upload Resume" and select PDF
   - Or paste resume text directly

3. **Add Job Description**
   - Paste job description in text area

4. **Analyze**
   - Click "🚀 Analyze Match"
   - View results in dashboard

### Advanced Usage

**Batch Processing (Coming Soon)**
```python
from src.models.matching_engine import MatchingEngine

# Process multiple resumes
for resume in resumes:
    score = matcher.match(resume, job_description)
```

## 📈 Scoring Methodology

### Overall Match Score
The system calculates a comprehensive match score using weighted components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Semantic Similarity | 40% | AI-based contextual understanding |
| Skill Match | 30% | Exact technical skill matches |
| Experience Match | 15% | Years of experience alignment |
| Education Match | 10% | Degree requirements |
| Keyword Density | 5% | ATS-style keyword presence |

### Match Levels
- **80-100%**: Excellent Match 🟢
- **60-79%**: Good Match 🔵
- **40-59%**: Fair Match 🟡
- **0-39%**: Poor Match 🔴

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ End-to-end ML pipeline development
- ✅ NLP and text processing
- ✅ AI embeddings and semantic search
- ✅ Production-grade code structure
- ✅ UI/UX design with Streamlit
- ✅ Deployment and MLOps basics

## 🚀 Deployment

### Deploy to Hugging Face Spaces

1. **Create account**: [huggingface.co/join](https://huggingface.co/join)

2. **Create new Space**
   - Click "New Space"
   - Name: `resume-analyzer`
   - SDK: Streamlit
   - Visibility: Public

3. **Push code**
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/resume-analyzer
git push hf main
```

4. **Add files**
   - Upload `packages.txt`
   - Upload `setup.sh`
   - Wait for build (5-10 minutes)

5. **Access your app**
```
https://huggingface.co/spaces/YOUR_USERNAME/resume-analyzer
```

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Visit [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect GitHub repository
4. Deploy!

## 🧪 Testing

Run comprehensive tests:

```bash
# Test Phase 2: Parsing
python test_phase2.py

# Test Phase 3: Matching
python test_phase3.py

# Test individual modules
python src/preprocessing/pdf_parser.py
python src/models/embedding_engine.py
```

## 🔮 Future Enhancements

- [ ] ATS score-only mode (no JD required)
- [ ] Batch resume processing
- [ ] Resume improvement suggestions (GPT integration)
- [ ] Multi-language support (Hindi, Tamil, etc.)
- [ ] LinkedIn profile analysis
- [ ] Video resume analysis
- [ ] Interview question generator
- [ ] Salary prediction
- [ ] Job recommendation system

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/Kuldeep007Singh)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Sentence Transformers by Hugging Face
- spaCy for NLP capabilities
- Streamlit for amazing UI framework
- Open source community

## 📞 Support

For issues, questions, or suggestions:
- 🐛 [Report Bug](https://github.com/yourusername/resume-job-matcher/issues)
- 💡 [Request Feature](https://github.com/yourusername/resume-job-matcher/issues)
- 📧 Email: your.email@example.com

---

⭐ **Star this repo if you find it helpful!**

Made with ❤️ and Python