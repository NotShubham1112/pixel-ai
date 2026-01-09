"""
Download Qwen2.5-0.5B model from Hugging Face for offline use.
This downloads the base model that you can use immediately or fine-tune later.
"""

import os
from pathlib import Path

def download_model():
    """Download model using huggingface-hub."""
    
    print("="*60)
    print("DOWNLOADING QWEN2.5-0.5B MODEL FROM HUGGING FACE")
    print("="*60)
    
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("\n⚠ huggingface-hub not installed!")
        print("\nInstalling now...")
        os.system("pip install huggingface-hub")
        from huggingface_hub import snapshot_download
    
    # Model to download
    model_id = "Qwen/Qwen2.5-0.5B-Instruct"
    local_dir = "./models/qwen2.5-0.5b-instruct"
    
    print(f"\nModel: {model_id}")
    print(f"Download to: {local_dir}")
    print(f"\nThis will download ~1GB of files...")
    print("Please wait...\n")
    
    try:
        # Download the model
        snapshot_download(
            repo_id=model_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        print("\n" + "="*60)
        print("✓ MODEL DOWNLOADED SUCCESSFULLY!")
        print("="*60)
        print(f"Location: {Path(local_dir).absolute()}")
        print(f"\nYou can now:")
        print(f"1. Use it for training:")
        print(f"   python train_lora.py --base-model {local_dir}")
        print(f"\n2. Or download pre-quantized GGUF version for immediate use")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading: {e}")
        print("\nTry manual download:")
        print(f"1. Visit: https://huggingface.co/{model_id}")
        print(f"2. Click 'Files and versions'")
        print(f"3. Download all files to: {local_dir}")
        return False


def download_gguf_model():
    """Download pre-quantized GGUF model (ready to use immediately)."""
    
    print("\n" + "="*60)
    print("DOWNLOADING PRE-QUANTIZED GGUF MODEL")
    print("="*60)
    
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        os.system("pip install huggingface-hub")
        from huggingface_hub import hf_hub_download
    
    # GGUF model (ready to use with llama.cpp)
    # Using a community GGUF version that's actually available
    repo_id = "bartowski/Qwen2.5-0.5B-Instruct-GGUF"
    filename = "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"
    local_dir = "./models"
    
    print(f"\nModel: {repo_id}")
    print(f"File: {filename}")
    print(f"Size: ~400MB")
    print(f"\nDownloading...\n")
    
    try:
        model_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        print("\n" + "="*60)
        print("✓ GGUF MODEL DOWNLOADED!")
        print("="*60)
        print(f"Location: {Path(model_path).absolute()}")
        print(f"\nYou can use it RIGHT NOW:")
        print(f"  python chat.py --model {model_path}")
        print("="*60)
        
        return model_path
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def main():
    """Main download function."""
    
    print("\nChoose what to download:\n")
    print("1. GGUF Model (400MB) - Ready to use immediately with chat.py")
    print("2. Full Model (1GB) - For training/fine-tuning")
    print("3. Both")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        download_gguf_model()
    elif choice == "2":
        download_model()
    elif choice == "3":
        download_gguf_model()
        download_model()
    else:
        print("Invalid choice. Downloading GGUF model (recommended)...")
        download_gguf_model()


if __name__ == "__main__":
    main()
