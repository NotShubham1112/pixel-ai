"""
Build a large knowledge base for RAG system.
Creates 5GB of educational content for accurate responses.
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import requests


class KnowledgeBaseBuilder:
    """Build comprehensive knowledge base from various sources."""
    
    def __init__(self, output_dir: str = "./knowledge_base"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.total_size = 0
    
    def add_wikipedia_summaries(self, topics: List[str]):
        """Add Wikipedia summaries for given topics."""
        print(f"\nFetching Wikipedia summaries for {len(topics)} topics...")
        
        summaries = []
        for topic in topics:
            try:
                # Wikipedia API
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    summary = {
                        "title": data.get("title", topic),
                        "text": data.get("extract", ""),
                        "source": "wikipedia",
                        "topic": topic
                    }
                    summaries.append(summary)
                    print(f"  ✓ {topic}")
                else:
                    print(f"  ✗ {topic} (not found)")
            except Exception as e:
                print(f"  ✗ {topic} ({e})")
        
        # Save
        output_file = self.output_dir / "wikipedia_summaries.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, indent=2, ensure_ascii=False)
        
        size = output_file.stat().st_size
        self.total_size += size
        print(f"✓ Saved {len(summaries)} summaries ({size/1024/1024:.1f} MB)")
    
    def add_educational_qa(self):
        """Add educational Q&A pairs."""
        print("\nGenerating educational Q&A...")
        
        # Sample educational content (expand this to 5GB!)
        qa_pairs = []
        
        # Science
        science_topics = {
            "Physics": [
                ("What is gravity?", "Gravity is a force that attracts objects with mass toward each other..."),
                ("How does electricity work?", "Electricity is the flow of electric charge through conductors..."),
                ("What is energy?", "Energy is the ability to do work or cause change..."),
            ],
            "Biology": [
                ("What is photosynthesis?", "Photosynthesis is how plants make food using sunlight..."),
                ("How does the heart work?", "The heart pumps blood throughout the body..."),
                ("What is DNA?", "DNA is the molecule that carries genetic information..."),
            ],
            "Chemistry": [
                ("What is an atom?", "An atom is the smallest unit of matter..."),
                ("What is a chemical reaction?", "A chemical reaction is when substances combine or break apart..."),
                ("What are the states of matter?", "Matter exists in solid, liquid, gas, and plasma states..."),
            ]
        }
        
        for subject, pairs in science_topics.items():
            for question, answer in pairs:
                qa_pairs.append({
                    "question": question,
                    "answer": answer,
                    "subject": subject,
                    "difficulty": "medium",
                    "age_group": "8-12"
                })
        
        # Math
        math_topics = [
            ("What is addition?", "Addition is combining two or more numbers to get a sum..."),
            ("What is multiplication?", "Multiplication is repeated addition..."),
            ("What is a fraction?", "A fraction represents a part of a whole..."),
        ]
        
        for question, answer in math_topics:
            qa_pairs.append({
                "question": question,
                "answer": answer,
                "subject": "Mathematics",
                "difficulty": "easy",
                "age_group": "6-10"
            })
        
        # Save
        output_file = self.output_dir / "educational_qa.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
        
        size = output_file.stat().st_size
        self.total_size += size
        print(f"✓ Saved {len(qa_pairs)} Q&A pairs ({size/1024:.1f} KB)")
    
    def add_common_knowledge(self):
        """Add common knowledge facts."""
        print("\nAdding common knowledge...")
        
        facts = [
            {"fact": "The Earth orbits the Sun once every 365.25 days.", "category": "astronomy"},
            {"fact": "Water boils at 100°C (212°F) at sea level.", "category": "physics"},
            {"fact": "The human body has 206 bones.", "category": "biology"},
            {"fact": "The speed of light is approximately 299,792 kilometers per second.", "category": "physics"},
            {"fact": "The Amazon rainforest produces about 20% of Earth's oxygen.", "category": "environment"},
            # Add thousands more...
        ]
        
        output_file = self.output_dir / "common_knowledge.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(facts, f, indent=2, ensure_ascii=False)
        
        size = output_file.stat().st_size
        self.total_size += size
        print(f"✓ Saved {len(facts)} facts ({size/1024:.1f} KB)")
    
    def build_from_text_files(self, text_dir: str):
        """Build knowledge base from text files."""
        print(f"\nProcessing text files from {text_dir}...")
        
        text_path = Path(text_dir)
        if not text_path.exists():
            print(f"  Directory not found: {text_dir}")
            return
        
        documents = []
        for file_path in text_path.glob("**/*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Split into chunks (for better retrieval)
                chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                for i, chunk in enumerate(chunks):
                    documents.append({
                        "text": chunk,
                        "source": str(file_path.name),
                        "chunk_id": i
                    })
        
        if documents:
            output_file = self.output_dir / "text_documents.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, ensure_ascii=False)
            
            size = output_file.stat().st_size
            self.total_size += size
            print(f"✓ Processed {len(documents)} chunks ({size/1024/1024:.1f} MB)")
    
    def get_stats(self):
        """Get knowledge base statistics."""
        print("\n" + "="*60)
        print("KNOWLEDGE BASE STATS")
        print("="*60)
        print(f"Total size: {self.total_size/1024/1024:.1f} MB")
        print(f"Target: 5000 MB (5 GB)")
        print(f"Progress: {self.total_size/1024/1024/5000*100:.1f}%")
        print("="*60)


def main():
    """Build knowledge base."""
    print("="*60)
    print("BUILDING KNOWLEDGE BASE")
    print("="*60)
    
    builder = KnowledgeBaseBuilder()
    
    # Add educational Q&A
    builder.add_educational_qa()
    
    # Add common knowledge
    builder.add_common_knowledge()
    
    # Add Wikipedia summaries for extensive topics
    print("\nFetching summaries for extensive topic lists...")
    
    # Science & Nature
    science_topics = [
        "Physics", "Chemistry", "Biology", "Astronomy", "Geology", "Meteorology",
        "Atom", "Molecule", "Element", "Periodic_table", "Force", "Energy", "Gravity",
        "Electricity", "Magnetism", "Light", "Sound", "Heat", "Thermodynamics",
        "Solar_System", "Sun", "Moon", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune",
        "Star", "Galaxy", "Black_hole", "Universe", "Big_Bang",
        "Cell_(biology)", "DNA", "Genetics", "Evolution", "Photosynthesis", "Respiration",
        "Ecosystem", "Food_web", "Biodiversity", "Climate_change", "Global_warming",
        "Animal", "Plant", "Fungus", "Bacteria", "Virus",
        "Mammal", "Bird", "Reptile", "Amphibian", "Fish", "Insect", "Dinosaur",
        "Human_body", "Brain", "Heart", "Lungs", "Stomach", "Skeleton", "Muscle"
    ]
    
    # History & Geography
    history_topics = [
        "History", "Archaeology", "Civilization", "Ancient_Egypt", "Ancient_Greece", "Roman_Empire",
        "Middle_Ages", "Renaissance", "Industrial_Revolution", "World_War_I", "World_War_II",
        "Geography", "Continent", "Ocean", "Mountain", "River", "Desert", "Forest",
        "Africa", "Antarctica", "Asia", "Europe", "North_America", "South_America", "Australia",
        "United_States", "China", "India", "United_Kingdom", "France", "Germany", "Japan", "Brazil"
    ]
    
    # Technology & Math
    tech_topics = [
        "Technology", "Computer", "Internet", "Artificial_intelligence", "Robot",
        "Smartphone", "Television", "Radio", "Camera", "Car", "Airplane", "Rocket",
        "Mathematics", "Arithmetic", "Algebra", "Geometry", "Calculus", "Statistics",
        "Number", "Fraction", "Equation", "Shape", "Graph"
    ]
    
    # Arts & Culture
    arts_topics = [
        "Art", "Painting", "Sculpture", "Music", "Dance", "Literature", "Poetry",
        "Theater", "Film", "Architecture", "Photography",
        "Language", "Writing", "Alphabet", "Grammar"
    ]
    
    # Combine all topics
    all_topics = science_topics + history_topics + tech_topics + arts_topics
    
    # Fetch summaries
    builder.add_wikipedia_summaries(all_topics)
    
    # Show stats
    builder.get_stats()
    
    print("\n✓ Knowledge base updated!")
    print(f"Total topics processed: {len(all_topics)}")
    print("\nNext steps:")
    print("1. Run this script periodically to add more topics")
    print("2. Add local text files to ./knowledge_base/ directory")
    print("3. Load into RAG: python rag_system.py")


if __name__ == "__main__":
    main()
