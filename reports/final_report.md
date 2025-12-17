# Báo Cáo Đồ Án: Hệ Thống Gợi ý MovieLens

**Môn học**: Đồ án Cuối kỳ – Recommendation Systems  
**Sinh viên**: Phạm Thành Nam & B22DCCN563  
**Thời gian**: Tháng 12/2025

---

## 1. Giới thiệu

Các nền tảng giải trí trực tuyến phụ thuộc vào cá nhân hóa để giữ chân người dùng và tăng mức độ tương tác. Đồ án này xây dựng một hệ thống gợi ý end-to-end dựa trên dữ liệu MovieLens, đáp ứng đầy đủ rubric: thu thập, làm sạch, trực quan hóa, xây dựng mô hình, đánh giá và giao diện người dùng. Ngoài yêu cầu tối thiểu, hệ thống còn có mô hình hybrid, vector TF-IDF cho metadata và ứng dụng Streamlit để tương tác.

## 2. Dữ liệu & chiến lược thu thập

- **Nguồn**: MovieLens Latest Small (https://files.grouplens.org/datasets/movielens/ml-latest-small.zip).
- **Quy mô**: 100.836 lượt chấm từ 610 người dùng trên 9.742 bộ phim (>2.000 mục theo yêu cầu).
- **Tự động hoá**: Script `scripts/download_movielens.py` tải và giải nén dữ liệu vào `data/raw/`.
- **Thuộc tính mục (>=5)**:
  1. Tiêu đề đã làm sạch
  2. Thể loại (đa nhãn)
  3. Năm phát hành
  4. Điểm trung bình
  5. Số lượt chấm (đại diện độ phổ biến)
  6. Độ lệch chuẩn điểm (độ ổn định)
  7. Vector TF-IDF từ tag (đặc trưng văn bản)

## 3. Làm sạch & chuẩn bị dữ liệu

Các bước làm sạch nằm trong `src/data_cleaning.py` và được minh hoạ trong notebook.

1. **Giá trị thiếu**: Chuỗi được điền `"unknown"`, số được điền median; timestamp chuyển về dạng datetime.
2. **Loại trùng**: Xoá các bản ghi trùng `(userId, movieId, timestamp)` để tránh đếm đôi.
3. **Xử lý ngoại lệ**: Winsorize số lượt rating của từng phim (1–99 percentile) nhằm giảm ảnh hưởng blockbuster.
4. **Vector hóa**: Gom tag theo phim, nối với tiêu đề và thể loại, sau đó TF-IDF (lọc stop-word tiếng Anh).
5. **Tổng hợp đặc trưng**: Rút trích năm phát hành, điểm trung bình, số lượt chấm, phương sai điểm cho cả mô hình lẫn biểu đồ.

Bảng master sạch được lưu ở `data/processed/master.parquet` để dễ tái lập.

## 4. Phân tích khám phá & trực quan hóa

Module `src/visualization.py` tạo biểu đồ và notebook thể hiện kết quả. Một số điểm nổi bật:

- **Phân bố rating**: Histogram + KDE cho thấy thiên lệch về điểm cao (mode ~4.0), hỗ trợ việc chuẩn hóa.
- **Tần suất thể loại**: Biểu đồ cột chỉ ra Drama, Comedy, Thriller chiếm ưu thế, dùng để điều chỉnh trọng số content-based.
- **Top phim**: Lọc theo ngưỡng số lượt chấm để tìm các phim được yêu thích ổn định.
- **Heatmap**: Mẫu ngẫu nhiên từ ma trận user–item thể hiện độ thưa (~1%), chứng minh cần collaborative filtering.

Mỗi biểu đồ tự động lưu khi truyền đường dẫn đầu ra, phục vụ báo cáo và thuyết trình.

## 5. Cách tiếp cận mô hình

### 5.1 Content-Based Filtering

- **Đặc trưng**: Vector TF-IDF trên chuỗi kết hợp tiêu đề, thể loại, tag + các thống kê số (avg rating, count, std) đã chuẩn hóa.
- **Chấm điểm**: Xây dựng hồ sơ người dùng bằng tổng trọng số các phim được đánh giá cao, sau đó xếp hạng phim chưa xem dựa vào cosine similarity.
- **Ưu điểm**: Xử lý tốt phim cold-start và dễ giải thích nhờ thuộc tính văn bản.

### 5.2 Collaborative Filtering (SVD)

- **Thư viện**: Scikit-learn `TruncatedSVD` trên ma trận user–item (không cần extension C++).
- **Huấn luyện**: Ma trận 610×9.742 với 50 nhân tố ẩn, seed cố định để tái lập.
- **Dự báo**: Tích vô hướng giữa vector người dùng và phim cho điểm cá nhân hóa.
- **Ưu điểm**: Bắt được thị hiếu ẩn và tương tác user–item, chạy gọn trong môi trường Python.

### 5.3 Hệ gợi ý Hybrid

- **Kết hợp**: Tổ hợp có trọng số (`alpha=0.55`) giữa điểm content và collaborative.
- **Động lực**: Tăng độ ổn định cho phim cold-start (dựa vào content) và kho phim lớn (SVD bao phủ).

Toàn bộ mô hình được huấn luyện qua `scripts/train_models.py`, kết quả lưu tại `models/artifacts/`.

## 6. Đánh giá

Việc đánh giá được thực hiện trong notebook và `src/evaluation.py`.

| Metric       | Mô tả                                                    | Kết quả (ví dụ split) |
| ------------ | -------------------------------------------------------- | --------------------- |
| RMSE         | Sai số bình phương trung bình căn (SVD vs. ground truth) | ~0.89                 |
| MAE          | Sai số tuyệt đối trung bình                              | ~0.70                 |
| Precision@10 | Số phim đúng / 10 gợi ý                                  | ~0.31                 |
| Recall@10    | Số phim đúng thu hồi / tổng phim đúng                    | ~0.22                 |

Quy trình:

1. **Hold-out split**: Chia 80/20 train-test, bảo toàn phân bố người dùng.
2. **Sai số dự báo**: Tính RMSE/MAE trên tập test với dự báo SVD.
3. **Top-N**: Với từng user, các phim giữ lại làm ground truth; danh sách gợi ý dùng để tính Precision@K và Recall@K.

Diễn giải: RMSE/MAE tương đồng baseline MovieLens cho SVD. Precision/Recall cho thấy khoảng 1/3 gợi ý trong top 10 là phù hợp, mở ra dư địa cải thiện bằng tín hiệu ngữ cảnh.

## 7. Giao diện người dùng

Ứng dụng Streamlit (`app.py`) đáp ứng yêu cầu UI:

- Sidebar: chọn user, đổi thuật toán (content/collab/hybrid), số lượng gợi ý, lọc thể loại.
- Khu vực chính: bảng tương tác với model score, thể loại, điểm trung bình, độ phổ biến.
- Bộ nhớ đệm giúp tải artifact một lần nhưng phản hồi nhanh.

## 8. Tái lập & triển khai

- **Môi trường**: `requirements.txt` liệt kê phụ thuộc chạy tốt với Python 3.11.
- **Tự động hóa**: Script shell xử lý tải dữ liệu và huấn luyện; notebook ghi lại từng bước phục vụ chấm.
- **Quản lý phiên bản**: Kiến trúc module trong `src/` giúp mở rộng (embeddings, implicit feedback...).
- **Triển khai**: Có thể public lên Streamlit Community Cloud hoặc đóng gói Docker cho Azure App Service.

## 9. Thách thức & cách khắc phục

1. **Tag thưa thớt**: Nhiều phim thiếu tag. Giải pháp: fallback sang thể loại & từ khóa tiêu đề, thêm prior dựa trên rating cho cold-start.
2. **Thiên lệch đánh giá**: Phim nổi tiếng chiếm ưu thế trong metric. Giải pháp: winsorize số lượt chấm và chia hold-out phân tầng để phim niche vẫn xuất hiện.
3. **Dung lượng bộ nhớ**: Ma trận TF-IDF lớn. Giải pháp: giới hạn vocab với `min_df=2` và chỉ dùng mảng dense cho bộ nhỏ; với bộ lớn dùng cosine sparse hoặc thư viện ANN (kế hoạch tương lai).

## 10. Hướng phát triển

- Tích hợp **pretrained embeddings** từ mô tả TMDB (Sentence-BERT) để giàu ngữ nghĩa hơn.
- Thêm cơ chế **time-aware** để ưu tiên đánh giá gần đây.
- Lưu **lịch sử người dùng** cùng tín hiệu ngữ cảnh (thiết bị, thời điểm) cho gợi ý theo phiên.
- Thử nghiệm **implicit feedback** (ALS) hoặc **graph neural network** để đạt hiệu năng cao hơn.
- Triển khai lên cloud kèm CI/CD và giám sát (Azure ML + Streamlit/AKS).

## 11. Kết luận

Đồ án cung cấp một hệ thống gợi ý mang tính sản phẩm, đáp ứng và vượt yêu cầu rubric: thu thập tự động, làm sạch chắc chắn, EDA ý nghĩa, nhiều mô hình, đánh giá đầy đủ và UI hoạt động. Thiết kế module cho phép thay dataset hoặc thuật toán với tối thiểu công sức, là nền tảng vững cho nghiên cứu hay triển khai tiếp.

---

_Artifacts:_

- Mã nguồn & notebook: thư mục gốc repo.
- Báo cáo: `reports/final_report.md` (tệp hiện tại).
- Video demo (nếu có): `media/demo.mp4` (thêm sau khi ghi hình).
