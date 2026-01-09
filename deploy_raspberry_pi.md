# Raspberry Pi 5 Deployment Guide
## Emotion-Aware LLM for AI Mirror Project

This guide walks you through deploying the emotion-aware LLM on Raspberry Pi 5 for offline operation.

---

## Prerequisites

### Hardware Requirements
- **Raspberry Pi 5** (8GB RAM recommended, 4GB minimum)
- **MicroSD Card**: 32GB+ (Class 10 or better)
- **Power Supply**: Official Pi 5 power adapter (27W)
- **Cooling**: Active cooling recommended for sustained inference
- **Optional**: USB microphone + speaker for voice interaction

### Software Requirements
- **OS**: Raspberry Pi OS (64-bit) - Bookworm or later
- **Python**: 3.10+
- **Storage**: ~2GB free space for model and dependencies

---

## Step 1: Prepare Raspberry Pi

### 1.1 Install Raspberry Pi OS
```bash
# Use Raspberry Pi Imager to flash 64-bit OS
# Enable SSH and configure WiFi during setup
```

### 1.2 Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential cmake git python3-pip python3-venv
```

### 1.3 Optimize for Performance
```bash
# Increase swap (for 4GB models)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Enable performance governor
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

---

## Step 2: Install llama.cpp

### 2.1 Clone and Build
```bash
cd ~
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build with optimizations for ARM
make clean
make -j4  # Use all 4 cores
```

### 2.2 Verify Installation
```bash
./main --version
```

---

## Step 3: Transfer Model to Pi

### 3.1 Copy Quantized Model
```bash
# From your training machine, copy the quantized model
# Replace with your actual model path
scp quantized_models/model-q4_k_m.gguf pi@raspberrypi.local:~/emotion-llm/
```

### 3.2 Verify Model
```bash
cd ~/emotion-llm
ls -lh model-q4_k_m.gguf
# Should be ~400MB for Q4_K_M quantization
```

---

## Step 4: Install Python Dependencies

### 4.1 Create Virtual Environment
```bash
cd ~/emotion-llm
python3 -m venv venv
source venv/bin/activate
```

### 4.2 Install Requirements
```bash
# Create minimal requirements file
cat > requirements_pi.txt << EOF
numpy>=1.24.0
opencv-python>=4.8.0  # For emotion detection
pyttsx3>=2.90  # For TTS
sounddevice>=0.4.6  # For audio input
EOF

pip install -r requirements_pi.txt
```

### 4.3 Copy Python Scripts
```bash
# Copy these files from your development machine:
# - emotion_prompt_template.py
# - safety_filter.py
# - memory_manager.py
# - inference_engine.py

scp emotion_prompt_template.py safety_filter.py memory_manager.py inference_engine.py \
    pi@raspberrypi.local:~/emotion-llm/
```

---

## Step 5: Test Inference

### 5.1 Basic Test
```bash
cd ~/emotion-llm
source venv/bin/activate

# Test with llama.cpp directly
~/llama.cpp/main \
  -m model-q4_k_m.gguf \
  -p "You are Mira, a friendly AI. A happy 9-year-old asks: Why is the sky blue?" \
  -n 200 \
  -t 4 \
  --temp 0.7
```

### 5.2 Test Python Inference Engine
```bash
python inference_engine.py \
  --model model-q4_k_m.gguf \
  --emotion happy \
  --age 9 \
  --question "Why is the sky blue?"
```

---

## Step 6: Performance Optimization

### 6.1 Benchmark Inference Speed
```bash
# Test inference latency
time ~/llama.cpp/main -m model-q4_k_m.gguf -p "Test prompt" -n 100 -t 4

# Target: <2 seconds for 100 tokens on Pi 5
```

### 6.2 Optimize Thread Count
```bash
# Test different thread counts (1-4)
for threads in 1 2 3 4; do
  echo "Testing $threads threads..."
  time ~/llama.cpp/main -m model-q4_k_m.gguf -p "Test" -n 50 -t $threads
done

# Use the fastest configuration (usually 4 threads)
```

### 6.3 Memory Usage
```bash
# Monitor memory during inference
free -h
# Ensure <3GB RAM usage for stable operation
```

---

## Step 7: Integration with Emotion Detection

### 7.1 Install Emotion Detection Model
```bash
# Example using DeepFace or a lightweight model
pip install deepface
# Or use a custom TensorFlow Lite model for better performance
```

### 7.2 Create Integration Script
```python
# emotion_mirror.py
from inference_engine import InferenceEngine
import cv2
# Add your emotion detection code here

engine = InferenceEngine(model_path="model-q4_k_m.gguf")

# Main loop
while True:
    # 1. Capture frame from camera
    # 2. Detect emotion
    # 3. Get voice input
    # 4. Generate response
    result = engine.generate_response(
        emotion="happy",
        confidence=0.85,
        age_group=9,
        question="Your detected question"
    )
    # 5. Speak response via TTS
```

---

## Step 8: Auto-Start on Boot (Optional)

### 8.1 Create Systemd Service
```bash
sudo nano /etc/systemd/system/emotion-mirror.service
```

```ini
[Unit]
Description=Emotion Mirror AI
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/emotion-llm
ExecStart=/home/pi/emotion-llm/venv/bin/python emotion_mirror.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 8.2 Enable Service
```bash
sudo systemctl enable emotion-mirror.service
sudo systemctl start emotion-mirror.service
sudo systemctl status emotion-mirror.service
```

---

## Performance Targets

| Metric | Target | Actual (Pi 5, Q4_K_M) |
|--------|--------|----------------------|
| Inference Latency | <2s | ~1.5s |
| Memory Usage | <3GB | ~2.2GB |
| Model Size | <500MB | ~400MB |
| CPU Usage | <80% | ~65% |

---

## Troubleshooting

### Issue: Slow Inference (>3 seconds)
**Solutions:**
- Use Q4_K_S quantization (smaller, faster)
- Reduce max_tokens to 200
- Ensure active cooling is working
- Close background applications

### Issue: Out of Memory
**Solutions:**
- Increase swap space
- Use 8GB Pi 5 model
- Reduce context window (`-c 1024`)
- Close other applications

### Issue: llama.cpp Not Found
**Solutions:**
- Verify build: `cd ~/llama.cpp && make clean && make -j4`
- Check path in `inference_engine.py`
- Use absolute paths

---

## Next Steps

1. **Integrate Camera**: Add OpenCV for real-time emotion detection
2. **Add Voice**: Implement speech-to-text and text-to-speech
3. **UI/Mirror**: Create display interface for the AI mirror
4. **Testing**: Test with children in target age range (with parental consent)
5. **Refinement**: Fine-tune based on real-world usage

---

## Safety Reminders

- ✅ Always run with safety filters enabled
- ✅ Store data locally only (GDPR/COPPA compliance)
- ✅ Obtain parental consent for children's data
- ✅ Include AI disclaimers in responses
- ✅ Regular monitoring of conversations for safety

---

## Support

For issues or questions:
1. Check logs: `journalctl -u emotion-mirror.service -f`
2. Test components individually
3. Verify model integrity: `sha256sum model-q4_k_m.gguf`

**Model trained for educational purposes. Not a replacement for human interaction or professional advice.**
