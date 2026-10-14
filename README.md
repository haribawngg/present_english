# SMS Spam Lab + TypeScript Frontend + Flask API

**Cài trên laptop để thuyết trình:** làm theo [SETUP_LAPTOP.md](SETUP_LAPTOP.md). Repo đã chứa model được huấn luyện; chỉ cần cài môi trường một lần, sau đó chạy `npm run dev`.

**Demo hoàn chỉnh:** xem [DEMO.md](DEMO.md). Chạy `npm run dev` tại thư mục gốc; Flask và Vite tự khởi động, link http://127.0.0.1:5173/ tự mở trên trình duyệt. Lần đầu trên máy mới chạy `npm install` và thiết lập Python theo DEMO.md. Giao diện TypeScript đã build sẵn; backend hiện dùng Flask + Waitress, thay thế FastAPI trước đây. Các hướng dẫn bên dưới tập trung vào huấn luyện bài lab.

**Cấu trúc source và debug:** xem [ARCHITECTURE.md](ARCHITECTURE.md). Frontend chia component; backend tách routes, validation và prediction service.

Mã nguồn thực hiện các mục 1–8 và phần 9* tùy chọn trong đề bài. Dữ liệu đã sao chép từ `smsspamcollection-1.tsv` bạn cung cấp vào `data/smsspamcollection.tsv`. Nhãn đúng là **ham** (tin thường), không phải `harm`. Dataset tiếng Anh; demo nên nhập SMS tiếng Anh.

## Chạy nhanh trên Windows / PowerShell

