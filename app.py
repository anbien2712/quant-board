import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Cấu hình trang Dashboard tối ưu không gian rộng
st.set_page_config(page_title="Quant Trading Executive Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- CSS TÙY CHỈNH GIAO DIỆN DARK MODE CAO CẤP ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1f242d 100%);
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    p, span, label { color: #9ca3af !important; }
    .explanation-box {
        background-color: #161b22;
        border-left: 4px solid #00f2fe;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
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
            <h4 style="color: #9ca3af; margin:0; font-size:13px;">🏛️ TỶ TRỌNG TRỤ (VN30)</h4>
            <h2 style="color: #00f2fe; margin:8px 0; font-size:26px;">58.4%</h2>
            <p style="color: #3fb950; margin:0; font-size:12px;">▲ +3.2% (Đồng thuận tăng)</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #9ca3af; margin:0; font-size:13px;">🌊 TỶ TRỌNG MIDCAP/PENNY</h4>
            <h2 style="color: #ff007f; margin:8px 0; font-size:26px;">62.1%</h2>
            <p style="color: #3fb950; margin:0; font-size:12px;">▲ +5.1% (Lan tỏa rộng)</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #9ca3af; margin:0; font-size:13px;">🔥 MÃ ĐẠT CHUẨN GRANGER</h4>
            <h2 style="color: #58a6ff; margin:8px 0; font-size:26px;">42 Mã</h2>
            <p style="color: #8b949e; margin:0; font-size:12px;">Dòng tiền lớn nhập cuộc</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="metric-card">
            <h4 style="color: #9ca3af; margin:0; font-size:13px;">🚨 CẢNH BÁO BULL TRAP</h4>
            <h2 style="color: #f85149; margin:8px 0; font-size:26px;">3 Mã</h2>
            <p style="color: #3fb950; margin:0; font-size:12px;">▼ -2 Mã so với phiên trước</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- THUYẾT MINH NHANH CHO NHÀ ĐẦU TƯ (EXECUTIVE SUMMARY) ---
st.markdown("""
    <div class="explanation-box">
        <strong style="color: #00f2fe;">💡 THUYẾT MINH CHI TIẾT TRẠNG THÁI THỊ TRƯỜNG HÔM NAY:</strong><br>
        • <b>Cấu trúc dòng tiền:</b> Cả nhóm Trụ (VN30) và Midcap đều duy trì tỷ trọng dòng tiền trên 50%, xác nhận trạng thái <i>Đồng thuận tăng</i> diện rộng.<br>
        • <b>Hành vi tạo lập:</b> Mô hình Granger ghi nhận 42 mã có dòng tiền thật dẫn dắt, rủi ro phân phối đỉnh ở mức thấp. Nhà đầu tư có thể tự tin gia tăng tỷ trọng ở các mã có điểm RS cao.
    </div>
""", unsafe_allow_html=True)

# --- HÀNG 2: BIỂU ĐỒ TRỰC QUAN (INTERACTIVE CHARTS) ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Biểu đồ Động Lượng Dòng Tiền (Trụ vs Midcap)")
    # Giả lập dữ liệu biểu đồ thời gian thực
    df_chart = pd.DataFrame({
        'Ngày': pd.date_range(start='2026-02-01', periods=20),
        'Nhóm Trụ (VN30)': np.cumsum(np.random.randn(20) + 0.4) + 100,
        'Nhóm Midcap': np.cumsum(np.random.randn(20) + 0.6) + 95
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_chart['Ngày'], y=df_chart['Nhóm Trụ (VN30)'], mode='lines+markers', name='Nhóm Trụ (VN30)', line=dict(color='#00f2fe', width=3)))
    fig.add_trace(go.Scatter(x=df_chart['Ngày'], y=df_chart['Nhóm Midcap'], mode='lines', name='Nhóm Midcap', line=dict(color='#ff007f', width=2, dash='dot')))
    
    fig.update_layout(
        paper_bgcolor='#161b22', plot_bgcolor='#161b22', font=dict(color='white'),
        margin=dict(l=10, r=10, t=20, b=10), height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("📊 Phân Bổ Trạng Thái")
    labels = ['Đẩy giá mạnh', 'Tích lũy bền', 'Kéo xào Vol', 'Bull Trap']
    values = [45, 30, 15, 10]
    
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker_colors=['#00f2fe', '#4facfe', '#ff9a9e', '#ff007f'])])
    fig_pie.update_layout(
        paper_bgcolor='#161b22', plot_bgcolor='#161b22', font=dict(color='white'),
        margin=dict(l=10, r=10, t=20, b=10), height=320, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- HÀNG 3: BẢNG XẾP HẠNG TOP CỔ PHIẾU ---
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

st.dataframe(df_top, use_container_width=True, hide_index=True)
