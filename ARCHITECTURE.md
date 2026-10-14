# Cấu trúc và hướng dẫn debug

Frontend vẫn là TypeScript thuần. Component là module xuất hàm template/render và callback; không cần React để sử dụng hay sửa giao diện.

```text
frontend/src/
  main.ts                         # Chỉ khởi động ứng dụng và import CSS
  app.ts                          # Điều phối request, state và callback
  pages/
    ClassificationPage.ts         # Ghép trang phân loại
    EvaluationPage.ts             # Khung trang đánh giá
  components/
    layout/
      AppLayout.ts                # Khung ứng dụng
      Sidebar.ts                  # Menu trái
      Navigation.ts               # Chuyển trang
      Feedback.ts                 # Lỗi và trạng thái kết nối
    classifier/
      MessageComposer.ts          # Input, mẫu tin, xóa, nút submit
      ModelSelector.ts            # Chọn mô hình
      PredictionResult.ts         # Nhãn, xác suất, token, giải thích NB
      Pipeline.ts                 # Minh họa quy trình xử lý
    dashboard/StatsCards.ts        # Thẻ thống kê dataset
    evaluation/
      MetricsTable.ts             # Bảng so sánh
      ConfusionMatrix.ts          # Ma trận nhầm lẫn
  services/api.ts                  # Fetch JSON, timeout, lỗi HTTP
  state/appState.ts                # State riêng cho mỗi lần mount app
  types/index.ts                   # Kiểu model, prediction và report
  constants/models.ts             # Tên và mô tả model
  utils/                          # DOM, escape HTML, định dạng, download
  styles/                         # CSS chia file, giữ thứ tự cascade
    glass-theme.css               # Palette pastel, kính mờ, hover và responsive của theme

backend/
  main.py                         # Giữ tương thích import create_app cũ
  app.py                          # Flask application factory
  config.py                       # Đường dẫn và giới hạn payload
  middleware.py                   # JSON errors và response headers
  validation.py                   # Kiểm tra request trước inference
  routes/
    api.py                        # Blueprint API và aliases
    frontend.py                   # Phục vụ index và assets
  services/prediction.py           # Nạp model và khóa inference giữa thread

spam_lab/                         # Thuật toán, preprocessing, train, inference
tests/test_lab.py                 # Kiểm thử thuật toán và tích hợp API
run_demo.py                       # Entry point chạy Waitress
package.json                      # npm run dev / npm run build từ thư mục gốc
scripts/dev.mjs                   # Quản lý Flask + Vite, mở browser, dừng server
backend/devserver.py              # Backend dev trên cổng trống tự động
```

## Luồng xử lý

`MessageComposer → callback app.ts → services/api.ts → Flask routes/api.py → validation.py → PredictionService → spam_lab/inference.py → PredictionResult`.

Component không tự fetch; `app.ts` quản lý request và truyền dữ liệu xuống. Mỗi lần đổi tin nhắn/model tăng `revision`, bỏ qua response cũ nếu nội dung đã thay đổi trong lúc chờ. Không có state mutable ở module scope.

## Debug theo triệu chứng

| Triệu chứng | Nơi kiểm tra |
|---|---|
| Không gửi request hoặc nút bị disabled | `MessageComposer.ts`, `app.ts` |
| Request lỗi hoặc timeout | Network `/api/predict`, `services/api.ts` |
| Response 422 | `backend/validation.py` |
| Response 503 | Log khởi động, `MODEL_DIR`, tài nguyên NLTK, `services/prediction.py` |
| JSON đúng nhưng UI sai | Component tương ứng, `types/index.ts` |
| Model trả kết quả không như mong đợi | `spam_lab/preprocessing.py`, `spam_lab/inference.py` |
| Lỗi giao diện ở màn hình nhỏ | `styles/responsive.css` |
| Token NB/xác suất sai | `PredictionResult.ts`, `spam_lab/naive_bayes.py` |

Chạy frontend bằng `npm --prefix frontend run dev` để dùng hot reload. Backend dùng `python -m flask --app backend.app:create_app run --debug --port 8000` khi phát triển local (mặc định ba model trong `artifacts`; đặt `MODEL_DIR` nếu cần Dense). Không bật debug Flask khi triển khai công khai.

Vite build bật source map: DevTools → Sources hiển thị file TypeScript gốc để đặt breakpoint. Các file `.map` chỉ chứa source của demo, không có khóa bí mật. `styles/index.css` là nơi quyết định thứ tự import; không đổi thứ tự tùy ý vì có selector dùng chung giữa component.

Theme Glassmorphism được import cuối ở `styles/glass-theme.css`; chỉnh các biến `--ink`, `--muted-ink`, `--glass`, `--glass-edge`, `--glass-shadow` để thay màu/độ mờ. Nền pastel trang trí nằm trong `components/layout/AmbientBackground.ts`, có `aria-hidden` và không chặn click. Theme có fallback khi browser không hỗ trợ backdrop-filter và giảm chuyển động theo `prefers-reduced-motion`.

## Sau khi sửa

```powershell
npm --prefix frontend run build
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python tools/package_project.py
```

Lệnh chạy demo khuyến nghị: `npm run dev` tại thư mục gốc. Tự khởi động Flask/Vite và mở http://127.0.0.1:5173/. Khởi động lại lệnh sau khi sửa Python; Vite tự cập nhật khi sửa giao diện. `run_demo.py` vẫn dùng được cho bản build static.
