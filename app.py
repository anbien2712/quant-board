import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Cấu hình trang Dashboard
st.set_page_config(page_title="Quant Trading Executive Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- CSS TÙY CHỈNH ÉP GIAO DIỆN TỐI (DARK MODE) & BO TRÒN HIỆN ĐẠI ---
st.markdown("""
    <style>
    /* Ép toàn bộ nền thành màu tối sang trọng */
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    
    /* Thiết kế thẻ Card Metrics giống hệt phong cách Crypto/Trading Dashboard */
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1f242d 100%);
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Tiêu đề bảng và chữ */
    h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    p, span, label { color: #9ca3af !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER TITLE ---
st.markdown("<h1 style='color: #00f2fe !important;'>⚡ QUANTITATIVE TRADING EXECUTIVE DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("Hệ thống giám sát vĩ mô, dòng tiền thông minh & định lượng kỹ thuật thời gian thực.")
st.markdown("---")

# --- HÀNG 1: CÁC THẺ CHỈ SỐ (METRICS CARDS) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #9ca3af; margin:0; font-size:14px;">🏛️ TỶ TRỌNG TRỤ (VN30)</h4>
            <h2 style="color: #00f2fe; margin:10px 0; font-size:28px;">58.4%</h2>
            <p style="color: #3fb950; margin:0; font-size:13px;">▲ +3.2% (Đồng thuận tăng)</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #9ca3af; margin:0; font-size:14px;">🌊 TỶ TRỌNG MIDCAP/PENNY</h4>
            <h2 style="color: #ff007f; margin:10px 0; font-size:28px;">62.1%</h2>
            <p style="color: #3fb950; margin:0; font-size:13px;">▲ +5.1% (Lan tỏa rộng)</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #9ca3af; margin:0; font-size:14px;">🔥 MÃ ĐẠT CHUẨN GRANGER</h4>
            <h2 style="color: #58a6ff; margin:10px 0; font-size:28px;">42 Mã</h2>
            <p style="color: #8b949e; margin:0; font-size:13px;">Dòng tiền lớn nhập cuộc</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #9ca3af; margin:0; font-size:14px;">🚨 CẢNH BÁO BULL TRAP</h4>
            <h2 style="color: #f85149; margin:10px 0; font-size:28px;">3 Mã</h2>
            <p style="color: #3fb950; margin:0; font-size:13px;">▼ -2 Mã so với phiên trước</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# --- HÀNG 2: BẢNG XẾP HẠNG TOP CỔ PHIẾU ---
st.subheader("🏆 Bảng Xếp Hạng Top Cổ Phiếu Dẫn Dắt & Thuyết Minh Dòng Tiền")

df_top = pd.DataFrame({
    "STT": [1, 2, 3, 4, 5],
    "Mã CK": ["SSI", "FPT", "HPG", "MWG", "VIX"],
    "Giá (VND)": [32.5, 125.0, 28.4, 73.5, 19.2],
    "Điểm RS3M": [95.4, 92.1, 88.3, 85.0, 84.2],
    "Trạng Thái Dòng Tiền": [
        "🔥 Nổ thanh khoản (Đẩy giá mạnh)", 
        "✅ Dòng tiền thật (Tích lũy bền)", 
        "✅ Dòng tiền thật (Tích lũy bền)", 
        "🚀 Đang tăng tốc ngắn hạn", 
        "🩸 Bull Trap (Bán ngược cụt đầu)"
    ]
})

# Hiển thị bảng sạch sẽ, ẩn đi cột index số thứ tự mặc định của pandas
st.dataframe(df_top, use_container_width=True, hide_index=True)
