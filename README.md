# PDF 內容解析與 Markdown 轉換工具 (inspect_pdf.py)

此工具專為 IAIO 訓練課程設計，旨在自動化提取 PDF 講義中的多維度資訊，並將其轉換為結構化的 Markdown 檔案，方便後續的知識整理與 Manim 動畫規劃。

## 核心功能

1.  **完整文字提取**：使用 `PyMuPDF` (fitz) 提取所有頁面的文字，並自動清理 Unicode Surrogate 字符以防編碼錯誤。
2.  **表格自動識別**：整合 `pdfplumber` 的表格識別引擎，將 PDF 中的表格轉換為標準 Markdown 表格格式。
3.  **圖片嵌入**：自動偵測頁面中的圖片，並將其轉換為 Base64 編碼直接嵌入 Markdown 檔案中。
4.  **分頁結構保留**：每個頁面都會有清晰的 `# Page {n}` 標記，方便定位。

## Markdown 欄位含義說明

| 標籤/格式 | 含義 | 備註 |
| :--- | :--- | :--- |
| `# Page {n}` | **頁碼標題** | 表示當前內容所屬的 PDF 原始頁碼。 |
| `## Paragraphs` | **文字段落** | 提取出的純文字內容，保留基本的換行。 |
| `![image](data:...)` | **圖片 (Base64)** | PDF 中的插圖或公式圖片，已嵌入為 PNG 格式。 |
| `### Table:` | **表格資料** | 以 Markdown 表格呈現的表格數據。 |
| `Formula/Text` | **公式與特殊塊** | 數學公式通常會出現在文字段落中，或作為圖片提取。 |

## 環境需求

請確保在 `myenv` 虛擬環境中運行，並已安裝以下依賴：
- `PyMuPDF` (fitz)
- `pdfplumber`
- `Pillow` (PIL)

## 使用方法

1.  在 `inspect_pdf.py` 中修改 `pdf_path` 為目標 PDF 的絕對路徑。
2.  執行指令：
    ```bash
    .\myenv\Scripts\python.exe "IAIO knowledge demonstration\inspect_pdf.py"
    ```
3.  輸出的 Markdown 檔案將保存在 PDF 所在目錄，檔名後綴為 `_content.md`。
