# PDF-to-Markdown Project with MinerU

This project uses MinerU (Magic-PDF) to convert PDF documents into structured Markdown with LaTeX formulas.

## Environment Setup

The environment `PDF-to-Markdown` has been created with Python 3.10 and necessary dependencies.

### Activation
To activate the environment, run:
```powershell
conda activate PDF-to-Markdown
```

### Dependencies
- **MinerU**: PDF extraction tool
- **PyTorch**: GPU-accelerated (CUDA 12.4)
- **ONNX Runtime**: GPU-accelerated (CUDA 12.x via `nvidia-cudnn-cu12`)

## Usage

1. **Prepare your PDF file**.
2. **Run the processing script**:
   ```powershell
   python "C:\Users\user\Desktop\Code-Project\Python-project\PDF-to-Markdown\run_mineru.py"
   ```
   Or simply:
   ```powershell
   cd "C:\Users\user\Desktop\Code-Project\Python-project\PDF-to-Markdown"
   python run_mineru.py
   ```
3. **Enter the PDF path** when prompted.

The script will:
- Set up the environment (CUDA paths).
- Run MinerU extraction.
- Save output to `Result-for-project/PDF-to-Markdown`.

## Configuration
- Model weights are located in `models/models/OpenDataLab/PDF-Extract-Kit-1___0/models`.
- Configuration files `magic-pdf.json` and `mineru.json` are in your user home directory (`C:\Users\user`).

## Troubleshooting
- If you encounter "DLL load failed" for ONNX Runtime, ensure `nvidia-cudnn-cu12` is installed (it should be). The `run_mineru.py` script automatically adds necessary DLLs to PATH.
