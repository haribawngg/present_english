# Demo SMS Lab: TypeScript + Flask

Frontend TypeScript thuần, Vite build; Flask API dùng model đã huấn luyện, Waitress phục vụ cả UI và API trên một địa chỉ. Mọi kết quả lấy từ backend thật, không dùng dự đoán giả.

## Chạy ngay trong workspace hiện tại

```powershell
npm run dev
```

Chạy tại thư mục gốc có `package.json`. Lệnh tự tải bốn model, khởi động Flask + Vite, in link **http://127.0.0.1:5173/** và mở trình duyệt mặc định. Nhấn Ctrl+C để dừng cả hai server. TensorFlow có thể mất vài giây để nạp lần đầu. Không cần chạy file Python riêng hoặc build frontend trước.

Nếu không muốn tự mở trình duyệt: `npm run dev -- --no-open`. Nếu cổng 5173 đang bận, Vite tự chọn 5174, 5175… và mở đúng link mới; xem dòng `Local:` trong terminal. Không cần tắt ứng dụng khác. Flask dùng một cổng trống tự động, Vite proxy `/api` đến đúng backend đó. Có thể đặt `MODEL_DIR` để dùng bộ model khác và `PYTHON_EXECUTABLE` để chọn Python khác `.venv`.

## Chạy từ gói ZIP trên máy khác

Giải nén, mở terminal trong thư mục có `package.json`. Cần Python và Node.js 22.12+ hoặc 24. Cài đặt một lần:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-tested.txt
.\.venv\Scripts\python -m spam_lab.preprocessing
npm install
npm run dev
```

`npm install` ở thư mục gốc tự cài dependency frontend theo lockfile. Những lần sau chỉ cần `npm run dev`. Nếu muốn chạy bản build sẵn không dùng Node.js, vẫn có thể dùng `.\.venv\Scripts\python run_demo.py` và mở cổng 8000 như trước.

`requirements-tested.txt` khóa phiên bản đã kiểm thử trên Python 3.13 Windows, gồm TensorFlow. Nếu dùng phiên bản Python/hệ điều hành khác và không có wheel tương thích, cài `requirements-neural.txt` rồi train lại bằng `python -m spam_lab.train --neural --output artifacts_new`; sau đó chạy `python run_demo.py --models artifacts_new`. Ba baseline không cần TensorFlow: cài `requirements.txt`, train `--output artifacts_basic`, chạy `python run_demo.py --models artifacts_basic`.

Lần đầu cần mạng để tải thư viện và tài nguyên NLTK. Sau đó inference chạy local. Giao diện có font hệ thống dự phòng nếu không tải được Google Fonts. Không ghi nội dung SMS vào database hoặc file lịch sử. Backend phục vụ local, chưa có đăng nhập/rate limit cho triển khai công khai.

## Tính năng để báo cáo

1. **Phân loại tin nhắn**: nhập SMS tiếng Anh, dùng mẫu ham/spam, chọn một trong các model khả dụng và nhấn Phân loại.
2. Xem nhãn, xác suất từng lớp, thời gian request và văn bản đã chuẩn hóa.
3. Với NB, xem đóng góp log-odds của tối đa 8 token ảnh hưởng mạnh nhất. Dương nghiêng về spam, âm nghiêng về ham; đây không phải xác suất riêng của từ.
4. **Đánh giá mô hình**: bảng accuracy/precision/recall/F1, chọn confusion matrix và tải metrics JSON.
5. Trạng thái loading, lỗi kết nối có nút thử lại, input rỗng bị chặn, giới hạn 5.000 ký tự, cảnh báo token ngoài vocabulary. Kết quả cũ được xóa khi đổi nội dung/model để tránh hiểu nhầm.

Số liệu trên giao diện được đọc từ artifacts, không hardcode. Xác suất model chưa được hiệu chỉnh. Cùng tập test 1.019 tin; neural giữ riêng validation từ train.

## Phát triển frontend

Cần Node.js 22.12+ hoặc 24. Từ thư mục gốc:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

Hai lệnh `--prefix frontend` trên là chế độ chỉ phát triển frontend, cần Flask chạy riêng ở cổng 8000. Cách khuyến nghị là `npm run dev` ở thư mục gốc để quản lý cả hai. Vite hot reload khi sửa TypeScript/CSS; khi sửa backend Python cần Ctrl+C rồi chạy lại. Build khi muốn cập nhật bản static:

```powershell
npm --prefix frontend run build
```

Frontend đã chia component, page, service, state và styles riêng. Xem [ARCHITECTURE.md](ARCHITECTURE.md) để tra cấu trúc và vị trí đặt breakpoint. `frontend/src/main.ts` chỉ khởi động; `app.ts` điều phối; CSS nằm trong `styles/`. TypeScript bật strict, build kiểm tra kiểu trước khi bundle và xuất source map để debug. Không lưu API key hoặc bí mật ở frontend.

## Flask API

| Method | Endpoint | Kết quả |
|---|---|---|
| GET | `/api/health` | Sẵn sàng 200, chưa tải được model 503 |
| GET | `/api/models` | Danh sách model được nạp |
| GET | `/api/metrics` | Metrics và metadata của lần train |
| POST | `/api/predict` | Danh sách dự đoán |

Vẫn hỗ trợ `/health`, `/models`, `/metrics`, `/predict` cho client cũ. FastAPI/Swagger đã được thay bằng Flask; `/docs` không còn dùng.

```json
{"messages":["You won a free prize! Call now!"],"model":"nb","explain":true}
```

Response `predictions` chứa `label`, `probabilities`, `confidence`, `normalized`, `model`, `warning` và `explanation` với NB. Dữ liệu sai trả 422, model không có trả 400. Batch tối đa 100 tin, 5.000 ký tự/tin. Payload tối đa 3 MB. Các đường dẫn chưa định nghĩa trả JSON 404. Flask chỉ phục vụ frontend build và assets, không mở thư mục model cho tải tùy ý. Dự đoán được khóa giữa các thread để tránh tranh chấp state NLTK/TensorFlow.

## Kiểm thử và đóng gói

```powershell
.\.venv\Scripts\python -m pytest -q
npm --prefix frontend run build
.\.venv\Scripts\python tools/package_project.py
```

Gói `sms_spam_lab.zip` chứa source frontend/backend, frontend đã build, dataset, notebook và model đã train. Không chứa `.venv`, `node_modules`, cache hay tài nguyên NLTK tải xuống.

Đã kiểm chứng: TypeScript strict và Vite build thành công; 20 kiểm thử Python đạt, gồm API Flask, cả bốn model, kiểm tra input, static assets và giới hạn payload. Trình duyệt đã xác nhận luồng mẫu spam → NB, mẫu ham → Dense và trang bảng metrics/confusion matrix. Công cụ chụp ảnh trình duyệt bị timeout nên chưa xác minh trực quan bằng screenshot hoặc trên kích thước mobile; CSS đã có breakpoint responsive.

Tham khảo API thư viện: [Flask application factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/), [Vite](https://vite.dev/guide/).
