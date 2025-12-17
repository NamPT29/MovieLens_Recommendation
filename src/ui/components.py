"""UI components for the Streamlit app."""

import pandas as pd
import streamlit as st


def render_hero_card() -> None:
    """Render the hero card with app title and description."""
    st.markdown(
        """
        <div class="hero-card">
            <span class="eyebrow">MOVIELENS OPS · LIVE FEED</span>
            <h1>Bảng Điều Khiển Gợi Ý Chiến Lược</h1>
            <p class="hero-copy">Theo dõi phản ứng của ba thuật toán chủ đạo đối với từng người dùng cụ thể, so sánh tức thời và khóa lại cấu hình gợi ý phù hợp nhất trước khi đẩy sang môi trường triển khai.</p>
            <div class="hero-meta">
                <span>Pipeline đã làm sạch</span>
                <span>Artifacts versioned</span>
                <span>Giải thích trực quan</span>
            </div>
        </div>
        <div style="margin-bottom: 32px;"></div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(profile: dict[str, str]) -> None:
    """Render stat cards showing user profile information."""
    col_a, col_b, col_c = st.columns([1, 1, 1], gap="large")
    with col_a:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">LƯỢT ĐÁNH GIÁ</div>
                <div class="stat-value">{profile['count']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">ĐIỂM TRUNG BÌNH</div>
                <div class="stat-value">{profile['avg']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_c:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">THỂ LOẠI ƯA THÍCH</div>
                <div class="stat-value" style="font-size:1.2rem; word-wrap: break-word;">{profile['genres']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Add spacing after stat cards
    st.markdown('<div style="margin-bottom: 32px;"></div>', unsafe_allow_html=True)


def render_top_picks(display_df: pd.DataFrame) -> None:
    """Render top 3 movie picks as chips."""
    if display_df.empty:
        return
    picks = display_df["Title"].head(3).tolist()
    chips = "".join(f"<span class='chip'>{title}</span>" for title in picks)
    st.markdown(
        f"""
        <div class="top-picks">
            <span class="top-picks-title">Spotlight</span>
            {chips}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_model_card(model_choice: str, model_descriptions: dict, context_line: str) -> None:
    """Render model description card."""
    model_copy = model_descriptions.get(model_choice, "")
    st.markdown(
        f"""
        <div class="model-card">
            <div class="model-tag">Model Focus</div>
            <h3>{model_choice}</h3>
            <p>{model_copy}</p>
            <p class="model-footnote">{context_line}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
