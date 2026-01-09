"""
RAG (Retrieval-Augmented Generation) System
Combines vector database with LLM for fast, accurate responses.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional

# Install dependencies
print("Installing RAG dependencies...")
os.system("pip install -q chromadb sentence-transformers")

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class RAGSystem:
    """RAG system for knowledge-augmented responses."""
    
    def __init__(
        self,
        knowledge_base_path: str = "./knowledge_base",
        db_path: str = "./vector_db",
        embedding_model: str = "all-MiniLM-L6-v2"  # Small, fast model
    ):
        """
        Initialize RAG system.
        
        Args:
            knowledge_base_path: Path to knowledge base files
            db_path: Path to vector database
            embedding_model: Sentence transformer model for embeddings
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self.db_path = Path(db_path)
        
        # Initialize embedding model (small, fast)
        print("Loading embedding model...")
        self.embedder = SentenceTransformer(embedding_model)
        print(f"✓ Loaded: {embedding_model}")
        
        # Initialize ChromaDB
        print("Initializing vector database...")
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "Educational knowledge for children"}
        )
        print(f"✓ Vector DB ready: {self.collection.count()} documents")
    
    def add_knowledge(self, texts: List[str], metadatas: List[Dict] = None, ids: List[str] = None):
        """
        Add knowledge to the database.
        
        Args:
            texts: List of text chunks to add
            metadatas: Optional metadata for each chunk
            ids: Optional IDs for each chunk
        """
        if not texts:
            return
        
        # Generate IDs if not provided
        if ids is None:
            start_id = self.collection.count()
            ids = [f"doc_{start_id + i}" for i in range(len(texts))]
        
        # Generate embeddings
        print(f"Adding {len(texts)} documents...")
        embeddings = self.embedder.encode(texts, show_progress_bar=True).tolist()
        
        # Add to database
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas or [{} for _ in texts],
            ids=ids
        )
        
        print(f"✓ Added {len(texts)} documents. Total: {self.collection.count()}")
    
    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Search for relevant knowledge.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        # Generate query embedding
        query_embedding = self.embedder.encode([query])[0].tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return formatted_results
    
    def augment_prompt(self, question: str, emotion: str = "neutral", age: int = 9) -> str:
        """
        Augment question with retrieved knowledge.
        
        Args:
            question: User's question
            emotion: Detected emotion
            age: User's age
            
        Returns:
            Augmented prompt with context
        """
        # Search for relevant knowledge
        results = self.search(question, n_results=3)
        
        # Build context from results
        context = ""
        if results:
            context = "\n\nRelevant facts:\n"
            for i, result in enumerate(results, 1):
                context += f"{i}. {result['text']}\n"
        
        # Create augmented prompt
        prompt = f"""You are Mira, a friendly AI assistant for children.

Context: The child is {age} years old and seems {emotion}.

Question: {question}
{context}
Based on the facts above, provide a clear, age-appropriate answer:"""
        
        return prompt
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        return {
            "total_documents": self.collection.count(),
            "embedding_model": "all-MiniLM-L6-v2",
            "db_path": str(self.db_path)
        }


def demo():
    """Demo the RAG system."""
    print("="*60)
    print("RAG SYSTEM DEMO")
    print("="*60)
    
    # Initialize RAG
    rag = RAGSystem()
    
    # Add sample knowledge (you'll add 5GB later!)
    sample_knowledge = [
        "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar.",
        "The sky appears blue because of Rayleigh scattering. Shorter wavelengths of light (blue) scatter more than longer wavelengths (red) when sunlight passes through Earth's atmosphere.",
        "Gravity is a force that attracts objects with mass toward each other. The more massive an object, the stronger its gravitational pull.",
        "The water cycle describes how water evaporates from the surface, rises into the atmosphere, cools and condenses into clouds, and falls back to the surface as precipitation.",
        "Dinosaurs were reptiles that lived millions of years ago during the Mesozoic Era. They went extinct about 65 million years ago, possibly due to an asteroid impact.",
    ]
    
    sample_metadata = [
        {"topic": "biology", "difficulty": "medium"},
        {"topic": "physics", "difficulty": "medium"},
        {"topic": "physics", "difficulty": "easy"},
        {"topic": "earth_science", "difficulty": "easy"},
        {"topic": "paleontology", "difficulty": "easy"},
    ]
    
    if rag.collection.count() == 0:
        print("\nAdding sample knowledge...")
        rag.add_knowledge(sample_knowledge, sample_metadata)
    
    # Test searches
    print("\n" + "="*60)
    print("TEST SEARCHES")
    print("="*60)
    
    test_questions = [
        "Why is the sky blue?",
        "How do plants make food?",
        "What is gravity?",
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        results = rag.search(question, n_results=2)
        print("Retrieved knowledge:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['text'][:100]}...")
            print(f"     Relevance: {1 - result['distance']:.2f}")
    
    # Show augmented prompt
    print("\n" + "="*60)
    print("AUGMENTED PROMPT EXAMPLE")
    print("="*60)
    prompt = rag.augment_prompt("Why is the sky blue?", emotion="curious", age=9)
    print(prompt)
    
    print("\n" + "="*60)
    print("✓ RAG SYSTEM READY!")
    print("="*60)
    print(f"Documents in database: {rag.collection.count()}")
    print("\nNext steps:")
    print("1. Add more knowledge: python build_knowledge_base.py")
    print("2. Use with chat: python rag_chat.py")
    print("="*60)


if __name__ == "__main__":
    demo()
