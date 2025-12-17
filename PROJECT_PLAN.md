# Kế Hoạch Đồ Án Hệ Thống Gợi ý

## Chiến lược dữ liệu

- **Nguồn**: MovieLens Latest Small (https://files.grouplens.org/datasets/movielens/ml-latest-small.zip)
- **Quy mô**: ~9,7K bộ phim, 100K lượt chấm (đáp ứng yêu cầu >2K mục).
- **Thuộc tính mục (>=5)**:
  1. Tiêu đề
  2. Thể loại (đa nhãn)
  3. Năm phát hành (tách từ tiêu đề)
  4. Điểm trung bình (tổng hợp)
  5. Số lượt đánh giá / độ phổ biến
  6. Phương sai điểm (độ ổn định)
  7. Vector TF-IDF của tag (đặc trưng văn bản)

## Tổng quan pipeline

1. **Thu thập dữ liệu** (`scripts/download_movielens.py`)
   - Tải và giải nén MovieLens vào `data/raw/`.
2. **Chuẩn bị dữ liệu** (`src/data_ingestion.py`, `src/data_cleaning.py`, `src/features.py`)
   - Ghép bảng ratings, movies, tags.
   - Xử lý giá trị thiếu, loại trùng, phát hiện & winsorize outlier ở số lượt rating.
   - Vector hóa tag + thể loại bằng TF-IDF.
3. **Phân tích khám phá** (`src/visualization.py`, `notebooks/recommendation_workflow.ipynb`)
   - Phân bố rating, tần suất thể loại, top phim theo lượt đánh giá, heatmap.
4. **Mô hình hóa** (`src/recommender.py`)
   - **Content-based**: độ tương đồng cosine trên vector TF-IDF.
   - **Collaborative**: phân rã TruncatedSVD trên ma trận user–item.
   - **Hybrid**: tổ hợp có trọng số của hai điểm số.
5. **Đánh giá** (`src/evaluation.py`)
   - RMSE & MAE (dự báo rating).
   - Precision@K & Recall@K với danh sách gợi ý top-N cho mỗi user.
6. **Giao diện** (`app.py`)
   - Streamlit UI với chọn user, đổi mô hình, lọc thể loại và bảng kết quả.
7. **Báo cáo** (`reports/final_report.md`, các cell tường thuật trong notebook)
   - Báo cáo markdown 8–12 trang tóm tắt phương pháp, kết quả, hướng phát triển.

## Sản phẩm bàn giao

- Notebook tái lập toàn bộ yêu cầu đồ án.
- Gói Python dạng module cho pipeline và mô hình.
- Giao diện Streamlit hướng đến người dùng cuối.
- Báo cáo cuối (markdown) sẵn sàng chuyển sang PDF/Docx.
- README với hướng dẫn cài đặt & chạy.
