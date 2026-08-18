import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime

# Cấu hình giao diện Full Width & Sidebar ẩn
st.set_page_config(page_title="Quant Trading Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- CSS NÂNG CẤP ĐẲNG CẤP UI/UX (DARK MODE TERMINAL) ---
st.markdown("""
    <style>
    /* Tổng thể nền */
    .stApp { background-color: #07090e; color: #f1f5f9; font-family: 'Inter', sans-serif; }
    
    /* Ẩn header và menu mặc định của streamlit cho thoáng */
    header { visibility: hidden; }
    
    /* Thiết kế Bento Card siêu mịn */
    .bento-card {
        background: #0f131f;
        border: 1px solid #1a2234;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
    }
    .bento-card:hover {
        border-color: #2e3b55;
    }
    
    .card-title { color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .card-value { color: #ffffff; font-size: 30px; font-weight: 800; }
    .card-sub { font-size: 12px; margin-top: 8px; font-weight: 600; }
    
    /* Tùy chỉnh bảng dữ liệu thành Dark Mode hoàn toàn */
    [data-testid="stDataFrame"] {
        background-color: #0f131f;
        border: 1px solid #1a2234;
        border-radius: 14px;
        overflow: hidden;
    }
    
    h3 { color: #f1f5f9 !important; font-weight: 700; font-size: 18px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER TITLE ---
st.markdown("<h2 style='color: #00f2fe; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 2px;'>⚡ QUANTITATIVE TRADING TERMINAL</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-size: 13px; font-weight: 500;'>Hệ thống giám sát vĩ mô, dòng tiền thông minh & định lượng kỹ thuật thời gian thực.</p>", unsafe_allow_html=True)
st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)

# --- HÀNG 1: CÁC KHUNG BENTO CARDS ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🏛️ Tỷ trọng Trụ (VN30)</div>
            <div class="card-value" style="color: #00f2fe;">58.4%</div>
            <div class="card-sub" style="color: #10b981;">▲ +3.2% Đồng thuận</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🌊 Tỷ trọng Midcap</div>
            <div class="card-value" style="color: #f43f5e;">62.1%</div>
            <div class="card-sub" style="color: #10b981;">▲ +5.1% Lan tỏa</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🔥 Dòng tiền Granger</div>
            <div class="card-value" style="color: #38bdf8;">42 Mã</div>
            <div class="card-sub" style="color: #64748b;">Xác nhận dòng lớn</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🚨 Cảnh báo Bull Trap</div>
            <div class="card-value" style="color: #fb7185;">3 Mã</div>
            <div class="card-sub" style="color: #10b981;">▼ Giảm rủi ro xả</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
        <div class="bento-card">
            <div class="card-title">🎯 Trạng thái Vĩ mô</div>
            <div class="card-value" style="color: #10b981; font-size: 22px; padding-top: 4px;">TÍCH CỰC</div>
            <div class="card-sub" style="color: #64748b;">An toàn giao dịch</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

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
    fig.add_trace(go.Scatter(x=df_chart['Ngày'], y=df_chart['Nhóm Trụ (VN30)'], mode='lines', name='Nhóm Trụ (VN30)', line=dict(color='#00f2fe', width=2.5)))
    fig.add_trace(go.Scatter(x=df_chart['Ngày'], y=df_chart['Nhóm Midcap'], mode='lines', name='Nhóm Midcap', line=dict(color='#f43f5e', width=2, dash='dot')))
    
    fig.update_layout(
        paper_bgcolor='#0f131f', plot_bgcolor='#0f131f', font=dict(color='#64748b', size=11),
        margin=dict(l=10, r=10, t=10, b=10), height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#f1f5f9')),
        xaxis=dict(showgrid=True, gridcolor='#1a2234', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#1a2234', zeroline=False)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### 📊 Phân Bổ Trạng Thái")
    labels = ['Đẩy giá mạnh', 'Tích lũy bền', 'Kéo xào Vol', 'Bull Trap']
    values = [45, 30, 15, 10]
    
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker_colors=['#00f2fe', '#38bdf8', '#fb7185', '#f43f5e'])])
    fig_pie.update_layout(
        paper_bgcolor='#0f131f', plot_bgcolor='#0f131f', font=dict(color='#64748b', size=11),
        margin=dict(l=10, r=10, t=10, b=10), height=320, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color='#f1f5f9'))
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

# --- HÀNG 3: BẢNG XẾP HẠNG DARK MODE HOÀN TOÀN ---
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
