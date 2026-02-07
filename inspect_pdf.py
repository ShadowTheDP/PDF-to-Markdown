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
"""

import os
import pymupdf4llm
import pathlib

def convert_pdf_to_markdown(pdf_path, output_dir):
    """
    使用 pymupdf4llm 將 PDF 轉換為 Markdown 並保存到指定目錄
    """
    if not os.path.exists(pdf_path):
        print(f"錯誤：找不到檔案 {pdf_path}")
        return

    file_name = pathlib.Path(pdf_path).stem
    output_path = os.path.join(output_dir, f"{file_name}.md")
    
    print(f"正在處理 PDF: {pdf_path}")
    
    try:
        # 使用 pymupdf4llm 進行轉換，這會自動處理表格和圖片嵌入
        md_text = pymupdf4llm.to_markdown(pdf_path, embed_images=True)
        
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_text)
            
        print(f"成功將 {pdf_path} 轉換為 {output_path}")
        return True
    except Exception as e:
        print(f"處理 {pdf_path} 時發生錯誤: {e}")
        return False

if __name__ == "__main__":
    # 定義輸入與輸出
    input_dir = r"C:\Users\user\Desktop\Python\python source\IAIO training"
    output_root = r"C:\Users\user\Desktop\Python\Result for project\PDF to Markdown"
    
    # 確保輸出根目錄存在
    os.makedirs(output_root, exist_ok=True)
    
    # 獲取所有 PDF
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    
    success_count = 0
    for pdf_file in pdf_files:
        full_path = os.path.join(input_dir, pdf_file)
        if convert_pdf_to_markdown(full_path, output_root):
            success_count += 1
            
    print(f"\n處理完成！成功轉換 {success_count}/{len(pdf_files)} 個檔案。")