Chạy từ thư mục gốc dự án. Khuyến nghị Python 3.11 hoặc 3.12 nếu dùng TensorFlow; phần cơ bản cũng được kiểm thử với Python 3.13.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m spam_lab.preprocessing
.\.venv\Scripts\python -m spam_lab.train --data data/smsspamcollection.tsv
.\.venv\Scripts\python run_demo.py --models artifacts
```

Nếu đã có `artifacts/bundle.joblib` được cung cấp trong gói, có thể bỏ bước train khi dùng đúng phiên bản thư viện ở `requirements-tested.txt`. Nếu cài phiên bản khác, train lại bằng `--output artifacts_new` rồi đặt `$env:MODEL_DIR="artifacts_new"` trước khi chạy backend. Lệnh train từ chối ghi đè thư mục đã có model.

Nếu tạo venv lỗi tại `ensurepip`, dùng `python -m pip --python .venv install -r requirements-dev.txt` với pip của Python hệ thống. Trên Linux/Colab dùng `python` sau khi kích hoạt môi trường bằng `source .venv/bin/activate`.

Mở http://127.0.0.1:8000 để sử dụng frontend. Xem DEMO.md để chạy đầy đủ bốn model. Backend tải model một lần khi khởi động, không train trong mỗi request. Sau khi thay model cần khởi động lại backend.

## Các bước của bài lab

| Mục | Hiện thực |
|---|---|
| 1 | `load_data` dùng pandas đọc TSV, nhận file có header hoặc hai cột không header; bỏ cột length/punct |
| 2 | NLTK `RegexpTokenizer`, Unicode NFKC, lowercase, URL/email/số thành token; WordNet lemmatization có POS rồi Porter stemming |
| 3 | Chia stratified train/test 80/20, seed=42 |
| 4 | Vocabulary chỉ học từ train; các từ ngoài vocabulary được bỏ qua |
| 5 | `CounterNaiveBayes`: đếm token theo lớp bằng Counter, prior, Laplace smoothing, log probability |
| 6 | Confusion matrix, accuracy, precision, recall và F1; spam là positive class |
| 7 | CountVectorizer + LogisticRegression |
| 8 | TfidfVectorizer + LogisticRegression |
| 9* | TfidfVectorizer + Dense(64) → Dropout(0.3) → Dense(32) → Dense(1, sigmoid) |

Mặc định `--mode both`: lemmatize trước rồi stem để minh họa cả hai kỹ thuật theo đề. Có thể dùng `--mode lemma` hoặc `--mode stem` để làm thí nghiệm riêng. Không bỏ stopwords để giữ ngữ cảnh SMS. Dấu câu bị loại. Lemmatization dùng từ điển và POS tagger huấn luyện sẵn; không học từ test.

Chuẩn hóa là phép biến đổi không học tham số. Trước chia dữ liệu, bỏ bản ghi rỗng, nhóm có cùng nội dung chuẩn hóa nhưng nhãn mâu thuẫn, và tin trùng chuẩn hóa. Cách này tránh leakage; số mẫu và kết quả có thể khác bài chữa chia trực tiếp dữ liệu gốc. Vectorizer và IDF chỉ fit trên train. Cả ba mô hình cơ bản dùng cùng tập train và test, unigram và toàn bộ vocab train. Không cân bằng lớp bằng oversampling. Không chọn siêu tham số hoặc model mặc định dựa trên test; API mặc định NB theo mục tiêu bài lab.

NB tính:

```text
P(c) = số tin lớp c / số tin train
P(w|c) = (Counter_c[w] + 1) / (tổng token lớp c + |V_train|)
score(c, x) = log P(c) + Σ count(w,x) * log P(w|c), w thuộc V_train
prediction = argmax score(c,x)
```

Softmax trên log score trả xác suất có tổng bằng 1; các xác suất này chưa được hiệu chỉnh, không phải cam kết về độ chắc chắn. Tin không có token trong vocab sẽ dùng baseline của model và trả `warning`. `nb_example.json` minh họa tính điểm của một tin test, `nb_vocabulary.csv` chứa số lần xuất hiện từ theo lớp.

## Dense Network (mục 9*)

```powershell
.\.venv\Scripts\python -m pip install -r requirements-neural.txt
.\.venv\Scripts\python -m spam_lab.train --neural --epochs 15 --output artifacts_neural
$env:MODEL_DIR="artifacts_neural"
.\.venv\Scripts\python run_demo.py --models artifacts_neural
```

TF-IDF giới hạn 5.000 features, float32 để giới hạn RAM khi chuyển dense. Tách 15% phần train thành validation có stratify; vectorizer neural chỉ fit trên phần train nhỏ hơn này. EarlyStopping theo validation loss, patience=3, lấy lại trọng số tốt nhất; test chỉ dùng đánh giá cuối cùng. Vì neural giữ riêng validation, số mẫu dùng cập nhật trọng số ít hơn ba baseline; cần nêu điều này khi so sánh. Seed cố định nhưng GPU/phần cứng có thể làm kết quả hơi khác. TensorFlow là dependency tùy chọn, không cần để chạy ba mô hình cơ bản.

## Kết quả đầu ra

Đã chạy thực tế trên file 5.572 tin: sau làm sạch còn 5.094 tin (4.075 train, 1.019 test; test gồm 900 ham và 119 spam). Bỏ 2 tin không còn token và 476 tin trùng chuẩn hóa.

| Model | Accuracy | Precision spam | Recall spam | F1 spam |
|---|---:|---:|---:|---:|
| NB Counter | 98,53% | 96,43% | 90,76% | 93,51% |
| Count + LR | 97,84% | 92,92% | 88,24% | 90,52% |
| TF-IDF + LR | 97,45% | 95,15% | 82,35% | 88,29% |
| TF-IDF + Dense | 98,43% | 98,13% | 88,24% | 92,92% |

NB có F1 và recall cao nhất trong split này; Dense có precision cao nhất. Đây là kết quả một split, không đủ kết luận mô hình luôn tốt nhất trên dữ liệu khác. Model cơ bản đã lưu ở `artifacts`; đầy đủ bốn model ở `artifacts_neural_verified`. Dùng `$env:MODEL_DIR="artifacts_neural_verified"` để demo cả bốn. Dense đã chạy TensorFlow 2.21.0 CPU và EarlyStopping ở epoch 6, khôi phục trọng số epoch 3.

Trong thư mục `--output`:

- `bundle.joblib`: preprocessing và các model; `dense.keras` nếu bật neural.
- `metrics.json`: metrics, báo cáo theo từng lớp, metadata, phiên bản, hash dữ liệu, history neural.
- `comparison.csv`: bảng so sánh bốn chỉ số.
- `confusion_matrices.png`: hàng là nhãn thật, cột là nhãn dự đoán; thứ tự `[ham, spam]`, tức `[[TN, FP], [FN, TP]]`.
- `test_predictions.csv`: tin test, nhãn thật và từng dự đoán để xem lỗi.
- `clean_dataset.csv`, `split.json`: dữ liệu sau làm sạch và chỉ số split để kiểm chứng.
- `nb_vocabulary.csv`, `nb_example.json`: tài liệu giải thích NB.

Accuracy = (TP+TN)/N; precision spam = TP/(TP+FP); recall spam = TP/(TP+FN). Khi mẫu spam ít, cần nhìn cả precision/recall/F1 và số spam bỏ sót, không chỉ accuracy.

## API cho frontend

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/health` | 200 khi model sẵn sàng; 503 nếu chưa tải được |
| GET | `/models` | Tên các model khả dụng và model mặc định |
| GET | `/metrics` | Kết quả đánh giá test và metadata |
| POST | `/predict` | Dự đoán 1–100 tin, tối đa 5.000 ký tự/tin |

