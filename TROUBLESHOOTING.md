# MinerU Local Environment Setup & Troubleshooting Log

This document records the process, challenges, and solutions for setting up a local MinerU (Magic-PDF) environment with GPU acceleration on Windows.

## Project Structure
- **Root Directory**: `Code-Project/Python-project/PDF-to-Markdown`
- **Core Script**: `run_mineru.py` (Automates environment setup and execution)
- **Models**: `models/` (Local storage for all AI weights)
- **Input**: `input/` (Place PDF files here)
- **Output**: `../../Result-for-project/PDF-to-Markdown` (Parsed Markdown and assets)

## Environment Specifications
- **OS**: Windows
- **Python**: 3.10 (Conda environment: `PDF-to-Markdown`)
- **GPU**: NVIDIA RTX 5060 (8GB VRAM)
- **CUDA**: 12.4
- **MinerU Version**: 2.7.6

## Troubleshooting Log

### 1. SSL/TLS Certificate Errors
**Issue**: `pip` failed to install packages due to `SSLCertVerificationError` (e.g., from `wheels.myhloli.com`).
**Solution**:
- Used `--trusted-host` flag during installation:
  ```bash
  pip install mineru[all] --extra-index-url https://wheels.myhloli.com --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host wheels.myhloli.com
  ```

### 2. ONNX Runtime GPU Issues
**Issue**: `AttributeError: module 'onnxruntime' has no attribute '__version__'` and missing CUDA provider.
**Solution**:
- Reinstalled `onnxruntime-gpu` specifically.
- Installed NVIDIA cuDNN and cuBLAS libraries via pip (`nvidia-cudnn-cu12`).
- Manually added NVIDIA library paths to `PATH` in `run_mineru.py` before importing MinerU modules.

### 3. Model Download & Path Configuration
**Issue**: MinerU tried to download models from Hugging Face/ModelScope despite local models being present, or failed to find local models.
**Solution**:
- **Downloaded Models**: Manually downloaded all weights to `models/` directory.
- **Config Fix**: Updated `magic-pdf.json` and `mineru.json` to point `models-dir` to the absolute path of the local model directory.
- **Path Format**: Ensured the path in JSON config ends correctly (removed trailing `\models` if it caused duplication in internal logic).
- **Environment Variables**: Set `MINERU_MODEL_SOURCE=local` in `run_mineru.py` to force local model usage.

### 4. Windows Symlink & Permission Errors (WinError 1314)
**Issue**: Hugging Face library tried to create symlinks for model cache, which requires Admin privileges on Windows.
**Solution**:
- Set environment variable `HF_HUB_DISABLE_SYMLINKS_WARNING=1`.
- Configured `HF_HOME` and `MODELSCOPE_CACHE` to local project directories to avoid system-wide permission issues.
- **Ultimate Fix**: By forcing `MINERU_MODEL_SOURCE=local` and ensuring `magic-pdf.json` was correct, we bypassed the need for Hugging Face caching entirely.

### 5. Terminal Output & Progress Visibility
**Issue**: `conda run` swallowed stdout/stderr, making the program appear "stuck" or "unresponsive".
**Solution**:
- Invoked the Python interpreter directly: `D:\anaconda\envs\Code-Project\python.exe run_mineru.py`.
- Added `-u` flag for unbuffered output: `python -u run_mineru.py`.
- Added explicit print statements and `sys.stdout.flush()` in the script.

### 6. Anti-Virus False Positives (.bat files)
**Issue**: Anti-virus flagged temp `.bat` files created by `conda run` as threats.
**Solution**:
- Switched to direct Python execution (`path/to/python.exe script.py`) instead of `conda run`, eliminating the generation of temporary batch scripts.

## Usage Guide

1.  **Activate Environment**:
    ```powershell
    conda activate PDF-to-Markdown
    ```
2.  **Run Parsing**:
    ```powershell
    python run_mineru.py "input_filename.pdf"
    ```
    *Note: The script automatically handles environment variables and model paths.*

3.  **Check Results**:
    Output is saved to `Code-Project/Result-for-project/PDF-to-Markdown/<filename>/auto`.
