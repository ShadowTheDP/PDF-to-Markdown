"""
PDF Content Inspector & Markdown Converter
==========================================

此腳本用於讀取 PDF 的完整內容（文字、圖片、表格、公式）並轉換為 Markdown 格式。
支援多頁處理、圖片 Base64 嵌入，並儘可能保留原始頁面結構。

Markdown 結構說明：
------------------
- `# Page {n}` : 頁碼標記
- `## Paragraphs` : 提取的文字段落
- `![image](data:image/png;base64,...)` : 嵌入的圖片（Base64 格式）
- `Table:` : 以 Markdown 表格格式呈現的資料
- `Formula/Text Blocks` : 包含數學公式或特殊排版的文字塊

依賴庫：
-------
- PyMuPDF (fitz): 用於文字與圖片提取
- pdfplumber: 用於表格提取
- base64: 用於圖片編碼
"""

import fitz  # PyMuPDF
import pdfplumber
import base64
import os
import io
from PIL import Image

# 目標 PDF 路徑
pdf_path = r"C:\Users\user\Desktop\Python\python source\IAIO training\part5_information theory.pdf"

def get_image_base64(pix):
    """將 PyMuPDF 的 pixmap 轉換為 Base64 字串"""
    img_data = pix.tobytes("png")
    return base64.b64encode(img_data).decode('utf-8')

def extract_tables(pdf_path, page_index):
    """使用 pdfplumber 提取指定頁面的表格"""
    tables_md = ""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_index]
        tables = page.extract_tables()
        for table in tables:
            if not table: continue
            tables_md += "\n### Table:\n"
            # 轉換為 Markdown 表格格式
            for i, row in enumerate(table):
                # 過濾 None 並轉換為字串
                row = [str(cell).replace('\n', ' ') if cell is not None else "" for cell in row]
                tables_md += "| " + " | ".join(row) + " |\n"
                if i == 0: # 添加分隔線
                    tables_md += "| " + " | ".join(["---"] * len(row)) + " |\n"
            tables_md += "\n"
    return tables_md

def inspect_pdf_to_markdown(path):
    """核心功能：解析 PDF 並生成 Markdown"""
    if not os.path.exists(path):
        print(f"錯誤：找不到檔案 {path}")
        return

    doc = fitz.open(path)
    output_md_path = os.path.splitext(path)[0] + "_content.md"
    # 若權限受限，改存在當前目錄
    try:
        md_file = open(output_md_path, "w", encoding="utf-8")
    except:
        output_md_path = "extracted_content.md"
        md_file = open(output_md_path, "w", encoding="utf-8")

    print(f"正在處理 PDF: {path}")
    print(f"總頁數: {len(doc)}")
    
    md_file.write(f"# PDF Content Extraction: {os.path.basename(path)}\n\n")

    for page_index in range(len(doc)):
        page = doc[page_index]
        print(f"正在處理第 {page_index + 1} 頁...")
        
        md_file.write(f"\n---\n# Page {page_index + 1}\n\n")
        
        # 1. 提取文字段落
        md_file.write("## Paragraphs\n")
        text = page.get_text("text")
        # 清除不合法的 Unicode 字符
        clean_text = text.encode('utf-8', 'ignore').decode('utf-8')
        md_file.write(clean_text + "\n\n")
        
        # 2. 提取表格 (使用 pdfplumber)
        try:
            tables_content = extract_tables(path, page_index)
            if tables_content:
                md_file.write(tables_content)
        except Exception as e:
            print(f"第 {page_index+1} 頁表格提取失敗: {e}")

        # 3. 提取圖片
        image_list = page.get_images(full=True)
        if image_list:
            md_file.write("## Images\n")
            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                # 如果是 CMYK 等特殊格式，先轉換為 RGB
                if pix.n - pix.alpha > 3:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                base64_str = get_image_base64(pix)
                md_file.write(f"![image_{page_index+1}_{img_index}](data:image/png;base64,{base64_str})\n\n")
                pix = None # 釋放內存

    md_file.close()
    doc.close()
    print(f"\n完成！內容已保存至: {output_md_path}")

if __name__ == "__main__":
    inspect_pdf_to_markdown(pdf_path)
