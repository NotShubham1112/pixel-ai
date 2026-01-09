"""
Updated simple chat that auto-detects and uses the smallest available model.
Prioritizes 2-bit for speed, falls back to 4-bit.
"""

import os
from pathlib import Path

print("="*60)
print("SMART CHAT - Auto Model Selection")
print("="*60)

# Check for available models (prefer smaller/faster)
models_dir = Path("models")
available_models = []

if models_dir.exists():
    # Priority order: 2-bit > 4-bit > 5-bit > 8-bit
    model_priority = [
        "Qwen2.5-0.5B-Instruct-Q2_K.gguf",      # 2-bit (fastest)
        "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",    # 4-bit (balanced)
        "Qwen2.5-0.5B-Instruct-Q5_K_M.gguf",    # 5-bit (better quality)
        "Qwen2.5-0.5B-Instruct-Q8_0.gguf",      # 8-bit (best quality)
    ]
    
    for model_name in model_priority:
        model_path = models_dir / model_name
        if model_path.exists():
            available_models.append((model_name, model_path))
            print(f"✓ Found: {model_name}")

if not available_models:
    print("\n❌ No models found!")
    print("\nDownload a model first:")
    print("  python download_2bit.py    # Fastest (2-bit, ~150MB)")
    print("  python download_model_fixed.py  # Balanced (4-bit, ~400MB)")
    exit(1)

# Use the first (highest priority) model
selected_model_name, selected_model_path = available_models[0]

print(f"\n🚀 Using: {selected_model_name}")

# Get quantization info
if "Q2" in selected_model_name:
    quant_info = "2-bit (Fastest, ~150MB, Good quality)"
elif "Q4" in selected_model_name:
    quant_info = "4-bit (Balanced, ~400MB, Great quality)"
elif "Q5" in selected_model_name:
    quant_info = "5-bit (Slower, ~500MB, Excellent quality)"
else:
    quant_info = "8-bit (Slowest, ~800MB, Best quality)"

print(f"   Quantization: {quant_info}")
print("="*60)

# Install llama-cpp-python if needed
print("\nChecking dependencies...")
try:
    from llama_cpp import Llama
    print("✓ llama-cpp-python installed")
except ImportError:
    print("Installing llama-cpp-python...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python"])
    from llama_cpp import Llama
    print("✓ Installed llama-cpp-python")

# Load model
print(f"\nLoading model: {selected_model_name}...")
llm = Llama(
    model_path=str(selected_model_path),
    n_ctx=2048,
    n_threads=4,
    verbose=False
)

print("✓ Model loaded!")
print("\n" + "="*60)
print("CHAT MODE")
print("="*60)
print("Commands:")
print("  /stats - Show model info")
print("  /quit  - Exit")
print("="*60 + "\n")

# Chat loop with stats
message_count = 0

while True:
    try:
        question = input("You: ").strip()
        
        if not question:
            continue
        
        # Commands
        if question.lower() in ['/quit', '/exit']:
            print("\nGoodbye! 👋")
            break
        
        if question.lower() == '/stats':
            print(f"\n📊 Model Stats:")
            print(f"  Model: {selected_model_name}")
            print(f"  Quantization: {quant_info}")
            print(f"  Messages: {message_count}")
            print(f"  Context: 2048 tokens")
            print(f"  Threads: 4\n")
            continue
        
        # Generate response
        prompt = f"""You are Pixel, a friendly and helpful AI assistant.

User: {question}

Pixel:"""
        
        response = llm(
            prompt,
            max_tokens=200,
            temperature=0.7,
            stop=["User:", "\nUser", "\n\n"],
            echo=False
        )
        
        answer = response['choices'][0]['text'].strip()
        print(f"\nAI: {answer}\n")
        message_count += 1
        
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        break
    except Exception as e:
        print(f"\n⚠ Error: {e}\n")
        continue
