# Hệ thống Gợi ý MovieLens – Đồ án Cuối Kỳ

Giải pháp gợi ý end-to-end đáp ứng toàn bộ tiêu chí của rubric môn học:

- ✅ Thu thập dữ liệu (MovieLens Latest Small, >2.000 phim)
- ✅ Làm sạch & tiền xử lý (giá trị thiếu, trùng lặp, outlier, TF-IDF)
- ✅ Phân tích khám phá & trực quan (phân bố rating, tần suất thể loại, top phim, heatmap)
- ✅ Nhiều chiến lược gợi ý (content-based, collaborative SVD, hybrid)
- ✅ Đánh giá mô hình (RMSE, MAE, Precision@K, Recall@K)
- ✅ Giao diện người dùng bằng Streamlit
- ✅ Notebook tường thuật + báo cáo 8–12 trang

## Cấu trúc Repository

```
project-root/
├── app.py                     # UI Streamlit
├── notebooks/
│   └── recommendation_workflow.ipynb
├── reports/
│   └── final_report.md
├── scripts/
│   ├── download_movielens.py  # Tải & giải nén dữ liệu
│   └── train_models.py        # Chạy toàn pipeline và lưu artifact
├── src/
│   ├── data_ingestion.py      # Tiện ích tải/đọc dữ liệu
│   ├── data_cleaning.py
│   ├── evaluation.py
│   ├── features.py
│   ├── recommender.py
│   ├── utils.py
│   └── visualization.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
│   └── artifacts/
├── requirements.txt
└── PROJECT_PLAN.md
```

## Khởi động nhanh

1. **Cài đặt phụ thuộc**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Tải dữ liệu**
   ```powershell
   python scripts/download_movielens.py --output data/raw
   ```
3. **Huấn luyện & sinh artifact**
   ```powershell
   python scripts/train_models.py \
       --raw_dir data/raw \
       --processed_dir data/processed \
       --artifact_dir models/artifacts
   ```
4. **Khám phá notebook**
   Mở `notebooks/recommendation_workflow.ipynb` trong VS Code/Jupyter và chạy tuần tự các cell.

5. **Chạy giao diện Streamlit**
   ```powershell
   streamlit run app.py
   ```

## Cấu hình MySQL (tuỳ chọn)

- Sao chép tệp mẫu: `copy .env.example .env` rồi cập nhật thông tin truy cập MySQL.
- Hoặc đặt trực tiếp biến môi trường `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` trước khi chạy app.
- Khi cấu hình đầy đủ, Streamlit sẽ cho phép lưu lịch sử tương tác xuống bảng `user_interactions` trong MySQL.

## Chức năng trong Streamlit

- Chọn bất kỳ `userId` có trong bộ ratings.
- Chuyển đổi giữa content-based, collaborative (SVD) hoặc hybrid.
- Lọc theo thể loại và số lượng gợi ý.

## Thước đo đánh giá

- `evaluation.rmse`, `evaluation.mae` cho bài toán dự báo rating.
- `evaluation.precision_at_k`, `evaluation.recall_at_k` cho chất lượng xếp hạng.

## Báo cáo

Bản tường thuật 8–12 trang nằm ở `reports/final_report.md` (sẵn sàng xuất PDF/DOCX).

## Hướng mở rộng

- Thay bằng bản MovieLens lớn hơn (1M/20M).
- Thêm tín hiệu ngữ cảnh (thời gian, mức độ gần đây).
- Triển khai app Streamlit lên cloud (Streamlit Community Cloud / Azure App Service).
