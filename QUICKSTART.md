# 🎬 MovieLens Recommendation System

Hệ thống gợi ý phim thông minh sử dụng Machine Learning với Streamlit UI.

## ⚡ Quick Start - Streamlit Cloud

### 1. Push lên GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy trên Streamlit Cloud

1. Truy cập: https://share.streamlit.io/
2. Đăng nhập với GitHub
3. Click **"New app"**
4. Chọn repository và file `app.py`
5. Click **"Deploy!"**

🎉 Xong! App sẽ tự động:

- Download dataset
- Train models
- Chạy ứng dụng

### 3. Cấu hình MySQL (Tùy chọn)

Trong Streamlit Cloud dashboard → Settings → Secrets:

```toml
MYSQL_HOST = "your-host"
MYSQL_USER = "your-user"
MYSQL_PASSWORD = "your-password"
MYSQL_DATABASE = "movielens"
```

## 📚 Chi Tiết

- [Hướng dẫn deployment đầy đủ](STREAMLIT_CLOUD_DEPLOYMENT.md)
- [Kế hoạch dự án](PROJECT_PLAN.md)
- [Báo cáo kết quả](reports/final_report.md)

## 🛠️ Local Development

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Cài đặt dependencies
pip install -r requirements.txt

# Download data
python scripts/download_movielens.py

# Train models
python scripts/train_models.py

# Chạy app
streamlit run app.py
```

## 🔧 Tech Stack

- **Frontend**: Streamlit
- **ML Models**: Scikit-learn, Surprise
- **Data**: MovieLens dataset
- **Deployment**: Streamlit Cloud / Docker / Azure

## 📊 Features

- ✅ Content-based filtering
- ✅ Collaborative filtering (SVD)
- ✅ Hybrid recommendations
- ✅ Interactive visualizations
- ✅ User profile analytics
- ✅ Real-time telemetry

---

**URL**: Sau khi deploy, app sẽ có URL: `https://YOUR_USERNAME-YOUR_REPO.streamlit.app`
