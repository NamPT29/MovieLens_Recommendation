"""MovieLens Recommendation System - Streamlit App."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from src.recommender import ContentBasedRecommender, HybridRecommender, load_models
from src.telemetry import fetch_recent_logs, log_recommendations, telemetry_available
from src.ui import inject_styles, render_hero_card, render_stat_cards, render_top_picks
from src.ui.components import render_model_card
from src.analytics import (
    describe_user_profile,
    build_insight_figures,
    build_catalogue_figures,
    build_usage_timeline,
)
from src.tmdb import get_poster_url

ARTIFACT_DIR = Path("models/artifacts")

MODEL_DESCRIPTIONS = {
    "Content-based": "Xây dựng fingerprint nội dung bằng TF-IDF thể loại/mô tả rồi xếp hạng các phim gần nhất với lịch sử của người dùng.",
    "Collaborative (SVD)": "Phân rã ma trận rating bằng SVD để học yếu tố tiềm ẩn user–item, tối ưu khi dữ liệu tương tác dày và đa dạng.",
    "Hybrid": "Pha trộn 55% collaborative và 45% content giúp vừa bám sát sở thích vừa mở rộng biên khám phá.",
}


@st.cache_resource
def get_models():
    """Load trained models and data artifacts."""
    if not (ARTIFACT_DIR / "content_model.joblib").exists():
        st.warning("⚠️ Models not found. Training models for the first time...")
        st.info("🔄 This may take 2-5 minutes. Please wait...")
        
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            
            # Check if data exists, if not download it
            data_path = Path("data/raw/ml-latest-small/ratings.csv")
            if not data_path.exists():
                st.info("📥 Downloading MovieLens dataset...")
                from scripts.download_movielens import main as download_main
                with st.spinner("Downloading dataset..."):
                    download_main()
                st.success("✅ Dataset downloaded!")
            
            # Train models
            st.info("🤖 Training recommendation models...")
            from scripts.train_models import main as train_main
            with st.spinner("Training models..."):
                train_main()
            
            st.success("✅ Models trained successfully! Reloading app...")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error during setup: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            st.stop()
    
    content_model, collab_model, feature_store = load_models(ARTIFACT_DIR)
    item_df = joblib.load(ARTIFACT_DIR / "item_df.joblib")
    ratings = joblib.load(ARTIFACT_DIR / "ratings.joblib")
    return content_model, collab_model, feature_store, item_df, ratings


def main() -> None:
    """Main application entry point."""
    st.set_page_config(page_title="MovieLens Recommender", layout="wide")

    # Sidebar configuration
    st.sidebar.subheader("Studio")
    theme_choice = st.sidebar.radio(
        "Theme",
        ["Dark", "Light"],
        index=0,
        help="Đổi bảng màu tổng thể của dashboard để phù hợp môi trường trình chiếu.",
    )
    alpha_default = 0.55
    hybrid_alpha = st.sidebar.slider(
        "Hybrid alpha",
        min_value=0.2,
        max_value=0.8,
        value=alpha_default,
        step=0.05,
        help="Điều chỉnh tỷ lệ trọng số giữa collaborative (cao) và content-based (thấp).",
    )
    view_mode = st.sidebar.radio(
        "Chế độ hiển thị",
        ["Dashboard phân tích", "Movie browser (mô phỏng xem phim)"],
        index=0,
        help="Chuyển sang chế độ mô phỏng web xem phim với player giả lập và danh sách đề xuất.",
    )
    inject_styles(theme_choice)

    # Load models and data
    content_model, collab_model, feature_store, item_df, ratings = get_models()
    hybrid_model = HybridRecommender(
        content_model=content_model, collab_model=collab_model, alpha=hybrid_alpha
    )

    # User controls
    user_ids = sorted(ratings["userId"].unique())
    st.sidebar.header("Điều hướng")
    user_id = st.sidebar.selectbox(
        "User ID",
        user_ids,
        index=0,
        help="Chọn user thực tế từ MovieLens để xem lịch sử gợi ý cá nhân.",
    )
    model_choice = st.sidebar.selectbox(
        "Model",
        ["Content-based", "Collaborative (SVD)", "Hybrid"],
        help="So sánh nhanh giữa ba chiến lược gợi ý đang triển khai.",
    )
    top_k = st.sidebar.slider(
        "Number of recommendations",
        min_value=5,
        max_value=20,
        value=10,
        help="Quy định số lượng phim xuất hiện trong bảng xếp hạng.",
    )
    genre_filter = st.sidebar.text_input(
        "Optional genre filter (e.g., Comedy)",
        help="Lọc nhanh theo thể loại quan tâm, hỗ trợ viết thường/hoa tự do.",
    )

    # Get user history and recommendations
    user_history = ratings[ratings["userId"] == user_id]

    if model_choice == "Content-based":
        recs = content_model.recommend(user_history, top_k=top_k)
    elif model_choice == "Collaborative (SVD)":
        recs = collab_model.recommend(user_id, item_df, top_k=top_k)
        recs = recs.rename(columns={"est_rating": "model_score"})
    else:
        recs = hybrid_model.recommend(user_id, user_history, top_k=top_k)
        recs = recs.rename(columns={"hybrid_score": "model_score"})

    if "model_score" not in recs.columns:
        recs["model_score"] = recs.get("score")

    # Apply genre filter
    if genre_filter:
        recs = recs[recs["genres"].str.contains(genre_filter, case=False, na=False)]

    # Auto-log recommendations
    base_display_cols = [
        "clean_title",
        "genres",
        "avg_rating",
        "rating_count",
        "model_score",
    ]
    logging_cols = [col for col in ["movieId", "model_score"] if col in recs.columns]
    auto_logged = False
    if telemetry_available() and "movieId" in recs.columns and not recs.empty:
        movie_ids = tuple(int(mid) for mid in recs["movieId"].tolist())
        signature = hash(
            (
                user_id,
                model_choice,
                top_k,
                (genre_filter or "").strip().lower(),
                movie_ids,
            )
        )
        last_sig = st.session_state.get("auto_log_sig")
        if movie_ids and signature != last_sig and logging_cols:
            inserted = log_recommendations(
                user_id,
                model_choice,
                recs[logging_cols],
                action="auto",
            )
            if inserted:
                st.session_state["auto_log_sig"] = signature
                auto_logged = True

    # Render UI components
    profile = describe_user_profile(user_history, item_df)

    if view_mode == "Dashboard phân tích":
        render_hero_card()
        render_stat_cards(profile)

        # Analytics charts
        rating_fig, genre_fig, rating_label, genre_label = build_insight_figures(
            user_history, item_df, ratings
        )
        insight_col1, insight_col2 = st.columns(2, gap="large")
        with insight_col1:
            st.markdown(f"#### {rating_label}")
            st.plotly_chart(rating_fig, width='stretch', config={"displayModeBar": False})
        with insight_col2:
            st.markdown(f"#### {genre_label}")
            st.plotly_chart(genre_fig, width='stretch', config={"displayModeBar": False})

        pop_fig, scatter_fig, pop_label, scatter_label = build_catalogue_figures(ratings, item_df)
        global_col1, global_col2 = st.columns(2, gap="large")
        with global_col1:
            st.markdown(f"#### {pop_label}")
            st.plotly_chart(pop_fig, width='stretch', config={"displayModeBar": False})
        with global_col2:
            st.markdown(f"#### {scatter_label}")
            st.plotly_chart(scatter_fig, width='stretch', config={"displayModeBar": False})

        # Model description
        genre_phrase = f" · Lọc: {genre_filter.title()}" if genre_filter else ""
        alpha_phrase = f" · α={hybrid_alpha:.2f}" if model_choice == "Hybrid" else ""
        context_line = f"User #{user_id} · Top {top_k}{genre_phrase}{alpha_phrase}"
        render_model_card(model_choice, MODEL_DESCRIPTIONS, context_line)

        # Recommendations table
        st.subheader("Bảng xếp hạng đề xuất")
        display_df = recs[base_display_cols].rename(
            columns={"clean_title": "Title", "model_score": "Model Score"}
        )
        display_df = display_df.loc[:, ~display_df.columns.duplicated()]
        render_top_picks(display_df)
        st.dataframe(display_df, width='stretch', height=540)
    else:
        render_hero_card()
        render_stat_cards(profile)

        st.subheader("Màn hình xem phim (mô phỏng)")
        if recs.empty:
            st.info("Không có phim phù hợp để gợi ý cho cấu hình hiện tại.")
        else:
            movie_titles = recs["clean_title"].tolist()
            default_index = 0
            selected_title = st.selectbox(
                "Chọn phim để xem",
                movie_titles,
                index=default_index,
                help="Chọn một phim trong danh sách gợi ý để mô phỏng màn hình xem phim.",
            )
            current_movie = recs[recs["clean_title"] == selected_title].iloc[0]

            col_player, col_meta = st.columns([3, 2], gap="large")
            with col_player:
                genres_text = str(current_movie.get("genres", ""))

                poster_url = None
                if "movieId" in current_movie:
                    try:
                        poster_url = get_poster_url(int(current_movie["movieId"]))
                    except Exception:
                        poster_url = None

                if poster_url:
                    # Hiển thị poster nhỏ lại (~60% chiều rộng cột) cho dễ nhìn
                    st.markdown(
                        f"""
                        <div style="max-width: 60%; margin: 0 auto;">
                            <img src="{poster_url}" alt="Poster" style="width: 100%; border-radius: 24px; box-shadow: 0 24px 60px rgba(0,0,0,0.7);" />
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="fake-player">
                            <div class="fake-player-overlay">
                                <span class="pill">NOW PLAYING</span>
                                <h2>{current_movie['clean_title']}</h2>
                                <p class="fake-player-meta">{genres_text}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with col_meta:
                st.markdown("#### Thông tin phim")

                st.write(f"**Thể loại:** {current_movie.get('genres', 'N/A')}")
                avg_rating_val = current_movie.get("avg_rating")
                try:
                    st.write(f"**Điểm trung bình:** {float(avg_rating_val):.2f}")
                except Exception:
                    st.write("**Điểm trung bình:** N/A")
                st.write(f"**Số lượt đánh giá:** {int(current_movie.get('rating_count', 0))}")
                st.write(f"**Model gợi ý:** {model_choice}")
                st.write(f"**User:** #{user_id}")

            st.markdown("### Phim tiếp theo dành cho bạn")
            next_recs = recs[recs["clean_title"] != selected_title].head(max(top_k - 1, 1))
            if next_recs.empty:
                st.info("Không còn phim nào khác trong danh sách đề xuất.")
            else:
                browser_cols = [
                    "clean_title",
                    "genres",
                    "avg_rating",
                    "rating_count",
                    "model_score",
                ]
                browser_cols = [c for c in browser_cols if c in next_recs.columns]
                browser_df = next_recs[browser_cols].rename(
                    columns={
                        "clean_title": "Title",
                        "avg_rating": "Avg Rating",
                        "rating_count": "#Ratings",
                        "model_score": "Model Score",
                    }
                )
                browser_df = browser_df.loc[:, ~browser_df.columns.duplicated()]
                st.dataframe(browser_df, width='stretch', height=420)

    # Telemetry controls
    log_box = st.sidebar.container()
    if telemetry_available():
        if auto_logged:
            log_box.success("Đã tự động ghi nhận lịch sử cho cấu hình hiện tại.")
        if log_box.button("Lưu thủ công", help="Nhấn khi muốn ép ghi lại log cho cấu hình này"):
            if "movieId" not in recs.columns or not logging_cols:
                log_box.error("Không tìm thấy dữ liệu hợp lệ để ghi log.")
            else:
                inserted = log_recommendations(
                    user_id, model_choice, recs[logging_cols], action="manual"
                )
                if inserted:
                    log_box.success(f"Đã lưu {inserted} dòng vào MySQL")
                else:
                    log_box.warning("Không có bản ghi nào được lưu (bảng rỗng hoặc lỗi kết nối).")
    else:
        log_box.info("Thiết lập MYSQL_HOST/PORT/USER/PASSWORD/DATABASE để bật lưu lịch sử.")

    st.caption(
        "Dùng thanh bên để điều hướng giữa các chế độ và quan sát cách mỗi thuật toán tái cấu hình bảng xếp hạng trong thời gian thực."
    )

    # MySQL telemetry viewer
    if telemetry_available():
        with st.expander("Lịch sử tương tác (MySQL)", expanded=False):
            limit = st.slider(
                "Số dòng gần nhất", min_value=5, max_value=50, value=15, step=5, key="log_limit"
            )
            logs = list(fetch_recent_logs(limit=limit))
            if logs:
                log_df, timeline_fig = build_usage_timeline(logs)
                if timeline_fig is not None:
                    st.plotly_chart(
                        timeline_fig, width='stretch', config={"displayModeBar": False}
                    )
                st.dataframe(log_df)
            else:
                st.info("Chưa có dữ liệu được ghi hoặc không thể kết nối MySQL.")


if __name__ == "__main__":
    main()
