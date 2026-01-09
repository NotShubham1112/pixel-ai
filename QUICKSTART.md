# Quick Start Guide - Running the Emotion LLM

## 🚀 Two Ways to Run This

### Option 1: Quick Test with Base Model (No Training Required)
**Time**: 10 minutes  
**Use**: Testing the system before training

### Option 2: Full Training Pipeline (Recommended for Production)
**Time**: 4-6 hours  
**Use**: Production-ready custom model

---

## Option 1: Quick Test (Base Model)

Since training takes time, let's test with the base model first:

### Step 1: Install llama.cpp
```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build (Windows)
cmake -B build
cmake --build build --config Release

# Or on Linux/Mac
make -j4
```

### Step 2: Download a Pre-quantized Model
```bash
# Download Qwen2.5-0.5B (the base model we'll fine-tune)
# Visit: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF

# Or use this command (requires huggingface-cli)
huggingface-cli download Qwen/Qwen2.5-0.5B-Instruct-GGUF qwen2.5-0.5b-instruct-q4_k_m.gguf --local-dir ./models
```

### Step 3: Test Inference
```bash
# Basic test
cd llama.cpp
./build/bin/Release/main.exe -m ../models/qwen2.5-0.5b-instruct-q4_k_m.gguf -p "You are a friendly AI for children. A happy 9-year-old asks: Why is the sky blue?" -n 200

# Or use our Python wrapper
cd ../llmemo
python test_base_model.py
```

---

## Option 2: Full Training Pipeline

### Prerequisites
- **GPU**: 16GB+ VRAM (RTX 3090, 4090, or Google Colab)
- **Time**: 4-6 hours total
- **Storage**: ~10GB free space

### Step 1: Install Training Dependencies
```bash
cd d:\llmemo

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
pip install -r requirements_training.txt
```

### Step 2: Generate Training Dataset
```bash
# Generate 50,000 training examples (~5 minutes)
python generate_dataset.py --size 50000 --output training_dataset.json

# Validate the dataset
python generate_dataset.py --validate --output training_dataset.json
```

**Output**: `training_dataset.json` (~7-10 MB)

### Step 3: Train the Model
```bash
# Start training (2-4 hours on RTX 3090)
python train_lora.py --dataset training_dataset.json --epochs 3

# Monitor progress - you'll see:
# - Loading base model (Qwen2.5-0.5B)
# - Applying QLoRA (4-bit quantization)
# - Training progress with loss metrics
# - Saving checkpoints
```

**Output**: `./emotion-llm-finetuned/` directory with trained model

### Step 4: Quantize for Raspberry Pi
```bash
# Convert to GGUF format (5-10 minutes)
python quantize_model.py --model ./emotion-llm-finetuned --method Q4_K_M

# This creates: quantized_models/model-q4_k_m.gguf (~400MB)
```

### Step 5: Test Your Trained Model
```bash
# Test inference with your custom model
python inference_engine.py \
  --model quantized_models/model-q4_k_m.gguf \
  --emotion happy \
  --age 9 \
  --question "Why is the sky blue?"
```

---

## Using the Model in Your Code

### Simple Python API

```python
from inference_engine import InferenceEngine

# Initialize (one time)
engine = InferenceEngine(
    model_path="quantized_models/model-q4_k_m.gguf",
    n_threads=4  # Adjust for your CPU
)

# Generate responses
result = engine.generate_response(
    emotion="happy",
    confidence=0.85,
    age_group=9,
    question="Why is the sky blue?",
    use_memory=True
)

print(result["response"])
# Output: "Great question! The sky looks blue because..."
```

### With Emotion Detection (Full AI Mirror)

```python
import cv2
from inference_engine import InferenceEngine
# Add your emotion detection library (DeepFace, etc.)

engine = InferenceEngine(model_path="model-q4_k_m.gguf")

# Main loop
cap = cv2.VideoCapture(0)  # Camera

while True:
    ret, frame = cap.read()
    
    # 1. Detect emotion from face
    emotion, confidence = detect_emotion(frame)  # Your function
    
    # 2. Get voice input
    question = get_voice_input()  # Your STT function
    
    # 3. Generate response
    result = engine.generate_response(
        emotion=emotion,
        confidence=confidence,
        age_group=9,  # Or detect age
        question=question
    )
    
    # 4. Speak response
    speak(result["response"])  # Your TTS function
    
    # 5. Display on mirror
    display_on_mirror(result["response"])
```

---

## Raspberry Pi Deployment

### Transfer Model to Pi
```bash
# From your PC, copy the quantized model
scp quantized_models/model-q4_k_m.gguf pi@raspberrypi.local:~/emotion-llm/

# Copy Python scripts
scp *.py pi@raspberrypi.local:~/emotion-llm/
```

### Run on Pi
```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Install llama.cpp on Pi
cd ~
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j4

# Test inference
cd ~/emotion-llm
python inference_engine.py \
  --model model-q4_k_m.gguf \
  --emotion happy \
  --age 9 \
  --question "Tell me about space"
```

**Expected Performance on Pi 5**:
- Inference time: ~1.5 seconds
- Memory usage: ~2.2 GB
- CPU usage: ~65%

---

## Testing Without Training (Quick Demo)

If you want to test RIGHT NOW without training:

### Create a Simple Test Script

```python
# test_system.py
from safety_filter import SafetyFilter
from memory_manager import MemoryManager
from emotion_prompt_template import EmotionPromptTemplate

# Test safety filter
filter = SafetyFilter()
result = filter.filter_input("Why is the sky blue?", age=9)
print(f"Safety check: {result.is_safe}")

# Test memory
memory = MemoryManager()
memory.give_consent(True)
memory.set_user_profile(name="Test User", age=9)
memory.add_interaction("happy", "Test question", "Test response")
print(f"Memory context: {memory.get_context()}")

# Test prompt generation
prompt = EmotionPromptTemplate.create_prompt(
    emotion="happy",
    confidence=0.85,
    age_group=9,
    question="Why is the sky blue?",
    memory=memory.get_context()
)
print(f"\nGenerated prompt:\n{prompt[:200]}...")
```

Run it:
```bash
python test_system.py
```

---

## Troubleshooting

### "No GPU available"
- Use Google Colab for training (free GPU)
- Or train on CPU (much slower, 12+ hours)

### "llama.cpp not found"
- Make sure you built llama.cpp first
- Update path in `inference_engine.py`

### "Model too slow on Pi"
- Use Q4_K_S quantization (smaller, faster)
- Reduce max_tokens to 150
- Ensure active cooling

---

## Summary

**To Actually Run This**:

1. **Quick Test** (10 min): Download base model + test with llama.cpp
2. **Full Training** (4-6 hours): Generate dataset → Train → Quantize → Deploy
3. **Production Use**: Integrate with camera/mic/TTS for AI Mirror

**Recommended Path**:
1. Test components now (already done ✓)
2. Generate full dataset tomorrow
3. Train overnight on GPU
4. Deploy to Pi next day

Need help with any specific step?
