# 🚀 Pixel-AI Model: GitHub Release Guide

This guide ensures your GGUF models are hosted reliably and can be downloaded directly by the `pixel-ai` package without authentication.

---

## 1. Create a GitHub Release

### Option A: Using the GitHub UI (Web)
1. Go to your repository: `https://github.com/username/pixel-ai`
2. Click on **Releases** (right sidebar) → **Draft a new release**.
3. **Tag version**: Use `v0.1.0` (ensure it starts with `v`).
4. **Release title**: `Pixel-AI v0.1.0 - Early Alpha Model`
5. **Description**: Paste the [Release Notes Template](#3-release-notes-template) below.
6. **Binaries**: Drag and drop your `pixel_ai_gguf.gguf` file (~200-500 MB).
7. Click **Publish release**.

### Option B: Using GitHub CLI (`gh`)

> [!NOTE]
> It looks like `gh` is not installed on your system. You can [install it here](https://cli.github.com/) or just use **Option A (Web UI)** above.

If you have it installed, run this from the project root (`d:\llmemo`):
```powershell
# Create the release and upload your Qwen model
gh release create v0.1.0 ./models/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf --title "Pixel-AI v0.1.0" --notes "Initial Qwen2.5-0.5B GGUF model release"
```

---

## 2. Obtain the Direct Download URL

For `pixel-ai install` to work, use the **browser_download_url**.

> [!IMPORTANT]
> **Correct Format**:
> `https://github.com/username/pixel-ai/releases/download/v0.1.0/pixel_ai_gguf.gguf`
> 
> **Why?** This URL is unauthenticated and redirects directly to the asset storage, making it perfect for `pip` package scripts.

---

## 3. Release Notes Template

```markdown
## 🌟 Pixel-AI v0.1.0
Initial release of the Emotion Mirror LLM model (GGUF format).

### 📊 Model Details
- **Architecture**: Qwen2.5-0.5B (Quantized)
- **Quantization**: Q4_K_M
- **Size**: ~350 MB
- **Target Hardware**: Raspberry Pi 5 (Optimized for minimal RAM)

### 🛠 Installation
```bash
pip install pixel-ai
pixel-ai install
```

### 🔒 Security & Privacy
This model runs **100% offline**. No data leaves your Raspberry Pi.
```

---

## 4. Best Practices

- **Semantic Versioning**: Use `vMAJOR.MINOR.PATCH` (e.g., `v1.2.3`).
  - **MAJOR**: Breaking changes to model architecture.
  - **MINOR**: New features or retrained weights.
  - **PATCH**: Optimization or bug fixes.
- **Stability**: Never delete old releases! Users on older versions of your package might still depend on those URLs.
- **Checksums**: (Optional) Provide an MD5 or SHA256 hash in the release notes so users can verify the download.

---

## 5. Tip: Auto-Updating Model URLs

Instead of hardcoding the URL in `utils.py`, you can fetch the **latest** release URL via the GitHub API:

```python
# In utils.py
LATEST_RELEASE_API = "https://api.github.com/repos/username/pixel-ai/releases/latest"

def get_latest_model_url():
    r = requests.get(LATEST_RELEASE_API)
    assets = r.json().get('assets', [])
    for asset in assets:
        if asset['name'].endswith('.gguf'):
            return asset['browser_download_url']
    return DEFAULT_FALLBACK_URL
```
