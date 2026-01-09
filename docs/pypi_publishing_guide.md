# 📦 Publishing Pixel-AI to PyPI (The "Short Command" Way)

To enable the simple `pip install pixel-ai` command for everyone, you must publish your code to the **Python Package Index (PyPI)**.

---

## 1. Create a PyPI Account
1. Go to [pypi.org/account/register/](https://pypi.org/account/register/) and create an account.
2. Enable **2FA** (Required for all PyPI users).
3. Create an **API Token** in your Account Settings. Copy it—you'll need it later.

---

## 2. Prepare for Upload
Run these commands in your `d:\llmemo` folder to install the necessary tools:
```powershell
pip install build twine
```

---

## 3. Build your Package
Run this to create the "distribution" files (the compressed version of your code):
```powershell
python -m build
```
This will create a `dist/` folder with two files: a `.tar.gz` and a `.whl`.

---

## 4. Upload to PyPI
Run this to send your code to the official Python registry:
```powershell
python -m twine upload dist/*
```
- **Username**: Use `__token__`
- **Password**: Paste your **API Token** (including the `pypi-` prefix).

---

## 5. Better Way: Auto-Publish with GitHub Actions
I have created a workflow at `.github/workflows/publish.yml`. This will automatically upload your code to PyPI every time you click "Publish Release" on GitHub.

### Setup "Trusted Publishing" (No Password Needed)
1. Log in to [PyPI.org](https://pypi.org).
2. Go to **Account Settings** -> **Publishing**.
3. Click **Add a new pending publisher**.
4. Fill in:
   - **PyPI Project Name**: `pixel-ai`
   - **Owner**: `NotShubham1112`
   - **Repository Name**: `pixel-ai`
   - **Workflow Name**: `publish.yml`
5. Click **Add**.

Now, whenever you create a new GitHub Release (like `v0.1.1`), GitHub will handle the PyPI upload for you!
