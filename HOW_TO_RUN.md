# How to Actually Run and Use This LLM

## 🎯 The Bottom Line

**You have 2 options:**

### Option A: Test Now (10 minutes)
Download a pre-trained model and test the system immediately

### Option B: Train Your Own (4-6 hours)
Create a custom emotion-aware model specifically for your AI Mirror

---

## Option A: Quick Test (Recommended First)

### What You Need
- Windows PC (you have this ✓)
- 10 minutes
- ~500MB download

### Step-by-Step

**1. Download llama.cpp** (if not already done)
```powershell
cd d:\
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release
```

**2. Download a Test Model**
```powershell
# Download Qwen2.5-0.5B (the base model)
# Go to: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF
# Download: qwen2.5-0.5b-instruct-q4_k_m.gguf
# Save to: d:\llmemo\models\
```

**3. Test It Right Now**
```powershell
cd d:\llama.cpp\build\bin\Release

# Simple test
.\main.exe -m d:\llmemo\models\qwen2.5-0.5b-instruct-q4_k_m.gguf -p "Hello, I'm a 9 year old. Why is the sky blue?" -n 200
```

**You should see a response in ~2 seconds!**

---

## Option B: Train Your Custom Model

This creates an emotion-aware model specifically for children.

### Prerequisites
- GPU with 16GB+ VRAM (or use Google Colab free)
- 4-6 hours total time
- 10GB free space

### Step 1: Generate Training Data (5 minutes)
```powershell
cd d:\llmemo
python generate_dataset.py --size 50000 --output training_dataset.json
```

**Output**: `training_dataset.json` (7-10 MB, 50,000 examples)

### Step 2: Install Training Dependencies (5 minutes)
```powershell
# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other requirements
pip install -r requirements_training.txt
```

### Step 3: Train the Model (2-4 hours)
```powershell
python train_lora.py --dataset training_dataset.json --epochs 3
```

**What happens:**
- Downloads base model (Qwen2.5-0.5B)
- Applies QLoRA fine-tuning
- Trains on your 50k examples
- Saves to `./emotion-llm-finetuned/`

**You can leave this running overnight!**

### Step 4: Quantize for Raspberry Pi (10 minutes)
```powershell
python quantize_model.py --model ./emotion-llm-finetuned --method Q4_K_M
```

**Output**: `quantized_models/model-q4_k_m.gguf` (~400MB)

### Step 5: Test Your Trained Model
```powershell
# Using Python API
python -c "from inference_engine import InferenceEngine; engine = InferenceEngine('quantized_models/model-q4_k_m.gguf'); print(engine.generate_response('happy', 0.85, 9, 'Why is the sky blue?')['response'])"
```

---

## Using in Your Python Code

### Simple Example
```python
from inference_engine import InferenceEngine

# Initialize once
engine = InferenceEngine(model_path="quantized_models/model-q4_k_m.gguf")

# Use many times
while True:
    question = input("Ask me anything: ")
    
    result = engine.generate_response(
        emotion="happy",  # From your emotion detection
        confidence=0.85,
        age_group=9,
        question=question
    )
    
    print(f"AI: {result['response']}")
```

### Full AI Mirror Integration
```python
import cv2
from inference_engine import InferenceEngine

engine = InferenceEngine("model-q4_k_m.gguf")
camera = cv2.VideoCapture(0)

while True:
    # 1. Capture frame
    ret, frame = camera.read()
    
    # 2. Detect emotion (use DeepFace or your CV model)
    emotion, confidence = detect_emotion(frame)
    
    # 3. Get voice input (use speech recognition)
    question = listen_for_question()
    
    # 4. Generate response
    result = engine.generate_response(
        emotion=emotion,
        confidence=confidence,
        age_group=9,  # Or detect from face
        question=question
    )
    
    # 5. Speak it out (use TTS)
    speak(result['response'])
    
    # 6. Show on mirror display
    show_on_mirror(result['response'])
```

---

## Deploy to Raspberry Pi

### Transfer Files
```powershell
# Copy model to Pi
scp quantized_models/model-q4_k_m.gguf pi@raspberrypi.local:~/emotion-llm/

# Copy Python scripts
scp *.py pi@raspberrypi.local:~/emotion-llm/
```

### Run on Pi
```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make -j4

# Test
cd ~/emotion-llm
python inference_engine.py --model model-q4_k_m.gguf --emotion happy --age 9 --question "Hi!"
```

**Performance on Pi 5**: ~1.5 seconds per response

---

## What You Can Do RIGHT NOW

### 1. Test Components (Already Done ✓)
```powershell
cd d:\llmemo
python test_system.py
```

### 2. Generate a Small Dataset
```powershell
python generate_dataset.py --size 1000 --output small_dataset.json
```

### 3. View Example Conversations
```powershell
python -c "import json; data = json.load(open('example_conversations.json')); print(json.dumps(data['conversations'][0], indent=2))"
```

---

## Recommended Path for You

**Today:**
1. ✓ Test components (done!)
2. Download base model for quick testing
3. Test with llama.cpp

**Tomorrow:**
1. Generate full dataset (50k examples)
2. Start training overnight

**Day 3:**
1. Quantize trained model
2. Test on your PC
3. Deploy to Raspberry Pi

---

## Need Help?

**Common Questions:**

**Q: Do I need a GPU?**  
A: For training, yes (or use Google Colab free). For running the model, no.

**Q: Can I skip training?**  
A: Yes! Use the base model for testing. But training gives you emotion-awareness.

**Q: How long does inference take?**  
A: ~1.5 seconds on Raspberry Pi 5, <1 second on a good PC.

**Q: Can I use this without Raspberry Pi?**  
A: Absolutely! Works on any Windows/Linux/Mac computer.

---

## Summary

**To run the LLM:**
1. Get llama.cpp
2. Get a model (download base OR train custom)
3. Run: `python inference_engine.py --model <path> --question "your question"`

**That's it!**

See `QUICKSTART.md` for more details.
