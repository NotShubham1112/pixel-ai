"""
Download 2-bit quantized model for maximum speed on Raspberry Pi.
Size: ~150MB (vs 400MB for 4-bit)
Speed: ~2x faster inference
Quality: Still good for most tasks!
"""

print("Downloading 2-bit quantized Qwen2.5-0.5B model...")
print("Size: ~150MB (much smaller!)")
print("Speed: 2x faster than 4-bit")
print("\nInstalling huggingface-hub if needed...")

import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "huggingface-hub"])

from huggingface_hub import hf_hub_download

print("\nDownloading 2-bit model...")

try:
    model_path = hf_hub_download(
        repo_id="bartowski/Qwen2.5-0.5B-Instruct-GGUF",
        filename="Qwen2.5-0.5B-Instruct-Q2_K.gguf",  # 2-bit version
        local_dir="./models",
        local_dir_use_symlinks=False
    )
    
    print("\n" + "="*60)
    print("✓ 2-BIT MODEL DOWNLOADED!")
    print("="*60)
    print(f"Location: {model_path}")
    print(f"\nSize comparison:")
    print(f"  2-bit (Q2_K):  ~150MB ← You just downloaded this")
    print(f"  4-bit (Q4_K):  ~400MB (your other model)")
    print(f"\nSpeed: ~2x faster on Raspberry Pi!")
    print(f"Quality: Good for most questions")
    print(f"\nUse it:")
    print(f"  python chat_simple.py  # Will auto-detect")
    print(f"  # Or specify: python chat.py --model {model_path}")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nAlternative: Download manually from:")
    print("https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF")
    print("File: Qwen2.5-0.5B-Instruct-Q2_K.gguf")
