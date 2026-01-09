# Interactive Chat Interface - Quick Guide

## 🎯 What This Does

A terminal-based chat interface that:
- ✅ Lets you chat with the LLM in real-time
- ✅ Automatically saves conversations to training dataset
- ✅ Learns from your conversations
- ✅ Works on Raspberry Pi
- ✅ Includes safety filtering and memory

---

## 🚀 Quick Start

### Option 1: Chat Without Model (Dataset Building)
```bash
cd d:\llmemo
python chat.py
```

This mode:
- No model needed
- Collects training data from your conversations
- Saves to `chat_training_data.json`
- Use this to build a custom dataset!

### Option 2: Chat With Model
```bash
# If you have a trained model
python chat.py --model quantized_models/model-q4_k_m.gguf

# Or with a downloaded base model
python chat.py --model models/qwen2.5-0.5b-instruct-q4_k_m.gguf
```

---

## 💬 How to Use

### 1. Start Chat
```bash
python chat.py
```

### 2. Setup Profile (Optional)
```
What's your name? Alex
How old are you? (5-16): 9
Can I remember your name and preferences? yes
What's your favorite color? blue
What's your favorite subject? Science
```

### 3. Chat!
```
[neutral] You: Why is the sky blue?
AI: Great question! The sky looks blue because...

[neutral] You: Tell me about space
AI: Space is amazing! It's the vast area beyond Earth...
```

### 4. Use Commands
```
/emotion  - Change emotion (happy, sad, angry, etc.)
/stats    - View statistics
/save     - Save dataset manually
/train    - Show training instructions
/quit     - Exit
```

---

## 📊 Example Session

```
============================================================
EMOTION LLM - INTERACTIVE CHAT
============================================================
Model: Dataset-only mode
Dataset: chat_training_data.json
Auto-save: Enabled
============================================================

============================================================
PROFILE SETUP
============================================================
What's your name? Alex
How old are you? (5-16): 9
Can I remember your name and preferences? yes
What's your favorite color? blue

✓ Profile saved! Hi Alex!
============================================================

============================================================
CHAT MODE
============================================================
Commands:
  /emotion - Change emotion
  /stats   - View statistics
  /save    - Save dataset
  /train   - Start training
  /quit    - Exit chat
============================================================

[neutral] You: Why is the sky blue?
AI: That's an interesting question! I'm still learning...

[neutral] You: /emotion
Available emotions: happy, sad, angry, surprised, neutral, confused, excited, worried
Set emotion: excited

[excited] You: I love learning about space!
AI: That's wonderful! Space is fascinating...

[excited] You: /stats

============================================================
STATISTICS
============================================================
Dataset examples: 2
Current session: 2 messages
Memory stats: {'total_interactions': 2, 'short_term_count': 2...}
============================================================

[excited] You: /quit
Goodbye! 👋

✓ Saved 2 examples to chat_training_data.json
```

---

## 🎓 Training with Your Conversations

### 1. Collect Data
```bash
# Chat for a while, building your dataset
python chat.py

# Check your dataset
python -c "import json; print(f'{len(json.load(open(\"chat_training_data.json\"))[\"examples\"])} examples')"
```

### 2. Combine with Generated Data
```bash
# Generate more examples
python generate_dataset.py --size 10000 --output generated_data.json

# Merge datasets (create merge script or manually combine)
```

### 3. Train Model
```bash
# Train with your chat data
python train_lora.py --dataset chat_training_data.json --epochs 3

# Or combine with generated data
python train_lora.py --dataset combined_dataset.json --epochs 3
```

### 4. Use Your Trained Model
```bash
# Quantize
python quantize_model.py --model ./emotion-llm-finetuned

# Chat with your custom model
python chat.py --model quantized_models/model-q4_k_m.gguf
```

---

## 🍓 Raspberry Pi Usage

### Setup on Pi
```bash
# Copy files to Pi
scp chat.py safety_filter.py memory_manager.py emotion_prompt_template.py \
    pi@raspberrypi.local:~/emotion-llm/

# SSH into Pi
ssh pi@raspberrypi.local
cd ~/emotion-llm
```

### Run on Pi
```bash
# Dataset-only mode (no model needed)
python3 chat.py

# With model (if you have one)
python3 chat.py --model model-q4_k_m.gguf
```

**Performance**: Works great on Pi 5! Responses in ~1.5 seconds with model.

---

## 🔧 Advanced Usage

### Custom Dataset Path
```bash
python chat.py --dataset my_custom_data.json
```

### Disable Auto-Save
```bash
python chat.py --no-auto-save
# Use /save command to save manually
```

### Integration with Emotion Detection
```python
# Modify chat.py to auto-detect emotions
import cv2

# In chat_loop(), before getting input:
frame = camera.read()
emotion = detect_emotion(frame)
self.current_emotion = emotion
```

---

## 📁 Output Files

### chat_training_data.json
Your training dataset with all conversations:
```json
{
  "dataset_info": {
    "total_examples": 50,
    "created_at": "2026-01-09T...",
    "source": "interactive_chat"
  },
  "examples": [
    {
      "input": {
        "emotion": "happy",
        "age_group": 9,
        "question": "Why is the sky blue?"
      },
      "output": "Great question! ..."
    }
  ]
}
```

### chat_memory.json
Conversation memory (if consent given):
```json
{
  "user_profile": {
    "name": "Alex",
    "favorite_color": "blue"
  },
  "short_term": [...]
}
```

---

## 💡 Tips

### Building a Good Dataset
1. **Vary emotions**: Use `/emotion` to change emotional context
2. **Different ages**: Test with different age groups
3. **Diverse topics**: Ask about science, feelings, school, etc.
4. **Natural language**: Chat naturally, not just Q&A

### Incremental Learning
1. Chat and collect 100+ examples
2. Train for 1 epoch (quick)
3. Test the model
4. Collect more data
5. Retrain with combined dataset

### Safety
- All conversations go through safety filter
- Inappropriate content is blocked
- Sensitive topics redirect to adults
- You can review dataset before training

---

## 🐛 Troubleshooting

**"No module named 'inference_engine'"**
- Normal! Chat works without model in dataset-only mode

**"Model not found"**
- Check model path
- Or run without `--model` flag for dataset-only mode

**Slow on Raspberry Pi**
- Use Q4_K_S quantization (smaller, faster)
- Reduce response length in inference_engine.py

---

## 🎯 Use Cases

### 1. Dataset Collection
```bash
# Collect real conversations from kids (with parental consent)
python chat.py
# Creates authentic training data!
```

### 2. Model Testing
```bash
# Test your trained model interactively
python chat.py --model your_model.gguf
```

### 3. Continuous Learning
```bash
# Use model, collect feedback, retrain
python chat.py --model model.gguf
# Chat, save data, retrain periodically
```

### 4. AI Mirror Integration
```python
# Integrate with camera and TTS
# See chat.py for modification points
```

---

## Summary

**To use the chat interface:**
```bash
# Simple: Just chat and build dataset
python chat.py

# Advanced: Chat with your trained model
python chat.py --model your_model.gguf
```

**Your conversations automatically become training data!**

This is perfect for:
- Building custom datasets
- Testing models interactively
- Continuous learning from real conversations
- Running on Raspberry Pi

Start chatting and building your dataset now! 🚀
