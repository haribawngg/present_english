# Setup laptop để thuyết trình

Repo đã có dữ liệu SMS và **bốn mô hình đã huấn luyện**. Không cần train lại. Lần setup đầu tiên cần Internet; hãy hoàn thành trước buổi thuyết trình.

## 1. Chuẩn bị

- Git.
- **Python 3.13, 64-bit** để khớp môi trường đã kiểm thử với model hiện tại.
- **Node.js 24 LTS** (hoặc Node.js 22.12+), có npm.
- Windows 64-bit là môi trường đã kiểm thử. Nếu TensorFlow báo thiếu DLL, kiểm tra Microsoft Visual C++ Redistributable x64.

Kiểm tra trong PowerShell:

```powershell
git --version
py -3.13 --version
node --version
npm --version
```

## 2. Clone và cài đặt một lần

```powershell
git clone https://github.com/haribawngg/present_english.git
cd present_english

py -3.13 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements-tested.txt
.\.venv\Scripts\python -m spam_lab.preprocessing

npm install
npm run dev
```

Không cần activate `.venv`: launcher tự tìm Python ở đó. Không cần thay đổi ExecutionPolicy của PowerShell. `npm install` tự cài dependency trong thư mục `frontend`.

Chờ model nạp xong. Terminal in dòng `Local: http://127.0.0.1:5173/` và tự mở trình duyệt. Nếu cổng đang bận, Vite chọn 5174, 5175… Hãy dùng **đúng link Local** được in ra.

## 3. Mỗi lần mở demo

```powershell
cd DUONG_DAN_DEN_REPO\present_english
npm run dev
```

Nhấn **Ctrl+C** để dừng frontend và backend cùng lúc. Nếu trình duyệt không tự mở, copy link `Local:` vào thanh địa chỉ. Có thể dùng `npm run dev -- --no-open` để chủ động mở link.

Sau khi cài đặt thành công, inference và giao diện chạy local, không cần dịch vụ AI hay API key. Font Google có thể chuyển sang font hệ thống khi mất mạng.

## 4. Kiểm tra trước khi thuyết trình

1. Giao diện hiện **Flask API đã kết nối** và **4 mô hình**.
2. Chọn **Tin quảng cáo → Naive Bayes → Phân loại tin nhắn**: xem nhãn spam và phần giải thích token.
3. Chọn **Tin thông thường → TF-IDF + Dense → Phân loại tin nhắn**: kiểm tra model neural.
4. Mở **Đánh giá mô hình**: bảng metrics, đổi model trong confusion matrix, tải metrics JSON.
5. Giữ máy đang sạc và thử mở lại sau khi ngắt Internet.

Nếu muốn chạy kiểm thử tự động:

```powershell
npm run build
.\.venv\Scripts\python -m pytest -q
```

Build trước test vì test tích hợp kiểm tra cả `frontend/dist`. Build không bắt buộc khi dùng `npm run dev`.

## 5. Xử lý lỗi nhanh

| Lỗi | Cách xử lý |
|---|---|
| `npm` hoặc `py` không nhận diện | Cài Node/Python, mở lại terminal |
| `Python environment missing` | Chạy lại bước tạo `.venv` trong đúng thư mục repo |
| Thiếu thư viện Python | Dùng `.\.venv\Scripts\python -m pip install -r requirements-tested.txt` |
| Thiếu WordNet/POS tagger | Chạy `.\.venv\Scripts\python -m spam_lab.preprocessing` khi có mạng |
| Thiếu dependency frontend | `npm install` tại thư mục gốc |
| TensorFlow cảnh báo không có GPU trên Windows | Demo chạy CPU, đây không phải lỗi khởi động |
| Model unavailable | Kiểm tra `artifacts_neural_verified/bundle.joblib`, `dense.keras`, `metrics.json` và log terminal |
| Python khác phiên bản hoặc không tìm được wheel | Dùng Python 3.13 x64 như hướng dẫn; tránh đổi phiên bản sklearn/joblib khi dùng model đã lưu |

Nếu cần trình bày gấp và TensorFlow chưa cài được, vẫn có thể dùng ba baseline:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m spam_lab.preprocessing
$env:MODEL_DIR="artifacts"
npm run dev
```

Để quay lại bốn model ở lần sau: `Remove-Item Env:MODEL_DIR -ErrorAction SilentlyContinue`, cài đầy đủ `requirements-tested.txt`, chạy lại `npm run dev`.

## Những gì có và không có trên GitHub

**Có:** source frontend/backend, dataset, notebook, hai bộ artifacts hoàn chỉnh (baseline và bốn model), lockfile, requirements và tài liệu.

**Không có:** môi trường ảo `.venv`, `node_modules`, NLTK resources đã tải, cache, log, file bí mật `.env`, frontend build và ZIP. Chúng được tạo lại khi setup/build. Các model dưới 4 MB/file nên không cần Git LFS.

Hướng dẫn sâu hơn: [DEMO.md](DEMO.md), [ARCHITECTURE.md](ARCHITECTURE.md), [README.md](README.md).
