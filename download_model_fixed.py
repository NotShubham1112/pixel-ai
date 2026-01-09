"""Quick download of working GGUF model."""
import os

print("Installing huggingface-hub...")
os.system("pip install -q huggingface-hub")

print("\nDownloading Qwen2.5-0.5B GGUF model...")
print("Size: ~300MB")
print("This may take 5-10 minutes...\n")

from huggingface_hub import hf_hub_download

try:
    model_path = hf_hub_download(
        repo_id="bartowski/Qwen2.5-0.5B-Instruct-GGUF",
        filename="Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
        local_dir="./models",
        local_dir_use_symlinks=False
    )
    
    print("\n" + "="*60)
    print("✓ MODEL DOWNLOADED!")
    print("="*60)
    print(f"Location: {model_path}")
    print("\nUse it now:")
    print(f"  python chat.py --model {model_path}")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nAlternative: Download manually from:")
    print("https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF")
