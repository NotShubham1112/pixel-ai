"""
Generate synthetic training dataset for emotion-aware child-friendly LLM.
Creates 50k-200k examples with balanced emotion and age distribution.
"""

import json
import random
from typing import List, Dict
from emotion_prompt_template import EmotionPromptTemplate


class DatasetGenerator:
    """Generates synthetic training data for emotion-aware conversations."""
    
    EMOTIONS = ["happy", "sad", "angry", "surprised", "neutral", "confused", "excited", "worried"]
    
    AGE_RANGES = {
        "5-7": (5, 7),
        "8-10": (8, 10),
        "11-13": (11, 13),
        "14-16": (14, 16)
    }
    
    # Question templates by emotion and age
    QUESTION_TEMPLATES = {
        "happy": [
            "I got an A on my {subject} test!",
            "I made a new friend today!",
            "Can we play a game?",
            "I love {activity}!",
            "Today was the best day ever!",
            "I'm so excited for {event}!",
        ],
        "sad": [
            "I miss my {person}",
            "Nobody wants to play with me",
            "I'm not good at {activity}",
            "My {pet} is sick",
            "I lost my favorite {item}",
            "Everyone is better than me at {subject}",
        ],
        "angry": [
            "My {sibling} broke my {item}!",
            "That's not fair!",
            "I hate {subject}!",
            "Everyone is so annoying",
            "Why do I have to {chore}?",
            "Nobody listens to me",
        ],
        "surprised": [
            "I saw a {animal} today!",
            "Wait, you're not a real person?",
            "How did you know that?",
            "I can't believe {event}!",
            "That's so cool!",
            "Really? Are you sure?",
        ],
        "neutral": [
            "What's your favorite {thing}?",
            "How does {concept} work?",
            "Can you help me with {subject}?",
            "Tell me about {topic}",
            "What is {concept}?",
            "Why do we have {thing}?",
        ],
        "confused": [
            "I don't understand {subject}",
            "Why do we have to {activity}?",
            "How does {concept} work?",
            "What does {word} mean?",
            "I'm confused about {topic}",
            "Can you explain {concept}?",
        ],
        "excited": [
            "I'm going to {place} tomorrow!",
            "Look at my {creation}!",
            "Guess what happened!",
            "I can't wait for {event}!",
            "This is amazing!",
            "I just learned about {topic}!",
        ],
        "worried": [
            "What if I fail my test?",
            "I'm scared of {thing}",
            "What if {bad_event} happens?",
            "I'm nervous about {event}",
            "Is {concern} going to happen?",
            "I can't stop thinking about {worry}",
        ]
    }
    
    # Replacement values for templates
    REPLACEMENTS = {
        "subject": ["math", "science", "English", "history", "art", "music"],
        "activity": ["reading", "drawing", "sports", "dancing", "singing", "coding"],
        "event": ["my birthday", "the school trip", "the weekend", "summer vacation"],
        "person": ["grandma", "best friend", "teacher", "cousin"],
        "pet": ["dog", "cat", "hamster", "fish"],
        "item": ["toy", "book", "game", "drawing", "project"],
        "sibling": ["brother", "sister"],
        "chore": ["clean my room", "do homework", "go to bed early"],
        "animal": ["rainbow", "shooting star", "butterfly", "bird"],
        "thing": ["color", "animal", "food", "book", "game"],
        "concept": ["gravity", "photosynthesis", "electricity", "the water cycle", "fractions"],
        "topic": ["space", "dinosaurs", "the ocean", "computers", "animals"],
        "word": ["algorithm", "ecosystem", "democracy", "molecule"],
        "creation": ["drawing", "LEGO creation", "story", "painting"],
        "place": ["Disneyland", "the beach", "grandma's house", "the zoo"],
        "bad_event": ["something bad", "I mess up", "I get in trouble"],
        "concern": ["my dog", "my grade", "my friend"],
        "worry": ["tomorrow", "the test", "what people think"]
    }
    
    def __init__(self, target_size: int = 50000):
        """
        Initialize dataset generator.
        
        Args:
            target_size: Target number of training examples (50k-200k)
        """
        self.target_size = target_size
        self.examples = []
        
    def fill_template(self, template: str) -> str:
        """Fill a template with random replacement values."""
        result = template
        for key, values in self.REPLACEMENTS.items():
            if f"{{{key}}}" in result:
                result = result.replace(f"{{{key}}}", random.choice(values))
        return result
    
    def generate_question(self, emotion: str) -> str:
        """Generate a random question for the given emotion."""
        template = random.choice(self.QUESTION_TEMPLATES[emotion])
        return self.fill_template(template)
    
    def generate_response(self, emotion: str, age: int, question: str, memory: Dict = None) -> str:
        """
        Generate an appropriate response (placeholder - in production, use GPT-4 or Claude).
        For this demo, we'll use template-based responses.
        """
        # This is a simplified version - in production, use a strong LLM to generate responses
        responses = {
            "happy": [
                "That's wonderful! I'm so happy for you! 🌟",
                "How exciting! Tell me more!",
                "That sounds amazing! What was your favorite part?",
            ],
            "sad": [
                "I can hear that you're feeling sad. It's okay to feel this way.",
                "That sounds really hard. Do you want to talk about it?",
                "I'm sorry you're going through this. Remember, it's okay to feel sad sometimes.",
            ],
            "angry": [
                "I can tell you're really frustrated. Let's take a deep breath together.",
                "That sounds upsetting. Have you talked to someone about how you feel?",
                "It's okay to feel angry, but let's think about what might help.",
            ],
            "surprised": [
                "Wow, that's so cool! Tell me more!",
                "That's amazing! What did you think about it?",
                "How exciting! I'd love to hear more details!",
            ],
            "neutral": [
                "That's a great question! Let me think about that.",
                "I'd be happy to help you with that!",
                "Interesting! Here's what I know about that...",
            ],
            "confused": [
                "Great question! Let me explain that in a simple way.",
                "I can see why that might be confusing. Let's break it down together!",
                "Don't worry, lots of people find that tricky at first!",
            ],
            "excited": [
                "OMG that's SO exciting!! 🎉",
                "I can feel your excitement! That's awesome!",
                "How cool! You must be so thrilled!",
            ],
            "worried": [
                "I hear that you're worried. Let's think about this together.",
                "It's normal to feel nervous sometimes. Take a deep breath!",
                "I understand your concern. Have you talked to a parent or teacher about this?",
            ]
        }
        
        return random.choice(responses[emotion])
    
    def generate_example(self) -> Dict:
        """Generate a single training example."""
        emotion = random.choice(self.EMOTIONS)
        age_range = random.choice(list(self.AGE_RANGES.keys()))
        age = random.randint(*self.AGE_RANGES[age_range])
        confidence = round(random.uniform(0.6, 0.95), 2)
        
        # 30% chance of including memory
        memory = {}
        includes_memory = random.random() < 0.3
        if includes_memory:
            memory = {
                "name": random.choice(["Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey"])
            }
            if random.random() < 0.5:
                memory["favorite_color"] = random.choice(["blue", "red", "purple", "green", "pink"])
            if random.random() < 0.3:
                memory["favorite_subject"] = random.choice(["Math", "Science", "Art", "Reading"])
        
        question = self.generate_question(emotion)
        response = self.generate_response(emotion, age, question, memory)
        
        # Determine safety level
        safety_keywords = ["die", "sick", "hurt", "scared", "hate", "nobody likes"]
        safety_level = "requires_disclaimer" if any(kw in question.lower() for kw in safety_keywords) else "safe"
        
        return {
            "instruction": EmotionPromptTemplate.SYSTEM_PROMPT,
            "input": {
                "emotion": emotion,
                "confidence": confidence,
                "age_group": age,
                "question": question,
                "memory": memory
            },
            "output": response,
            "metadata": {
                "emotion_category": emotion,
                "age_group": age_range,
                "safety_level": safety_level,
                "response_type": random.choice(["answer", "reflection", "encouragement", "redirection"]),
                "includes_memory": includes_memory
            }
        }
    
    def generate_dataset(self) -> List[Dict]:
        """Generate the complete dataset."""
        print(f"Generating {self.target_size} training examples...")
        
        # Ensure balanced distribution
        examples_per_emotion = self.target_size // len(self.EMOTIONS)
        
        for emotion in self.EMOTIONS:
            print(f"Generating {examples_per_emotion} examples for emotion: {emotion}")
            for _ in range(examples_per_emotion):
                self.examples.append(self.generate_example())
        
        # Shuffle for randomness
        random.shuffle(self.examples)
        
        print(f"✓ Generated {len(self.examples)} examples")
        return self.examples
    
    def save_dataset(self, output_path: str = "training_dataset.json"):
        """Save the dataset to a JSON file."""
        emotion_dist = {}
        age_dist = {}
        
        for ex in self.examples:
            emotion = ex["metadata"]["emotion_category"]
            age = ex["metadata"]["age_group"]
            emotion_dist[emotion] = emotion_dist.get(emotion, 0) + 1
            age_dist[age] = age_dist.get(age, 0) + 1
        
        dataset = {
            "dataset_info": {
                "version": "1.0.0",
                "total_examples": len(self.examples),
                "emotion_distribution": emotion_dist,
                "age_distribution": age_dist
            },
            "examples": self.examples
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Dataset saved to {output_path}")
        print(f"  - Total examples: {len(self.examples)}")
        print(f"  - Emotion distribution: {emotion_dist}")
        print(f"  - Age distribution: {age_dist}")
    
    def validate_dataset(self) -> bool:
        """Validate dataset for safety and quality."""
        print("Validating dataset...")
        
        forbidden_words = ["kill", "suicide", "drug", "alcohol", "sex", "weapon"]
        issues = []
        
        for i, ex in enumerate(self.examples):
            # Check for forbidden content
            text = ex["input"]["question"].lower() + " " + ex["output"].lower()
            for word in forbidden_words:
                if word in text:
                    issues.append(f"Example {i}: Contains forbidden word '{word}'")
            
            # Check response length
            if len(ex["output"]) > 300:
                issues.append(f"Example {i}: Response too long ({len(ex['output'])} chars)")
            
            # Check age appropriateness
            if ex["input"]["age_group"] < 5 or ex["input"]["age_group"] > 16:
                issues.append(f"Example {i}: Invalid age {ex['input']['age_group']}")
        
        if issues:
            print(f"⚠ Found {len(issues)} validation issues:")
            for issue in issues[:10]:  # Show first 10
                print(f"  - {issue}")
            return False
        
        print("✓ Dataset validation passed!")
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate emotion-aware training dataset")
    parser.add_argument("--size", type=int, default=50000, help="Number of examples to generate")
    parser.add_argument("--output", type=str, default="training_dataset.json", help="Output file path")
    parser.add_argument("--validate", action="store_true", help="Validate dataset only")
    
    args = parser.parse_args()
    
    generator = DatasetGenerator(target_size=args.size)
    
    if args.validate:
        # Load and validate existing dataset
        with open(args.output, 'r', encoding='utf-8') as f:
            data = json.load(f)
            generator.examples = data["examples"]
        generator.validate_dataset()
    else:
        # Generate new dataset
        generator.generate_dataset()
        generator.validate_dataset()
        generator.save_dataset(args.output)
        
        print(f"\n✓ Dataset generation complete!")
        print(f"  Run training with: python train_lora.py --dataset {args.output}")
