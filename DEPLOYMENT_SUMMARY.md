# MinerU (Magic-PDF) 本地部署與自動化流程總結

本文件對照 AI Coder 的自身指示詞，記錄了 MinerU 在本地環境的佈署細節與自動化腳本邏輯，確保後續可直接進行高效轉換。

## 1. 環境佈置對照 (Conda 驅動)

| 指示詞要求 | 執行狀態 | 具體配置詳情 |
| :--- | :---: | :--- |
| **虛擬環境管理** | ✅ 已達成 | 使用 Conda 建立，名稱為 `PDF-to-Markdown`。 |
| **Python 版本** | ✅ 已達成 | Python 3.10.19 (MinerU 最佳相容版本)。 |
| **核心庫安裝** | ✅ 已達成 | 安裝 `mineru[all]` 並配置 `onnxruntime-gpu` (CUDA 12.8)。 |
| **模型權重配置** | ✅ 已達成 | 權重存放於 `D:\anaconda\envs\PDF-to-Markdown\Lib\site-packages\magic_pdf\models`，並已更新 `~/magic-pdf.json`。 |

## 2. 自動化腳本功能 ([run_mineru.py](file:///c:/Users/user/Desktop/Code-Project/Python-project/PDF-to-Markdown/run_mineru.py))

為了提高效率，腳本已實現以下自動化邏輯：

- **批量處理能力**：支援輸入單一檔案路徑或整個資料夾路徑。
- **路徑自動優化**：
    - 自動偵測並移動 MinerU 產出的 `auto` 子資料夾內容至根目錄。
    - 將 `images` 資料夾重新命名為 `assets` 以符合資產管理規範。
- **環境變數封裝**：
    - 自動設置 `MINERU_MODEL_SOURCE=local` 強制讀取本地模型。
    - 自動設置 `HF_HOME` 與 `MODELSCOPE_CACHE` 至項目 `.cache` 目錄，避免權限錯誤。
    - 動態更新 `PATH` 以包含 NVIDIA DLLs (`cudnn`, `cublas`)，解決 GPU 調用問題。
- **產出優化**：自動刪除 `_origin.pdf` 等中間產物，保持結果清爽。

## 3. 操作指南 (快速啟動)

### 啟動環境
```powershell
conda activate PDF-to-Markdown
```

### 執行轉換任務
使用更新後的腳本進行批量轉換：
```powershell
# 語法：python run_mineru.py [輸入路徑] -o [輸出路徑]
python run_mineru.py "C:\path\to\pdfs" -o "C:\path\to\output"
```

## 4. 自我檢查清單核對

- [x] **Conda 環境**：已確認為 Python 3.10 且運行穩定。
- [x] **模型配置**：`magic-pdf.json` 指向正確，無需聯網即可運行。
- [x] **LaTeX 公式**：經測試，公式還原度高，符合標準 LaTeX 規範 ($ ... $ 與 $$ ... $$)。
- [x] **資產引用**：Markdown 中的圖片路徑已統一修改為 `assets/` 相對路徑。

## 5. 後續效率提升建議
- **硬體佔用**：MinerU 解析大型 PDF (如 200 頁以上) 時會佔用約 6-8GB 顯存，執行時建議關閉其他重型 GPU 應用。
- **日誌追蹤**：轉換進度會即時顯示在終端機中，若遇到錯誤可查閱項目根目錄的 `TROUBLESHOOTING.md`。
