import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Quant Trading Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #2d3250; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ QUANTITATIVE TRADING EXECUTIVE DASHBOARD")
st.markdown("Hệ thống giám sát vĩ mô, dòng tiền thông minh & định lượng kỹ thuật thời gian thực.")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="🏛️ Tỷ trọng Trụ (VN30)", value="58.4%", delta="+3.2% (Đồng thuận)")
with col2: st.metric(label="🌊 Tỷ trọng Midcap/Penny", value="62.1%", delta="+5.1% (Lan tỏa)")
with col3: st.metric(label="🔥 Mã đạt chuẩn Granger", value="42 Mã", delta="Dòng tiền thật")
with col4: st.metric(label="🚨 Cảnh báo Bull Trap", value="3 Mã", delta="-2 Mã (An toàn)", delta_color="inverse")

st.markdown("---")
st.subheader("🏆 Bảng Xếp Hạng Top Cổ Phiếu Dẫn Dắt & Thuyết Minh Dòng Tiền")

df_top = pd.DataFrame({
    "STT": [1, 2, 3, 4, 5],
    "Mã CK": ["SSI", "FPT", "HPG", "MWG", "VIX"],
    "Giá (VND)": [32.5, 125.0, 28.4, 73.5, 19.2],
    "Điểm RS3M": [95.4, 92.1, 88.3, 85.0, 84.2],
    "Trạng Thái Dòng Tiền": ["🔥 Nổ thanh khoản (Đẩy giá mạnh)", "✅ Dòng tiền thật (Tích lũy bền)", "✅ Dòng tiền thật (Tích lũy bền)", "🚀 Đang tăng tốc ngắn hạn", "🩸 Bull Trap (Bán ngược cụt头)"]
})
st.dataframe(df_top, use_container_width=True)