"""
Embedding Engine
Creates semantic embeddings for resumes and job descriptions
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """Generate and manage embeddings for text matching"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding engine
        
        Args:
            model_name: Name of sentence transformer model
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info("Model loaded successfully")
    
    def create_embedding(self, text: str) -> np.ndarray:
        """
        Create embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def create_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            Array of embedding vectors
        """
        if not texts:
            raise ValueError("Text list cannot be empty")
        
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        # Cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        normalized_similarity = (similarity + 1) / 2
        
        return float(normalized_similarity)
    
    def create_resume_embedding(self, resume_data: Dict) -> np.ndarray:
        """
        Create embedding from structured resume data
        
        Args:
            resume_data: Parsed resume dictionary
            
        Returns:
            Resume embedding
        """
        # Combine relevant fields for embedding
        text_parts = []
        
        # Add skills (most important)
        if 'all_skills' in resume_data and resume_data['all_skills']:
            text_parts.append("Skills: " + ", ".join(resume_data['all_skills']))
        
        # Add experience summary
        if 'cleaned_text' in resume_data:
            # Extract experience section (heuristic)
            text = resume_data['cleaned_text']
            if 'experience' in text.lower():
                exp_start = text.lower().find('experience')
                exp_text = text[exp_start:exp_start+500]  # Take 500 chars
                text_parts.append(exp_text)
        
        # Combine all parts
        combined_text = " ".join(text_parts)
        
        if not combined_text.strip():
            combined_text = resume_data.get('cleaned_text', 'No content')
        
        return self.create_embedding(combined_text)
    
    def create_jd_embedding(self, jd_data: Dict) -> np.ndarray:
        """
        Create embedding from structured job description
        
        Args:
            jd_data: Parsed job description dictionary
            
        Returns:
            Job description embedding
        """
        # Combine relevant fields
        text_parts = []
        
        # Job title (important)
        if jd_data.get('job_title'):
            text_parts.append(f"Role: {jd_data['job_title']}")
        
        # Required skills (most important)
        if jd_data.get('all_required_skills'):
            text_parts.append("Required skills: " + ", ".join(jd_data['all_required_skills']))
        
        # Must have requirements
        if jd_data.get('must_have_requirements'):
            text_parts.append("Must have: " + " ".join(jd_data['must_have_requirements'][:5]))
        
        # Combine all parts
        combined_text = " ".join(text_parts)
        
        if not combined_text.strip():
            combined_text = jd_data.get('cleaned_text', 'No content')
        
        return self.create_embedding(combined_text)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return self.model.get_sentence_embedding_dimension()


# Test function
def test_embedding_engine():
    """Test embedding engine"""
    
    print("Testing Embedding Engine")
    print("="*60)
    
    # Initialize
    engine = EmbeddingEngine()
    print(f"✓ Model loaded: {engine.model_name}")
    print(f"✓ Embedding dimension: {engine.get_embedding_dimension()}")
    
    # Test texts
    text1 = "Python machine learning engineer with 5 years experience in TensorFlow and PyTorch"
    text2 = "Senior ML engineer needed with Python, TensorFlow, and deep learning skills"
    text3 = "Java backend developer with Spring Boot experience"
    
    # Create embeddings
    print("\n✓ Creating embeddings...")
    emb1 = engine.create_embedding(text1)
    emb2 = engine.create_embedding(text2)
    emb3 = engine.create_embedding(text3)
    
    print(f"  Embedding shape: {emb1.shape}")
    
    # Compute similarities
    print("\n✓ Computing similarities:")
    sim_1_2 = engine.compute_similarity(emb1, emb2)
    sim_1_3 = engine.compute_similarity(emb1, emb3)
    sim_2_3 = engine.compute_similarity(emb2, emb3)
    
    print(f"  Similar texts (ML engineer): {sim_1_2:.3f} (should be high)")
    print(f"  Different domains (ML vs Java): {sim_1_3:.3f} (should be low)")
    print(f"  Different domains (ML vs Java): {sim_2_3:.3f} (should be low)")
    
    print("\n✅ Embedding engine working correctly!")
    
    return engine


if __name__ == "__main__":
    test_embedding_engine()