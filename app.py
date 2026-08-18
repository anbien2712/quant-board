import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime

# Cấu hình giao diện Full Width
st.set_page_config(page_title="Quant Trading Executive Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- CSS BENTO GRID & DARK MODE CHUYÊN NGHIỆP ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    .bento-card {
        background: #141824;
        border: 1px solid #1e2638;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        height: 100%;
    }
    
    .card-title { color: #8a99ad; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .card-value { color: #ffffff; font-size: 32px; font-weight: 700; }
    .card-sub { font-size: 12px; margin-top: 6px; font-weight: 500; }
    
    h1, h2, h3 { color: #ffffff !important; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER TITLE ---
st.markdown("<h2 style='color: #00f2fe; margin-bottom: 0;'>⚡ QUANTITATIVE TRADING TERMINAL</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #8a99ad; font-size: 14px;'>Hệ thống giám sát vĩ mô, dòng tiền thông minh & định lượng kỹ thuật thời gian thực.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- HÀNG 1: CÁC KHUNG BENTO CARDS ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🏛️ Tỷ trọng Trụ (VN30)</div>
            <div class="card-value" style="color: #00f2fe;">58.4%</div>
            <div class="card-sub" style="color: #3fb950;">▲ +3.2% Đồng thuận tăng</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🌊 Tỷ trọng Midcap</div>
            <div class="card-value" style="color: #ff007f;">62.1%</div>
            <div class="card-sub" style="color: #3fb950;">▲ +5.1% Lan tỏa rộng</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🔥 Dòng tiền Granger</div>
            <div class="card-value" style="color: #58a6ff;">42 Mã</div>
            <div class="card-sub" style="color: #8a99ad;">Dòng tiền lớn xác nhận</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🚨 Cảnh báo Bull Trap</div>
            <div class="card-value" style="color: #f85149;">3 Mã</div>
            <div class="card-sub" style="color: #3fb950;">▼ Giảm rủi ro phân phối</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🎯 Trạng thái Vĩ mô</div>
            <div class="card-value" style="color: #3fb950; font-size: 24px; padding-top: 5px;">TÍCH CỰC</div>
            <div class="card-sub" style="color: #8a99ad;">Hệ thống an toàn giao dịch</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- HÀNG 2: BIỂU ĐỒ & PHÂN BỔ ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📈 Động Lượng Dòng Tiền (Trụ vs Midcap)")
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date)
    
    np.random.seed(42)
    df_chart = pd.DataFrame({
        'Ngày': dates,
        'Nhóm Trụ (VN30)': np.cumsum(np.random.randn(len(dates)) + 0.3) + 100,
        'Nhóm Midcap': np.cumsum(np.random.randn(len(dates)) + 0.5) + 95
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_chart['Ngày'], y=df_chart['Nhóm Trụ (VN30)'], mode='lines+markers', name='Nhóm Trụ (VN30)', line=dict(color='#00f2fe', width=3), marker=dict(size=4)))
    fig.add_trace(go.Scatter(x=df_chart['Ngày'], y=df_chart['Nhóm Midcap'], mode='lines', name='Nhóm Midcap', line=dict(color='#ff007f', width=2, dash='dot')))
    
    fig.update_layout(
        paper_bgcolor='#141824', plot_bgcolor='#141824', font=dict(color='#8a99ad', size=12),
        margin=dict(l=10, r=10, t=10, b=10), height=340,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor='#1e2638'),
        yaxis=dict(showgrid=True, gridcolor='#1e2638')
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### 📊 Phân Bổ Trạng Thái")
    labels = ['Đẩy giá mạnh', 'Tích lũy bền', 'Kéo xào Vol', 'Bull Trap']
    values = [45, 30, 15, 10]
    
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.55, marker_colors=['#00f2fe', '#4facfe', '#ff9a9e', '#ff007f'])])
    fig_pie.update_layout(
        paper_bgcolor='#141824', plot_bgcolor='#141824', font=dict(color='#8a99ad', size=12),
        margin=dict(l=10, r=10, t=10, b=10), height=340, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- HÀNG 3: BẢNG DỮ LIỆU CHUYÊN NGHIỆP ---
st.markdown("### 🏆 Bảng Xếp Hạng Top Cổ Phiếu Dẫn Dắt & Thuyết Minh Dòng Tiền")

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
