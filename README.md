# Hệ thống Tóm tắt Văn bản (Text Summarization)

Xây dựng từ đầu, hỗ trợ **Tiếng Việt & Tiếng Anh**, gồm 2 phương pháp:
- **Extractive**: TextRank (baseline) + BiLSTM + Attention
- **Abstractive**: Seq2Seq LSTM + Pointer-Generator Network

Phiên bản mới bao gồm bộ ba service: **React + Vite** frontend, **Express** backend và **Flask** Python AI core.

---

## Cấu trúc thư mục

```
summarization/
├── data/                        # Dữ liệu
│   ├── sample_vi.json           # Mẫu tiếng Việt
│   ├── sample_en.json           # Mẫu tiếng Anh
│   ├── processed_vi.json        # Đã tiền xử lý
│   └── processed_en.json
├── models/                      # Model đã train
│   ├── bilstm_vi.pt
│   ├── bilstm_en.pt
│   ├── seq2seq_vi.pt
│   └── seq2seq_en.pt
├── outputs/                     # Kết quả đánh giá
│   ├── evaluation_vi.json
│   └── evaluation_en.json
├── generate_sample_data.py      # Tạo dữ liệu mẫu
├── preprocessing.py             # Tiền xử lý văn bản
├── textrank.py                  # TextRank (không cần train)
├── bilstm_extractive.py         # BiLSTM Extractive
├── seq2seq_abstractive.py       # Seq2Seq + Pointer-Generator
├── evaluate.py                  # Đánh giá ROUGE
└── run_pipeline.py              # Chạy toàn bộ pipeline
```

---

## Cài đặt

```bash
pip install torch scikit-learn rouge-score numpy
# Nếu có GPU NVIDIA (khuyến nghị):
pip install torch --index-url https://download.pytorch.org/whl/cu121
# Tiếng Việt thật (crawl data):
pip install underthesea requests beautifulsoup4
```

---

## Cách chạy
python ai_core/server.py
cd backend && npm install && npm run dev
cd frontend && npm install && npm run dev
### Chạy phiên bản Web Edition
```bash
# 1) Chạy Flask AI Core
cd ai_core
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

Mở terminal mới và chạy backend:
```bash
cd "c:\Users\nguye\OneDrive\Máy tính\summarization_project (1)\summarization\ai_core" ; python main.py
cd backend
npm install
npm run dev
```

Mở terminal mới và chạy frontend:
```bash
cd frontend
npm install
npm run dev
```

Sau khi cả 3 service đã khởi động, mở trình duyệt tại:
```bash
http://localhost:5173
```

> Giao diện hiện đã hỗ trợ upload file PDF / DOCX / TXT để tự động trích xuất văn bản và tóm tắt.

### Chạy toàn bộ pipeline (khuyến nghị)
```bash
cd summarization/
python run_pipeline.py vi     # chỉ tiếng Việt (mặc định dùng dataset thật nếu có)
python run_pipeline.py en     # chỉ tiếng Anh (dùng sample data)
python run_pipeline.py both   # cả hai
```

### Chạy từng bước riêng lẻ

```bash
# 1. Tạo data mẫu
python generate_sample_data.py

# 2. Tiền xử lý
python preprocessing.py

# 3. TextRank demo (không cần train)
python textrank.py data/processed_vi.json

# 4. Train + demo BiLSTM
python bilstm_extractive.py train vi
python bilstm_extractive.py predict vi

# 5. Train + demo Seq2Seq
python seq2seq_abstractive.py train vi
python seq2seq_abstractive.py predict vi

# 6. Đánh giá tất cả
python evaluate.py vi
```

---

## Kết quả kỳ vọng (ROUGE F1)

| Model | ROUGE-1 | ROUGE-2 | ROUGE-L |
|---|---|---|---|
| TextRank (baseline) | ~0.35–0.42 | ~0.15–0.20 | ~0.30–0.38 |
| BiLSTM Extractive | ~0.42–0.50 | ~0.20–0.28 | ~0.38–0.45 |
| Seq2Seq + PG | ~0.25–0.35 | ~0.08–0.15 | ~0.22–0.32 |

> Seq2Seq ROUGE thường thấp hơn extractive vì sinh câu mới — ROUGE đo overlap từ,
> không phản ánh đúng chất lượng ngữ nghĩa. Cần BERTScore để đánh giá chính xác hơn.

---

## Dùng data thật (tiếng Việt)

Thay `generate_sample_data.py` bằng crawler thật:

```python
# Crawl VnExpress
import requests
from bs4 import BeautifulSoup

def crawl_vnexpress(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    title = soup.find("h1", class_="title-detail").text.strip()
    description = soup.find("p", class_="description").text.strip()
    content = " ".join(p.text for p in soup.find_all("p", class_="Normal"))
    return {"article": content, "summary": description, "lang": "vi"}
```

---

## Nâng cấp tiếp theo

- **Tiếng Việt tốt hơn**: dùng `underthesea` để tokenize đúng từ ghép
- **Embedding tốt hơn**: train Word2Vec/FastText trên corpus lớn
- **Abstractive mạnh hơn**: fine-tune mBERT / PhoBERT + VinAI/BARTpho
- **Demo UI**: `streamlit run app.py`

---

## Kiến trúc model

### BiLSTM Extractive
```
Câu → TF-IDF vector → BiLSTM (2 lớp) → Attention → Score [0,1] → Top-k câu
```

### Seq2Seq + Pointer-Generator
```
Từ → Embedding → Encoder BiLSTM → Decoder LSTM + Bahdanau Attention
                                 → p_gen gate → vocab dist + copy dist → từ
```
