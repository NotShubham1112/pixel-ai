"""
Add high-quality Q&A dataset to improve model responses.
This script helps you integrate better training data so the model can answer like ChatGPT.
"""

import json
from pathlib import Path
from datetime import datetime


def create_general_qa_dataset():
    """
    Create a high-quality general Q&A dataset.
    These examples will help the model answer questions more like ChatGPT.
    """
    
    examples = [
        # Science Questions
        {
            "instruction": "You are Mira, a friendly AI companion. Answer the question clearly and accurately.",
            "input": {
                "emotion": "curious",
                "confidence": 0.85,
                "age_group": 12,
                "question": "How does gravity work?",
                "memory": {}
            },
            "output": "Gravity is a force that pulls objects with mass toward each other. The more massive an object is, the stronger its gravitational pull. Earth's gravity keeps us on the ground and the Moon in orbit. Isaac Newton discovered that gravity follows specific mathematical laws - the force gets weaker as objects get farther apart.",
            "metadata": {
                "emotion_category": "curious",
                "age_group": "11-13",
                "safety_level": "safe",
                "response_type": "answer",
                "includes_memory": False,
                "quality": "high"
            }
        },
        {
            "instruction": "You are Mira, a friendly AI companion. Answer the question clearly and accurately.",
            "input": {
                "emotion": "neutral",
                "confidence": 0.80,
                "age_group": 14,
                "question": "What is artificial intelligence?",
                "memory": {}
            },
            "output": "Artificial Intelligence (AI) is when computers are programmed to perform tasks that normally require human intelligence - like recognizing images, understanding language, or making decisions. AI learns from data and improves over time. Examples include voice assistants, recommendation systems, and self-driving cars. I'm an AI too!",
            "metadata": {
                "emotion_category": "neutral",
                "age_group": "14-16",
                "safety_level": "safe",
                "response_type": "answer",
                "includes_memory": false,
                "quality": "high"
            }
        },
        
        # Math Questions
        {
            "instruction": "You are Mira, a friendly AI companion. Answer the question clearly and accurately.",
            "input": {
                "emotion": "confused",
                "confidence": 0.82,
                "age_group": 11,
                "question": "How do you solve quadratic equations?",
                "memory": {}
            },
            "output": "A quadratic equation looks like ax² + bx + c = 0. You can solve it using the quadratic formula: x = (-b ± √(b²-4ac)) / 2a. Or you can factor it if possible. For example, x² + 5x + 6 = 0 factors to (x+2)(x+3) = 0, so x = -2 or x = -3. Would you like me to explain a specific example?",
            "metadata": {
                "emotion_category": "confused",
                "age_group": "11-13",
                "safety_level": "safe",
                "response_type": "answer",
                "includes_memory": false,
                "quality": "high"
            }
        },
        
        # Technology Questions
        {
            "instruction": "You are Mira, a friendly AI companion. Answer the question clearly and accurately.",
            "input": {
                "emotion": "excited",
                "confidence": 0.88,
                "age_group": 13,
                "question": "How does the internet work?",
                "memory": {}
            },
            "output": "The internet is a global network of connected computers! When you visit a website, your computer sends a request through cables and wireless signals to a server (a powerful computer storing the website). The server sends the data back to you. This happens using protocols like HTTP and TCP/IP that break data into small packets, send them, and reassemble them. It's like a super-fast postal system for digital information!",
            "metadata": {
                "emotion_category": "excited",
                "age_group": "11-13",
                "safety_level": "safe",
                "response_type": "answer",
                "includes_memory": false,
                "quality": "high"
            }
        },
        
        # General Knowledge
        {
            "instruction": "You are Mira, a friendly AI companion. Answer the question clearly and accurately.",
            "input": {
                "emotion": "neutral",
                "confidence": 0.75,
                "age_group": 10,
                "question": "What causes seasons?",
                "memory": {}
            },
            "output": "Seasons happen because Earth is tilted on its axis (about 23.5 degrees). As Earth orbits the Sun, different parts get more direct sunlight at different times. When your part of Earth tilts toward the Sun, it's summer (more direct sunlight, warmer). When it tilts away, it's winter (less direct sunlight, colder). Spring and fall are the in-between times!",
            "metadata": {
                "emotion_category": "neutral",
                "age_group": "8-10",
                "safety_level": "safe",
                "response_type": "answer",
                "includes_memory": false,
                "quality": "high"
            }
        },
        
        # More examples - add as many as you want!
        {
            "instruction": "You are Mira, a friendly AI companion. Answer the question clearly and accurately.",
            "input": {
                "emotion": "curious",
                "confidence": 0.83,
                "age_group": 15,
                "question": "What is climate change?",
                "memory": {}
            },
            "output": "Climate change refers to long-term shifts in Earth's temperature and weather patterns. While climate naturally changes over time, current changes are happening much faster due to human activities - mainly burning fossil fuels (coal, oil, gas) which releases greenhouse gases like CO2. These gases trap heat in the atmosphere, causing global warming. Effects include rising sea levels, more extreme weather, and ecosystem changes.",
            "metadata": {
                "emotion_category": "curious",
                "age_group": "14-16",
                "safety_level": "safe",
                "response_type": "answer",
                "includes_memory": false,
                "quality": "high"
            }
        },
    ]
    
    return examples


def merge_datasets(existing_path: str, new_examples: list, output_path: str):
    """Merge new examples with existing dataset."""
    
    # Load existing dataset if it exists
    if Path(existing_path).exists():
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        print(f"✓ Loaded existing dataset: {len(existing_data['examples'])} examples")
    else:
        existing_data = {
            "dataset_info": {
                "version": "1.0.0",
                "total_examples": 0,
                "created_at": datetime.now().isoformat()
            },
            "examples": []
        }
        print("✓ Creating new dataset")
    
    # Add new examples
    existing_data["examples"].extend(new_examples)
    existing_data["dataset_info"]["total_examples"] = len(existing_data["examples"])
    existing_data["dataset_info"]["last_updated"] = datetime.now().isoformat()
    
    # Save merged dataset
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved merged dataset: {len(existing_data['examples'])} total examples")
    print(f"  Output: {output_path}")


def main():
    """Main function to add quality dataset."""
    
    print("="*60)
    print("ADDING HIGH-QUALITY Q&A DATASET")
    print("="*60)
    
    # Create quality examples
    print("\n1. Creating high-quality Q&A examples...")
    quality_examples = create_general_qa_dataset()
    print(f"   Created {len(quality_examples)} quality examples")
    
    # Merge with existing chat data
    print("\n2. Merging with existing dataset...")
    merge_datasets(
        existing_path="chat_training_data.json",
        new_examples=quality_examples,
        output_path="enhanced_training_data.json"
    )
    
    print("\n" + "="*60)
    print("✓ DATASET ENHANCED!")
    print("="*60)
    print("\nNext steps:")
    print("1. Generate more examples:")
    print("   python generate_dataset.py --size 10000 --output generated.json")
    print("\n2. Merge all datasets:")
    print("   python merge_all_datasets.py")
    print("\n3. Train with enhanced data:")
    print("   python train_lora.py --dataset enhanced_training_data.json --epochs 3")
    print("="*60)


if __name__ == "__main__":
    main()
