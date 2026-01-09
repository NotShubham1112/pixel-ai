"""
Convert fine-tuned model to GGUF format for Raspberry Pi deployment.
Supports INT4/INT8 quantization for optimal performance.
"""

import os
import subprocess
import argparse
from pathlib import Path


class ModelQuantizer:
    """Quantize and convert models to GGUF format for llama.cpp."""
    
    QUANTIZATION_METHODS = {
        "Q4_K_M": "4-bit quantization, medium quality (recommended for Pi)",
        "Q4_K_S": "4-bit quantization, small size",
        "Q5_K_M": "5-bit quantization, better quality",
        "Q8_0": "8-bit quantization, high quality, larger size"
    }
    
    def __init__(self, model_path: str, output_dir: str = "./quantized_models"):
        self.model_path = Path(model_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def check_llama_cpp(self):
        """Check if llama.cpp is installed."""
        print("Checking for llama.cpp installation...")
        
        llama_cpp_path = Path("llama.cpp")
        
        if not llama_cpp_path.exists():
            print("⚠ llama.cpp not found. Installing...")
            print("\nPlease run these commands:")
            print("  git clone https://github.com/ggerganov/llama.cpp")
            print("  cd llama.cpp")
            print("  make")
            print("\nOr on Windows:")
            print("  git clone https://github.com/ggerganov/llama.cpp")
            print("  cd llama.cpp")
            print("  cmake -B build")
            print("  cmake --build build --config Release")
            return False
        
        print("✓ llama.cpp found")
        return True
    
    def convert_to_gguf(self):
        """Convert HuggingFace model to GGUF format."""
        print(f"Converting {self.model_path} to GGUF format...")
        
        gguf_path = self.output_dir / "model-f16.gguf"
        
        # Use llama.cpp's convert script
        convert_script = Path("llama.cpp") / "convert-hf-to-gguf.py"
        
        if not convert_script.exists():
            print(f"⚠ Conversion script not found at {convert_script}")
            print("Please ensure llama.cpp is properly installed.")
            return None
        
        cmd = [
            "python",
            str(convert_script),
            str(self.model_path),
            "--outfile", str(gguf_path),
            "--outtype", "f16"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Conversion failed: {result.stderr}")
            return None
        
        print(f"✓ Converted to GGUF: {gguf_path}")
        return gguf_path
    
    def quantize_model(self, gguf_path: Path, method: str = "Q4_K_M"):
        """Quantize GGUF model."""
        print(f"Quantizing with method: {method} - {self.QUANTIZATION_METHODS[method]}")
        
        output_path = self.output_dir / f"model-{method.lower()}.gguf"
        
        quantize_bin = Path("llama.cpp") / "build" / "bin" / "quantize"
        if not quantize_bin.exists():
            # Try alternative path
            quantize_bin = Path("llama.cpp") / "quantize"
        
        if not quantize_bin.exists():
            print(f"⚠ Quantize binary not found. Please build llama.cpp first.")
            return None
        
        cmd = [
            str(quantize_bin),
            str(gguf_path),
            str(output_path),
            method
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Quantization failed: {result.stderr}")
            return None
        
        # Get file size
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✓ Quantized model saved: {output_path}")
        print(f"  Size: {size_mb:.2f} MB")
        
        return output_path
    
    def quantize_all_methods(self, gguf_path: Path):
        """Quantize with all available methods for comparison."""
        print("\nQuantizing with all methods for comparison...")
        
        results = {}
        for method in self.QUANTIZATION_METHODS.keys():
            output_path = self.quantize_model(gguf_path, method)
            if output_path:
                results[method] = output_path
        
        print("\n" + "="*60)
        print("QUANTIZATION SUMMARY")
        print("="*60)
        for method, path in results.items():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"{method:12} - {size_mb:6.2f} MB - {path}")
        print("="*60)
        print("\nRecommended for Raspberry Pi 5: Q4_K_M (best balance)")
        print("For 4GB Pi: Use Q4_K_S (smaller)")
        print("For 8GB Pi: Can use Q5_K_M (better quality)")
        
        return results
    
    def full_conversion(self, quantization_method: str = "Q4_K_M"):
        """Complete conversion pipeline."""
        print("="*60)
        print("EMOTION LLM - MODEL QUANTIZATION FOR RASPBERRY PI")
        print("="*60)
        
        # Step 1: Check llama.cpp
        if not self.check_llama_cpp():
            print("\n❌ Please install llama.cpp first.")
            return None
        
        # Step 2: Convert to GGUF
        gguf_path = self.convert_to_gguf()
        if not gguf_path:
            return None
        
        # Step 3: Quantize
        quantized_path = self.quantize_model(gguf_path, quantization_method)
        
        if quantized_path:
            print("\n" + "="*60)
            print("✓ QUANTIZATION COMPLETE!")
            print("="*60)
            print(f"Quantized model: {quantized_path}")
            print(f"\nNext steps:")
            print(f"1. Copy {quantized_path} to your Raspberry Pi")
            print(f"2. Install llama.cpp on Pi: see deploy_raspberry_pi.md")
            print(f"3. Test inference: python inference_engine.py --model {quantized_path}")
            print("="*60)
        
        return quantized_path


def main():
    parser = argparse.ArgumentParser(description="Quantize emotion LLM for Raspberry Pi")
    parser.add_argument("--model", type=str, required=True, help="Path to fine-tuned model directory")
    parser.add_argument("--output", type=str, default="./quantized_models", help="Output directory")
    parser.add_argument("--method", type=str, default="Q4_K_M", 
                       choices=["Q4_K_M", "Q4_K_S", "Q5_K_M", "Q8_0"],
                       help="Quantization method")
    parser.add_argument("--all", action="store_true", help="Quantize with all methods for comparison")
    
    args = parser.parse_args()
    
    quantizer = ModelQuantizer(args.model, args.output)
    
    if args.all:
        gguf_path = quantizer.convert_to_gguf()
        if gguf_path:
            quantizer.quantize_all_methods(gguf_path)
    else:
        quantizer.full_conversion(args.method)


if __name__ == "__main__":
    main()
