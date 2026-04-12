import os
import sys
import shutil
import subprocess
from pathlib import Path
import re
import datetime
import zipfile

def setup_cuda_env():
    """Ensure CUDA/cuDNN DLLs are in PATH for ONNX Runtime."""
    conda_prefix = os.environ.get("CONDA_PREFIX", r"D:\anaconda\envs\PDF-to-Markdown")
    site_packages = os.path.join(conda_prefix, "Lib", "site-packages")
    nvidia_paths = [
        os.path.join(site_packages, "nvidia", "cudnn", "bin"),
        os.path.join(site_packages, "nvidia", "cublas", "bin"),
    ]
    path_modified = False
    current_path = os.environ.get("PATH", "")
    
    for p in nvidia_paths:
        if os.path.exists(p) and p not in current_path:
            os.environ["PATH"] = p + os.pathsep + current_path
            path_modified = True
            
    if path_modified:
        print("Updated PATH with NVIDIA DLLs.")

def get_mineru_cmd():
    """Find mineru executable."""
    conda_prefix = os.environ.get("CONDA_PREFIX", r"D:\anaconda\envs\PDF-to-Markdown")
    mineru_exe = os.path.join(conda_prefix, "Scripts", "mineru.exe")
    if os.path.exists(mineru_exe):
        return mineru_exe
    
    cmd = shutil.which("mineru")
    if cmd:
        return cmd
        
    return [sys.executable, "-m", "mineru"]

def post_process_assets(output_dir, pdf_stem):
    """Rename images folder to assets and update markdown links."""
    images_dir = output_dir / "images"
    assets_dir = output_dir / "assets"
    md_file = output_dir / f"{pdf_stem}.md"
    
    # 1. Rename images -> assets
    if images_dir.exists():
        if assets_dir.exists():
            print(f"Warning: {assets_dir} already exists. Merging...")
            for item in images_dir.iterdir():
                dst = assets_dir / item.name
                if dst.exists():
                    dst.unlink()
                shutil.move(str(item), str(dst))
            images_dir.rmdir()
        else:
            images_dir.rename(assets_dir)
        print(f"Renamed 'images' directory to 'assets': {assets_dir}")
    
    # 2. Update Markdown content
    if md_file.exists():
        try:
            content = md_file.read_text(encoding='utf-8')
            # Replace images/filename.jpg with assets/filename.jpg
            # MinerU might use relative paths like ./images/ or just images/
            new_content = content.replace("images/", "assets/")
            md_file.write_text(new_content, encoding='utf-8')
            print(f"Updated Markdown asset links in: {md_file}")
        except Exception as e:
            print(f"Error updating Markdown file: {e}")

def optimize_output(output_dir, pdf_stem):
    """
    Remove intermediate files. (Zipping disabled as per asset accessibility requirements)
    """
    print(f"Optimizing output in {output_dir}...")
    
    # 1. Remove origin pdf
    origin_pdf = output_dir / f"{pdf_stem}_origin.pdf"
    if origin_pdf.exists():
        try:
            origin_pdf.unlink()
            print(f"Removed intermediate file: {origin_pdf.name}")
        except Exception as e:
            print(f"Error removing origin pdf: {e}")

def create_changing_description(output_base, pdf_path):
    """Create Changing Description.txt as required."""
    desc_file = output_base / "Changing Description.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""Time: {timestamp}
Processed Files:
- {pdf_path.name}
Conversion Parameters:
- Model Dir: Local
- Device: CUDA
- Table Recognition: Enabled (Slanet)
Output Path: {output_base}
"""
    try:
        if desc_file.exists():
            # Append to existing file
            with open(desc_file, "a", encoding="utf-8") as f:
                f.write("\n" + "-"*40 + "\n" + content)
        else:
            desc_file.write_text(content, encoding="utf-8")
        print(f"Updated Changing Description.txt at {desc_file}")
    except Exception as e:
        print(f"Error writing Changing Description.txt: {e}")

def process_pdf(pdf_path, output_base):
    pdf_path = Path(pdf_path)
    print(f"\n{'='*60}")
    print(f"Processing PDF: {pdf_path.name}")
    print(f"{'='*60}")
    
    script_path = Path(__file__).resolve()
    cache_dir = script_path.parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Run mineru command
    mineru_cmd = get_mineru_cmd()
    cmd = []
    if isinstance(mineru_cmd, list):
        cmd.extend(mineru_cmd)
    else:
        cmd.append(mineru_cmd)
        
    cmd.extend([
        "-p", str(pdf_path),
        "-o", str(output_base),
        "-m", "auto",
        "-b", "pipeline",
        "--device", "cuda",
        "--source", "local"
    ])
    
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"
    env["HF_HOME"] = str(cache_dir / "huggingface")
    env["MODELSCOPE_CACHE"] = str(cache_dir / "modelscope")
    env["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    env["MINERU_MODEL_SOURCE"] = "local"

    try:
        subprocess.run(cmd, env=env, check=True)
        
        # Post-processing for assets
        pdf_stem = pdf_path.stem
        # MinerU output structure: output_base / pdf_stem / auto (sometimes)
        pdf_output_dir = output_base / pdf_stem
        
        # Check if 'auto' subfolder exists and move its contents up
        auto_dir = pdf_output_dir / "auto"
        if auto_dir.exists():
            print(f"Moving contents from {auto_dir} to {pdf_output_dir}...")
            for item in auto_dir.iterdir():
                dst = pdf_output_dir / item.name
                if dst.exists():
                    if dst.is_dir():
                        shutil.rmtree(dst)
                    else:
                        dst.unlink()
                shutil.move(str(item), str(dst))
            auto_dir.rmdir()
        
        if pdf_output_dir.exists():
            post_process_assets(pdf_output_dir, pdf_stem)
            optimize_output(pdf_output_dir, pdf_stem)
            create_changing_description(output_base, pdf_path)
            print(f"Success! Result in: {pdf_output_dir}")
        else:
            print(f"Warning: Output directory not found for {pdf_stem}")
            
    except subprocess.CalledProcessError as e:
        print(f"Error running mineru for {pdf_path.name}: {e}")
    except Exception as e:
        print(f"Unexpected error for {pdf_path.name}: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process PDFs to Markdown using MinerU")
    parser.add_argument("input", help="Path to PDF file or directory containing PDFs")
    parser.add_argument("-o", "--output", help="Output base directory")
    
    args = parser.parse_args()
    
    setup_cuda_env()
    
    input_path = Path(args.input)
    if not args.output:
        script_path = Path(__file__).resolve()
        output_base = script_path.parent.parent.parent / "Result-for-project" / "PDF-to-Markdown"
    else:
        output_base = Path(args.output)
        
    output_base.mkdir(parents=True, exist_ok=True)
    
    if input_path.is_file():
        if input_path.suffix.lower() == ".pdf":
            process_pdf(input_path, output_base)
        else:
            print(f"Error: {input_path} is not a PDF file.")
    elif input_path.is_dir():
        pdf_files = list(input_path.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {input_path}")
        else:
            print(f"Found {len(pdf_files)} PDF files. Starting batch processing...")
            for pdf_file in pdf_files:
                process_pdf(pdf_file, output_base)
    else:
        print(f"Error: Input path {input_path} not found.")

