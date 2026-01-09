"""
Merge multiple datasets into one comprehensive training dataset.
Combines: chat data, generated data, quality Q&A, and sample data.
"""

import json
from pathlib import Path
from datetime import datetime


def load_dataset(path: str) -> list:
    """Load examples from a dataset file."""
    if not Path(path).exists():
        print(f"  ⚠ {path} not found, skipping")
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    examples = data.get("examples", [])
    print(f"  ✓ {path}: {len(examples)} examples")
    return examples


def merge_all_datasets(output_path: str = "final_training_dataset.json"):
    """Merge all available datasets."""
    
    print("="*60)
    print("MERGING ALL DATASETS")
    print("="*60)
    
    all_examples = []
    
    # List of dataset files to merge
    dataset_files = [
        "chat_training_data.json",      # From interactive chat
        "test_dataset.json",             # From test generation
        "sample_dataset.json",           # Curated samples
        "enhanced_training_data.json",   # Quality Q&A
        "generated_data.json",           # If you generated more
    ]
    
    print("\nLoading datasets...")
    for dataset_file in dataset_files:
        examples = load_dataset(dataset_file)
        all_examples.extend(examples)
    
    # Create final dataset
    final_dataset = {
        "dataset_info": {
            "version": "1.0.0",
            "total_examples": len(all_examples),
            "created_at": datetime.now().isoformat(),
            "source": "merged_datasets",
            "merged_from": dataset_files
        },
        "examples": all_examples
    }
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print("✓ MERGE COMPLETE!")
    print("="*60)
    print(f"Total examples: {len(all_examples)}")
    print(f"Output file: {output_path}")
    print(f"File size: {Path(output_path).stat().st_size / 1024:.1f} KB")
    
    # Show distribution
    emotions = {}
    for ex in all_examples:
        emotion = ex.get("input", {}).get("emotion", "unknown")
        emotions[emotion] = emotions.get(emotion, 0) + 1
    
    print(f"\nEmotion distribution:")
    for emotion, count in sorted(emotions.items(), key=lambda x: -x[1]):
        print(f"  {emotion}: {count}")
    
    print(f"\n{'='*60}")
    print("Ready to train!")
    print(f"Run: python train_lora.py --dataset {output_path} --epochs 3")
    print("="*60)


if __name__ == "__main__":
    merge_all_datasets()
