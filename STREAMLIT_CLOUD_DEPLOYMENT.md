# Hướng Dẫn Deploy Lên Streamlit Cloud

## 📋 Checklist Trước Khi Deploy

✅ Đã tạo các file cấu hình:

- [x] `.streamlit/config.toml` - Cấu hình UI
- [x] `.gitignore` - Loại trừ file không cần thiết
- [x] `packages.txt` - System dependencies
- [x] `requirements.txt` - Python dependencies

⚠️ **LƯU Ý QUAN TRỌNG**: Models phải được train lại sau khi deploy vì artifacts quá lớn để push lên GitHub.

## 🚀 Các Bước Deploy

### Bước 1: Chuẩn Bị GitHub Repository

```bash
# Khởi tạo Git (nếu chưa có)
git init

# Add tất cả files (gitignore sẽ tự động loại trừ file không cần)
git add .

# Commit
git commit -m "Initial commit - MovieLens Recommender"

# Tạo repository trên GitHub rồi push
git remote add origin https://github.com/your-username/your-repo-name.git
git branch -M main
git push -u origin main
```

### Bước 2: Deploy Trên Streamlit Cloud

1. Truy cập: https://share.streamlit.io/
2. Đăng nhập bằng GitHub account
3. Click **"New app"**
4. Chọn:
   - **Repository**: your-username/your-repo-name
   - **Branch**: main
   - **Main file path**: app.py
5. Click **"Deploy!"**

### Bước 3: Train Models Trên Cloud (QUAN TRỌNG!)

Sau khi app deploy lần đầu, nó sẽ báo lỗi vì chưa có models. Bạn cần:

**Option 1: Train tự động khi khởi động** (Khuyến nghị)

Thêm code này vào `app.py` để tự động train nếu chưa có models:

```python
# Thêm vào đầu hàm main() hoặc get_models()
if not (ARTIFACT_DIR / "content_model.joblib").exists():
    st.info("🔄 Training models for the first time... This may take a few minutes.")
    from scripts.train_models import main as train_main
    train_main()
    st.success("✅ Models trained successfully!")
    st.rerun()
```

**Option 2: Pre-train và upload artifacts**

```bash
# Train models locally
python scripts/train_models.py

# Compress artifacts
tar -czf models.tar.gz models/artifacts/

# Upload to cloud storage (Google Drive, Dropbox, etc.)
# Rồi download trong app khi khởi động
```

### Bước 4: Cấu Hình Secrets (Nếu Dùng MySQL)

Nếu bạn sử dụng MySQL telemetry:

1. Trong Streamlit Cloud dashboard, click vào app của bạn
2. Click **"Settings"** → **"Secrets"**
3. Thêm secrets:

```toml
MYSQL_HOST = "your-mysql-host"
MYSQL_PORT = 3306
MYSQL_USER = "your-username"
MYSQL_PASSWORD = "your-password"
MYSQL_DATABASE = "movielens"
```

### Bước 5: Giám Sát & Quản Lý

- **URL**: App của bạn sẽ có địa chỉ: `https://your-username-your-repo-name.streamlit.app`
- **Logs**: Xem logs trong Streamlit Cloud dashboard
- **Reboot**: Nếu cần restart, click "⋮" → "Reboot app"
- **Update**: Mỗi lần push code mới lên GitHub, app sẽ tự động redeploy

## 🎯 Tips & Best Practices

### Tối Ưu Performance

1. **Cache aggressively**:

   ```python
   @st.cache_resource  # Cho models
   @st.cache_data      # Cho data
   ```

2. **Lazy loading**: Chỉ load models khi cần
3. **Compress data**: Dùng parquet thay vì CSV
4. **Limit data size**: Dùng subset của MovieLens (small dataset)

### Xử Lý Data Files

Vì GitHub giới hạn file size, bạn có thể:

1. **Download on startup**:

   ```python
   if not Path("data/raw").exists():
       download_movielens_data()
   ```

2. **Use Git LFS**: Cho files lớn

   ```bash
   git lfs install
   git lfs track "*.csv"
   ```

3. **Host externally**: Upload data lên cloud storage

## ⚡ Quick Fix Cho Lỗi Thường Gặp

### Lỗi: "Models not found"

→ Thêm auto-training code như Option 1 ở trên

### Lỗi: "Memory limit exceeded"

→ Giảm kích thước dataset hoặc upgrade plan

### Lỗi: "Module not found"

→ Kiểm tra `requirements.txt` có đầy đủ dependencies

### Lỗi: "Git LFS bandwidth"

→ Host data files trên external storage

## 🔗 Resources

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Community Forum: https://discuss.streamlit.io/
- Status Page: https://status.streamlit.io/

---

**Lưu ý**: Streamlit Cloud free tier có giới hạn:

- 1GB RAM per app
- 1 CPU core
- 3 apps maximum
- Public repositories only (hoặc cần upgrade cho private repos)
