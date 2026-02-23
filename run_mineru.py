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
    conda_prefix = os.environ.get("CONDA_PREFIX", r"D:\anaconda\envs\Code-Project")
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
    conda_prefix = os.environ.get("CONDA_PREFIX", r"D:\anaconda\envs\Code-Project")
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
            print(f"Warning: {assets_dir} already exists. Merging/Overwriting...")
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
            new_content = content.replace("images/", "assets/")
            md_file.write_text(new_content, encoding='utf-8')
            print(f"Updated Markdown asset links in: {md_file}")
        except Exception as e:
            print(f"Error updating Markdown file: {e}")

def optimize_output(output_dir, pdf_stem):
    """
    Compress non-markdown files and remove origin pdf.
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

    # 2. Compress assets
    md_file = output_dir / f"{pdf_stem}.md"
    zip_path = output_dir / "assets.zip"
    
    files_to_zip = []
    dirs_to_zip = []
    
    for item in output_dir.iterdir():
        if item.name == md_file.name or item.name == zip_path.name:
            continue
        if item.is_file():
            files_to_zip.append(item)
        elif item.is_dir():
            dirs_to_zip.append(item)
            
    if not files_to_zip and not dirs_to_zip:
        print("No assets to compress.")
        return

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_zip:
                zipf.write(file, arcname=file.name)
            for directory in dirs_to_zip:
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(output_dir)
                        zipf.write(file_path, arcname=arcname)
        
        print(f"Compressed assets to: {zip_path}")
        
        # Verify zip exists and is valid before deleting
        if zip_path.exists() and zipfile.is_zipfile(zip_path):
            for file in files_to_zip:
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Error deleting file {file}: {e}")
            for directory in dirs_to_zip:
                try:
                    shutil.rmtree(directory)
                except Exception as e:
                    print(f"Error deleting directory {directory}: {e}")
            print("Cleaned up uncompressed assets.")
            
            # Add note to MD
            if md_file.exists():
                content = md_file.read_text(encoding='utf-8')
                note = "> **Note:** Images and other assets have been compressed into `assets.zip` to save space. Unzip it to view images.\n\n"
                md_file.write_text(note + content, encoding='utf-8')
                
    except Exception as e:
        print(f"Error during compression: {e}")

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

def process_pdf(pdf_path_str):
    # Check if path is just a filename in input dir
    # Use Path(__file__).resolve() to avoid relative path issues
    script_path = Path(__file__).resolve()
    # Assuming script is in Python-project/PDF-to-Markdown/
    project_root = script_path.parent.parent.parent # Code-Project
    
    # Ensure relative paths are correct
    # Input dir: Python-project/PDF-to-Markdown/input
    input_dir = script_path.parent / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    
    # Cache dir: Python-project/PDF-to-Markdown/.cache
    cache_dir = script_path.parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = Path(pdf_path_str)
    if not pdf_path.exists():
        # Try input dir
        pdf_path_in_input = input_dir / pdf_path_str
        if pdf_path_in_input.exists():
            pdf_path = pdf_path_in_input
        else:
            print(f"Error: File not found: {pdf_path_str}")
            print(f"Checked absolute path and: {pdf_path_in_input}")
            return

    print(f"Processing PDF: {pdf_path}")
    
    # Define output base: Result-for-project/PDF-to-Markdown
    output_base = project_root / "Result-for-project" / "PDF-to-Markdown"
    output_base.mkdir(parents=True, exist_ok=True)
    
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
    
    print(f"Running MinerU...")
    
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"
    # Set cache directories to project local
    env["HF_HOME"] = str(cache_dir / "huggingface")
    env["MODELSCOPE_CACHE"] = str(cache_dir / "modelscope")
    # Disable symlinks for HF to avoid Windows errors
    env["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    # Force local model source
    env["MINERU_MODEL_SOURCE"] = "local"

    print(f"Environment variables set:")
    print(f"  HF_HOME: {env['HF_HOME']}")
    print(f"  MINERU_MODEL_SOURCE: {env['MINERU_MODEL_SOURCE']}")

    try:
        # Pre-check model existence
        import json
        mineru_config = Path.home() / "mineru.json"
        if mineru_config.exists():
            data = json.loads(mineru_config.read_text(encoding='utf-8'))
            models_dir = data.get("models-dir", {}).get("pipeline")
            if models_dir:
                # Check for a specific model file to verify path correctness
                # Expected path: models_dir/models/MFD/YOLO/yolo_v8_ft.pt
                test_path = Path(models_dir) / "models" / "MFD" / "YOLO" / "yolo_v8_ft.pt"
                print(f"Checking model path: {test_path}")
                if test_path.exists():
                    print("  [OK] Model file found.")
                else:
                    print("  [ERROR] Model file NOT found at expected path!")
                    # Try to find where it is
                    possible_path = Path(models_dir) / "MFD" / "YOLO" / "yolo_v8_ft.pt"
                    if possible_path.exists():
                        print(f"  [INFO] Found it at {possible_path}. The config path might include 'models' already?")
                    else:
                        print("  [ERROR] Could not locate model file in subdirectories.")
        else:
            print("mineru.json not found in home directory.")

        print("Starting MinerU execution...")
        print("This process may take some time depending on the PDF size and GPU performance.")
        print("Please wait...")
        sys.stdout.flush()

        subprocess.run(cmd, env=env, check=True)
        print("MinerU execution completed successfully.")
        
        # Post-processing for assets
        pdf_stem = pdf_path.stem
        # MinerU output structure: output_base / pdf_stem
        output_dir = output_base / pdf_stem
        
        if output_dir.exists():
            post_process_assets(output_dir, pdf_stem)
            optimize_output(output_dir, pdf_stem)
            create_changing_description(output_base, pdf_path)
            print(f"\nSuccess! Output saved to: {output_dir}")
        else:
            print(f"\nWarning: Output directory not found at {output_dir}")
            
    except subprocess.CalledProcessError as e:
        print(f"\nError running mineru: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    setup_cuda_env()
    
    if len(sys.argv) > 1:
        pdf_input = sys.argv[1]
    else:
        print("Please enter the path to the PDF file to process:")
        pdf_input = input().strip()
        # Remove quotes
        if (pdf_input.startswith('"') and pdf_input.endswith('"')) or \
           (pdf_input.startswith("'") and pdf_input.endswith("'")):
            pdf_input = pdf_input[1:-1]
            
    if pdf_input:
        process_pdf(pdf_input)
    else:
        print("No PDF path provided.")