Request:

```json
{"messages":["Congratulations! Win free cash now!","See you tonight"],"model":"nb","explain":true}
```

Response có `predictions` là danh sách: `message`, `normalized`, `model`, `label`, `confidence`, `probabilities: {ham, spam}`, `known_token_count`, `warning`. Với NB và `explain=true`, có thêm `explanation` gồm log prior, log score, đóng góp log odds từng token và từ ngoài vocab. Đóng góp dương nghiêng về spam. Với LR/neural không trả phần giải thích NB.

```javascript
const response = await fetch('http://127.0.0.1:8000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ messages: [message], model: 'nb', explain: true })
});
const data = await response.json();
if (!response.ok) throw new Error(JSON.stringify(data.detail));
console.log(data.predictions[0]);
```

400: tên model không hợp lệ/chưa huấn luyện; 422: input sai; 503: model chưa sẵn sàng. Frontend build và Flask dùng cùng origin; Vite dev proxy /api đến Flask. API dùng cho demo local; không có đăng nhập hay rate limiting. Chỉ tải artifact đáng tin do chính bạn tạo vì joblib sử dụng pickle.

Frontend đã hiện thực: ô nhập SMS, chọn model, nút phân loại, nhãn ham/spam, xác suất, token đã chuẩn hóa, bảng so sánh metrics, confusion matrix và bảng đóng góp từ của NB. Source nằm trong `frontend/src`.

## Colab và báo cáo

Mở `notebooks/sms_spam_lab.ipynb` bằng Upload notebook trên https://colab.research.google.com/ . Notebook yêu cầu upload gói `sms_spam_lab.zip`, giải nén source và dataset, cài dependencies rồi chạy lab. Có cell tùy chọn cho neural, hiển thị kết quả và tải artifacts. Để lấy đường link nộp bài, lưu bản sao notebook vào Google Drive của bạn, chạy các cell và dùng Share. Dự án chưa tạo một đường link Colab công khai trong tài khoản của bạn.

Phạm vi bàn giao hiện tại là mã Python, backend và notebook; chưa tạo PDF báo cáo. Có thể dùng bảng CSV, hình confusion matrix và phần công thức trong README làm nội dung báo cáo. Hai link mẫu Canvas/Colab trong đề không truy cập được ở phiên làm việc này; mã bám theo yêu cầu được chép trong đề, không khẳng định sao chép bài chữa.

## Kiểm thử

```powershell
.\.venv\Scripts\python -m pytest -q
```

Chạy train ra `artifacts` trước để kiểm thử tích hợp không bị skip. Kiểm tra công thức NB bằng ví dụ tính tay và đối chiếu sklearn MultinomialNB, ổn định số với tin dài, không leakage, vocabulary train, serialization/API, input lỗi và trạng thái chưa có model.

Tài liệu tham khảo: [scikit-learn text features](https://scikit-learn.org/stable/modules/feature_extraction.html), [NLTK WordNetLemmatizer](https://www.nltk.org/api/nltk.stem.wordnet.html), [Flask](https://flask.palletsprojects.com/en/stable/), [Keras EarlyStopping](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping).


