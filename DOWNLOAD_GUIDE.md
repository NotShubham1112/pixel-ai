# Download Model from Hugging Face - Quick Guide

## 🎯 Two Options

### Option 1: GGUF Model (Recommended - Use Immediately)
**Size**: ~400MB  
**Use**: Ready to chat right away  
**Best for**: Testing, immediate use, Raspberry Pi

### Option 2: Full Model (For Training)
**Size**: ~1GB  
**Use**: Fine-tuning with your dataset  
**Best for**: Custom training

---

## 🚀 Quick Download

### Automatic Download (Easiest)
```bash
cd d:\llmemo
python download_model.py
```

Follow the prompts:
- Choose option 1 for GGUF (immediate use)
- Choose option 2 for full model (training)
- Choose option 3 for both

---

## 📥 Manual Download (If Script Fails)

### For GGUF Model (Immediate Use)

1. **Visit**: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF

2. **Click**: "Files and versions" tab

3. **Download**: `qwen2-0_5b-instruct-q4_k_m.gguf` (~400MB)

4. **Save to**: `d:\llmemo\models\`

5. **Use it**:
```bash
python chat.py --model models/qwen2-0_5b-instruct-q4_k_m.gguf
```

### For Full Model (Training)

1. **Install git-lfs** (if not installed):
```bash
git lfs install
```

2. **Clone the model**:
```bash
cd d:\llmemo
git clone https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct models/qwen2.5-0.5b-instruct
```

3. **Use for training**:
```bash
python train_lora.py --base-model models/qwen2.5-0.5b-instruct
```

---

## ✅ After Download

### Test the GGUF Model
```bash
# Start chatting immediately!
python chat.py --model models/qwen2-0_5b-instruct-q4_k_m.gguf
```

### Or Train Your Custom Model
```bash
# Train with your dataset
python train_lora.py --dataset final_training_dataset.json --epochs 3
```

---

## 🔧 Troubleshooting

### "huggingface-hub not found"
```bash
pip install huggingface-hub
```

### "git-lfs not installed"
Download from: https://git-lfs.github.com/

### Slow download?
- Use a download manager
- Or download during off-peak hours
- Resume is supported if interrupted

---

## 📊 Model Comparison

| Model Type | Size | Use Case | Speed |
|------------|------|----------|-------|
| GGUF Q4_K_M | 400MB | Immediate chat | Fast |
| Full Model | 1GB | Training | N/A |
| Your Trained | 400MB | Custom responses | Fast |

---

## 🎯 Recommended Workflow

1. **Download GGUF** (quick test):
```bash
python download_model.py
# Choose option 1
```

2. **Test it**:
```bash
python chat.py --model models/qwen2-0_5b-instruct-q4_k_m.gguf
```

3. **If satisfied, train custom model**:
```bash
python train_lora.py --dataset final_training_dataset.json
```

4. **Use your custom model**:
```bash
python chat.py --model quantized_models/model-q4_k_m.gguf
```

---

## 💡 Pro Tips

- **GGUF model** works offline immediately
- **Full model** needed only for training
- Download once, use forever (offline)
- Models work on Windows, Linux, Mac, Raspberry Pi

---

## Summary

**Fastest way to get started:**
```bash
python download_model.py
# Choose 1 (GGUF)
# Wait 5-10 minutes
python chat.py --model models/qwen2-0_5b-instruct-q4_k_m.gguf
```

**You'll be chatting with a real LLM in minutes!** 🚀
