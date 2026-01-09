"""
QLoRA fine-tuning script for emotion-aware child-friendly LLM.
Optimized for small datasets and Raspberry Pi deployment.
"""

import os
import json
import torch
from dataclasses import dataclass
from typing import Optional
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import argparse


@dataclass
class ModelConfig:
    """Configuration for model and training."""
    base_model: str = "Qwen/Qwen2.5-0.5B-Instruct"
    dataset_path: str = "training_dataset.json"
    output_dir: str = "./emotion-llm-finetuned"
    
    # LoRA parameters
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: list = None
    
    # Training parameters
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    max_seq_length: int = 512
    warmup_steps: int = 100
    
    # Quantization
    use_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    
    def __post_init__(self):
        if self.lora_target_modules is None:
            # Target attention and MLP layers for Qwen
            self.lora_target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


class EmotionLLMTrainer:
    """Trainer for emotion-aware LLM using QLoRA."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.dataset = None
        
    def load_dataset(self):
        """Load and preprocess the training dataset."""
        print(f"Loading dataset from {self.config.dataset_path}...")
        
        with open(self.config.dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        examples = data["examples"]
        print(f"Loaded {len(examples)} examples")
        
        # Format examples for training
        formatted_data = []
        for ex in examples:
            # Create a conversational format
            emotion = ex["input"]["emotion"]
            age = ex["input"]["age_group"]
            question = ex["input"]["question"]
            response = ex["output"]
            
            # Format: System + User + Assistant
            text = f"""<|im_start|>system
{ex['instruction']}<|im_end|>
<|im_start|>user
[EMOTION: {emotion}] [AGE: {age}]
{question}<|im_end|>
<|im_start|>assistant
{response}<|im_end|>"""
            
            formatted_data.append({"text": text})
        
        self.dataset = Dataset.from_list(formatted_data)
        print(f"✓ Dataset prepared: {len(self.dataset)} examples")
        
        return self.dataset
    
    def load_model(self):
        """Load base model with 4-bit quantization."""
        print(f"Loading base model: {self.config.base_model}...")
        
        # Quantization config for QLoRA
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=self.config.use_4bit,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model,
            trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Prepare for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)
        
        print("✓ Model loaded with 4-bit quantization")
        
        return self.model
    
    def setup_lora(self):
        """Configure and apply LoRA."""
        print("Setting up LoRA...")
        
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
        print("✓ LoRA configured")
        
        return self.model
    
    def tokenize_dataset(self):
        """Tokenize the dataset."""
        print("Tokenizing dataset...")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=self.config.max_seq_length,
                padding="max_length"
            )
        
        tokenized_dataset = self.dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=self.dataset.column_names
        )
        
        print("✓ Dataset tokenized")
        return tokenized_dataset
    
    def train(self):
        """Execute the training loop."""
        print("Starting training...")
        
        # Load everything
        self.load_dataset()
        self.load_model()
        self.setup_lora()
        tokenized_dataset = self.tokenize_dataset()
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            fp16=True,
            save_strategy="epoch",
            logging_steps=10,
            warmup_steps=self.config.warmup_steps,
            lr_scheduler_type="cosine",
            optim="paged_adamw_8bit",
            report_to="none",
            save_total_limit=2,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        # Train!
        print("🚀 Training started...")
        trainer.train()
        
        # Save final model
        print("Saving final model...")
        trainer.save_model(self.config.output_dir)
        self.tokenizer.save_pretrained(self.config.output_dir)
        
        print(f"✓ Training complete! Model saved to {self.config.output_dir}")
        print(f"\nNext steps:")
        print(f"1. Quantize for Raspberry Pi: python quantize_model.py --model {self.config.output_dir}")
        print(f"2. Test inference: python test_inference.py --model {self.config.output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Train emotion-aware LLM with QLoRA")
    parser.add_argument("--dataset", type=str, default="training_dataset.json", help="Path to training dataset")
    parser.add_argument("--base-model", type=str, default="Qwen/Qwen2.5-0.5B-Instruct", help="Base model to fine-tune")
    parser.add_argument("--output", type=str, default="./emotion-llm-finetuned", help="Output directory")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size per device")
    parser.add_argument("--learning-rate", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--dry-run", action="store_true", help="Test setup without training")
    
    args = parser.parse_args()
    
    config = ModelConfig(
        base_model=args.base_model,
        dataset_path=args.dataset,
        output_dir=args.output,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate
    )
    
    trainer = EmotionLLMTrainer(config)
    
    if args.dry_run:
        print("DRY RUN MODE - Testing setup...")
        trainer.load_dataset()
        print("✓ Dataset loaded successfully")
        trainer.load_model()
        print("✓ Model loaded successfully")
        trainer.setup_lora()
        print("✓ LoRA configured successfully")
        print("\n✓ Dry run complete! Ready for training.")
    else:
        trainer.train()


if __name__ == "__main__":
    main()
