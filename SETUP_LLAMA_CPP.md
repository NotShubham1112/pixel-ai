# Quick Setup: Install llama.cpp for Windows

## ✅ Model Downloaded Successfully!
**Location**: `d:\llmemo\models\Qwen2.5-0.5B-Instruct-Q4_K_M.gguf` (398MB)

## ⚠️ Issue: llama.cpp Not Found

The chat interface needs llama.cpp to run the model. Here's how to install it:

---

## Option 1: Quick Install (Recommended)

### Step 1: Download Pre-built Binary
```powershell
cd d:\llmemo

# Download llama.cpp Windows release
Invoke-WebRequest -Uri "https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b4268-bin-win-avx2-x64.zip" -OutFile "llama.cpp.zip"

# Extract
Expand-Archive -Path llama.cpp.zip -DestinationPath llama.cpp

# Test
.\llama.cpp\llama-cli.exe --version
```

### Step 2: Update inference_engine.py
The path in `inference_engine.py` needs to point to the correct llama.cpp executable.

---

## Option 2: Build from Source (If pre-built doesn't work)

### Requirements:
- Visual Studio 2022 (Community Edition is free)
- CMake
- Git

### Steps:
```powershell
cd d:\llmemo

# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build with CMake
cmake -B build
cmake --build build --config Release

# The executable will be at: build\bin\Release\llama-cli.exe
```

---

## Option 3: Use Python Binding (Easiest!)

Instead of llama.cpp binary, use Python library:

```powershell
pip install llama-cpp-python
```

Then create a new file `chat_simple.py`:

```python
from llama_cpp import Llama

# Load model
llm = Llama(
    model_path="models/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=4
)

# Chat loop
print("Chat with Qwen2.5-0.5B (type 'quit' to exit)")
while True:
    question = input("\nYou: ")
    if question.lower() == 'quit':
        break
    
    response = llm(
        f"You are a helpful AI assistant. User asks: {question}",
        max_tokens=200,
        temperature=0.7,
        stop=["User:", "\n\n"]
    )
    
    print(f"AI: {response['choices'][0]['text']}")
```

Run it:
```powershell
python chat_simple.py
```

---

## Quick Test (Option 3 - Recommended)

Let me create this for you now!
