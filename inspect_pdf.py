"""
PDF Content Inspector & Markdown Converter
==========================================

此腳本用於讀取 PDF 的完整內容（文字、圖片、表格、公式）並轉換為 Markdown 格式。
支援多頁處理、圖片 Base64 嵌入，並儘可能保留原始頁面結構。

依賴庫：
-------
- PyMuPDF (fitz): 用於文字與圖片提取
- pymupdf4llm: 用於高品質的 Markdown 轉換
- base64: 用於圖片編碼

使用方法：
---------
python inspect_pdf.py <input_pdf_path> <output_directory>
"""

import os
import sys
import argparse
import pathlib
import pymupdf4llm

def convert_pdf_to_markdown(pdf_path, output_dir):
    """
    使用 pymupdf4llm 將 PDF 轉換為 Markdown 並保存到指定目錄
    """
    if not os.path.exists(pdf_path):
        print(f"錯誤：找不到檔案 {pdf_path}")
        return False

    file_name = pathlib.Path(pdf_path).stem
    output_path = os.path.join(output_dir, f"{file_name}.md")
    
    print(f"正在處理 PDF: {pdf_path}")
    print(f"輸出目錄: {output_dir}")
    
    try:
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)

        # 使用 pymupdf4llm 進行轉換，這會自動處理表格和圖片嵌入
        # embed_images=True 會將圖片轉換為 Base64 嵌入到 Markdown 中
        md_text = pymupdf4llm.to_markdown(pdf_path, embed_images=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_text)
            
        print(f"成功將 {pdf_path} 轉換為 {output_path}")
        return True
    except Exception as e:
        print(f"處理 {pdf_path} 時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown with embedded images and tables.")
    parser.add_argument("input_pdf", help="Path to the input PDF file.")
    parser.add_argument("output_dir", help="Directory to save the output Markdown file.")
    
    args = parser.parse_args()
    
    success = convert_pdf_to_markdown(args.input_pdf, args.output_dir)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
