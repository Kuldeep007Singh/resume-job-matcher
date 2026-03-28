"""
PDF Resume Parser
Extracts text from PDF resumes with multiple fallback methods
"""

import pdfplumber
import PyPDF2
import re
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse PDF resumes and extract structured information"""
    
    def __init__(self):
        self.text = ""
        self.metadata = {}
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (primary method)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
            return ""
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2 (fallback method)"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            logger.warning(f"PyPDF2 failed: {e}")
            return ""
    
    def parse_pdf(self, pdf_path: str) -> str:
        """
        Parse PDF with fallback mechanisms
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        # Try pdfplumber first (better formatting)
        text = self.extract_text_pdfplumber(pdf_path)
        
        # Fallback to PyPDF2
        if not text or len(text) < 50:
            logger.info("Trying fallback method...")
            text = self.extract_text_pypdf2(pdf_path)
        
        if not text or len(text) < 50:
            raise ValueError("Could not extract sufficient text from PDF")
        
        self.text = text
        return text
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s@.+\-,():/]', '', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information from text
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with email, phone, linkedin
        """
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phone (Indian and international formats)
        phone_patterns = [
            r'\+91[-.\s]?\d{10}',  # +91 format
            r'\d{10}',  # 10 digit
            r'\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # 123-456-7890
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = phones[0]
                break
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            contact_info['linkedin'] = linkedin[0]
        
        # Extract GitHub
        github_pattern = r'github\.com/[\w-]+'
        github = re.findall(github_pattern, text.lower())
        if github:
            contact_info['github'] = github[0]
        
        return contact_info
    
    def extract_name(self, text: str) -> Optional[str]:
        """
        Extract candidate name (heuristic: first line or first capitalized phrase)
        
        Args:
            text: Resume text
            
        Returns:
            Candidate name
        """
        lines = text.split('\n')
        
        # Try first few lines
        for line in lines[:5]:
            line = line.strip()
            # Check if line looks like a name (2-4 words, all capitalized)
            words = line.split()
            if 2 <= len(words) <= 4:
                if all(word[0].isupper() for word in words if word):
                    return line
        
        return None
    
    def parse_resume(self, pdf_path: str) -> Dict:
        """
        Complete resume parsing pipeline
        
        Args:
            pdf_path: Path to PDF resume
            
        Returns:
            Dictionary with structured resume data
        """
        # Extract text
        raw_text = self.parse_pdf(pdf_path)
        
        # Clean text
        cleaned_text = self.clean_text(raw_text)
        
        # Extract structured information
        contact_info = self.extract_contact_info(cleaned_text)
        name = self.extract_name(cleaned_text)
        
        result = {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'name': name,
            'email': contact_info['email'],
            'phone': contact_info['phone'],
            'linkedin': contact_info['linkedin'],
            'github': contact_info['github'],
        }
        
        logger.info(f"Successfully parsed resume. Text length: {len(cleaned_text)} chars")
        return result


# Test function
def test_parser():
    """Test the parser with a sample PDF"""
    parser = ResumeParser()
    
    # Test text cleaning
    sample_text = """
    John   Doe
    john.doe@email.com    |    +91-9876543210
    
    
    Skills:  Python,  Machine Learning, Deep Learning
    """
    
    cleaned = parser.clean_text(sample_text)
    print("Cleaned Text:")
    print(cleaned)
    print("\n" + "="*50 + "\n")
    
    # Test contact extraction
    contact = parser.extract_contact_info(sample_text)
    print("Contact Info:")
    print(contact)
    print("\n" + "="*50 + "\n")
    
    name = parser.extract_name(sample_text)
    print(f"Extracted Name: {name}")


if __name__ == "__main__":
    test_parser()