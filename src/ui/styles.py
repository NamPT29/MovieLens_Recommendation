"""Theme and styling configuration for the Streamlit app."""

import streamlit as st


def inject_styles(theme: str = "Dark") -> None:
    """Inject CSS that changes based on theme selection."""
    bg_dark = "radial-gradient(circle at 20% 20%, rgba(255,255,255,0.06), transparent 42%), radial-gradient(circle at 80% 0%, rgba(255,107,53,0.12), transparent 45%), #050912"
    bg_light = "linear-gradient(135deg, #fdf7f2 0%, #f1f5ff 60%, #e5eefb 100%)"
    
    if theme == "Light":
        bg = bg_light
        text_color = "#1c2439"
        panel_bg = "rgba(255,255,255,0.9)"
        panel_solid = "#ffffff"
        border_color = "rgba(15,23,42,0.08)"
        muted_color = "#5f6580"
        sidebar_bg = "linear-gradient(180deg, #ffffff 0%, #f0f4ff 100%)"
        hero_bg = "linear-gradient(120deg, #ffffff 0%, #f1f5ff 60%, #fef2e8 100%)"
        hero_text = "#101530"
        stat_text = "#101530"
        label_color = "rgba(15,23,42,0.65)"
        eyebrow_color = "rgba(16,21,48,0.7)"
        chip_bg = "rgba(15,23,42,0.04)"
        chip_border = "rgba(15,23,42,0.12)"
        chip_text = "#1c2439"
        df_bg = "#ffffff"
        df_border = "rgba(15,23,42,0.08)"
        df_text = "#1c2439"
        model_tag_text = "#a5482a"
    else:
        bg = bg_dark
        text_color = "#ffffff"
        panel_bg = "rgba(15,23,42,0.78)"
        panel_solid = "#141b2f"
        border_color = "rgba(255,255,255,0.12)"
        muted_color = "#ffffff"
        sidebar_bg = "linear-gradient(180deg, #040812 0%, #0a1630 100%)"
        hero_bg = "linear-gradient(125deg, #111a36 0%, #1f2750 60%, #1b4b6b 100%)"
        hero_text = "#ffffff"
        stat_text = "#ffffff"
        label_color = "#ffffff"
        eyebrow_color = "#ffffff"
        chip_bg = "rgba(255,255,255,0.05)"
        chip_border = "rgba(255,255,255,0.12)"
        chip_text = "#ffffff"
        df_bg = "#050913"
        df_border = "rgba(255,255,255,0.12)"
        df_text = "#ffffff"
        model_tag_text = "#ffffff"
    
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&family=Clash+Display:wght@500;600&family=Source+Code+Pro:wght@500&display=swap');
            
            .stApp {{
                font-family: 'Space Grotesk', sans-serif;
                background: {bg} !important;
                color: {text_color} !important;
            }}
            
            .stApp *, .stMarkdown, .stMarkdown * {{
                color: {text_color} !important;
            }}
            
            [data-testid="stSidebar"] {{
                background: {sidebar_bg} !important;
                color: {text_color} !important;
                border-right: 1px solid {border_color} !important;
            }}
            
            [data-testid="stSidebar"] * {{
                font-family: 'Space Grotesk', sans-serif !important;
                color: {text_color} !important;
            }}
            
            /* Input fields and select boxes - black text on white background */
            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] select,
            [data-testid="stSidebar"] textarea,
            .stSelectbox > div > div,
            .stTextInput > div > div > input {{
                color: #000000 !important;
                background-color: #ffffff !important;
            }}
            
            /* Dropdown options */
            [data-baseweb="popover"] {{
                color: #000000 !important;
            }}
            
            [data-baseweb="select"] span,
            [data-baseweb="select"] div {{
                color: #000000 !important;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                font-family: 'Clash Display', 'Space Grotesk', sans-serif !important;
                color: {text_color} !important;
            }}
            
            .hero-card {{
                position: relative;
                overflow: hidden;
                background: {hero_bg};
                padding: 36px 40px;
                border-radius: 32px;
                color: {hero_text} !important;
                border: 1px solid {border_color};
                box-shadow: 0 25px 70px rgba(5,10,22,0.3);
            }}
            
            .hero-card * {{
                color: {hero_text} !important;
            }}
            
            .hero-card::after {{
                content: "";
                position: absolute;
                inset: 0;
                background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.18), transparent 45%);
                pointer-events: none;
                mix-blend-mode: screen;
            }}
            
            .hero-card h1 {{
                margin-bottom: 10px;
                font-size: 2.6rem;
                letter-spacing: -0.02em;
                position: relative;
                z-index: 1;
            }}
            
            .hero-card p {{
                position: relative;
                z-index: 1;
                opacity: 0.9;
                max-width: 700px;
            }}
            
            .hero-copy {{
                font-size: 1.05rem;
                line-height: 1.55;
            }}
            
            .eyebrow {{
                font-size: 0.85rem;
                letter-spacing: 0.25em;
                text-transform: uppercase;
                color: {eyebrow_color} !important;
                margin-bottom: 12px;
                display: inline-block;
            }}
            
            .hero-meta {{
                position: relative;
                z-index: 1;
                margin-top: 18px;
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
            }}
            
            .hero-meta span {{
                font-size: 0.85rem;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                padding: 6px 14px;
                border-radius: 999px;
                border: 1px solid {border_color};
                background: {chip_bg};
                color: {chip_text} !important;
            }}
            
            .stat-card {{
                background: {panel_bg};
                border-radius: 22px;
                padding: 20px 24px;
                border: 1px solid {border_color};
                box-shadow: 0 18px 50px rgba(3,7,18,0.2);
                min-height: 120px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}
            
            .stat-label {{
                text-transform: uppercase;
                font-size: 0.72rem;
                letter-spacing: 0.12em;
                color: {label_color} !important;
                margin-bottom: 8px;
            }}
            
            .stat-value {{
                font-size: 2rem;
                font-weight: 600;
                margin-top: 8px;
                color: {stat_text} !important;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}
            
            .model-card {{
                border-radius: 22px;
                padding: 24px 28px;
                background: {panel_solid};
                border: 1px solid {border_color};
                margin-top: 28px;
                box-shadow: 0 18px 45px rgba(5,8,20,0.3);
                color: {text_color} !important;
            }}
            
            .model-card * {{
                color: {text_color} !important;
            }}
            
            .model-footnote {{
                margin-top: 12px;
                font-size: 0.85rem;
                color: {muted_color} !important;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}
            
            .model-tag {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-family: 'Source Code Pro', monospace;
                font-size: 0.85rem;
                background: rgba(255,107,53,0.15);
                color: {model_tag_text} !important;
                border-radius: 999px;
                padding: 4px 12px;
                border: 1px solid rgba(255,107,53,0.35);
            }}
            
            .top-picks {{
                margin: 18px 0 12px;
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                align-items: center;
            }}
            
            .top-picks-title {{
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.2em;
                color: {muted_color} !important;
            }}
            
            .chip {{
                background: {chip_bg};
                border-radius: 999px;
                padding: 6px 14px;
                border: 1px solid {chip_border};
                box-shadow: 0 6px 18px rgba(8,12,26,0.2);
                font-weight: 500;
                color: {chip_text} !important;
            }}

            /* Fake video player for movie browser mode */
            .fake-player {{
                position: relative;
                width: 100%;
                padding-top: 56.25%; /* 16:9 ratio */
                border-radius: 24px;
                overflow: hidden;
                background: radial-gradient(circle at 10% 10%, rgba(255,255,255,0.18), transparent 40%),
                            radial-gradient(circle at 90% 0%, rgba(255,107,53,0.35), transparent 45%),
                            #050814;
                box-shadow: 0 30px 80px rgba(0,0,0,0.6);
                border: 1px solid {border_color};
            }}

            .fake-player-overlay {{
                position: absolute;
                inset: 0;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding: 24px 28px;
                background: linear-gradient(180deg, rgba(5,8,20,0.05) 0%, rgba(5,8,20,0.85) 100%);
            }}

            .fake-player-overlay h2 {{
                margin: 4px 0 6px;
                font-size: 1.6rem;
                letter-spacing: -0.02em;
            }}

            .fake-player-meta {{
                font-size: 0.9rem;
                opacity: 0.9;
            }}

            .pill {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 12px;
                border-radius: 999px;
                font-size: 0.75rem;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                border: 1px solid rgba(255,255,255,0.4);
                background: rgba(15,23,42,0.6);
            }}
            
            div[data-testid="stDataFrame"] > div {{
                border-radius: 26px;
                border: 1px solid {df_border};
                background: {df_bg};
                box-shadow: 0 25px 70px rgba(5,8,20,0.3);
            }}
            
            div[data-testid="stDataFrame"] table {{
                color: {df_text} !important;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 0.95rem;
            }}
            
            div[data-testid="stDataFrame"] tbody tr:hover {{
                background: rgba(255,107,53,0.08) !important;
            }}
            
            div[data-testid="stDataFrame"] thead {{
                background: linear-gradient(90deg, rgba(255,255,255,0.05), rgba(255,255,255,0));
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
