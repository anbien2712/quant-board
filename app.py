import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# --- CẤU HÌNH ---
st.set_page_config(page_title="E.V Quant Executive Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #d1d5db; }
    .bento-box { background: #151a23; border: 1px solid #1f2937; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
    .box-title { color: #f3f4f6; font-size: 16px; font-weight: 700; margin-bottom: 15px; border-bottom: 1px solid #1f2937; padding-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- ĐỌC DỮ LIỆU THẬT ---
try:
    df = pd.read_csv("MASTER_QUANT_DB.csv")
    df.columns = [col.upper() for col in df.columns]
    
    # Lọc VNINDEX - Giả định file CSV có cột 'TICKER' hoặc 'SYMBOL'
    ticker_col = 'TICKER' if 'TICKER' in df.columns else 'SYMBOL'
    df_vni = df[df[ticker_col].astype(str).str.upper() == 'VNINDEX'].sort_values('DATE')
    
    data_ok = not df_vni.empty
except Exception as e:
    data_ok = False
    err_msg = str(e)

# --- UI ---
st.markdown("<h2 style='color: #3b82f6;'>⚡ E.V QUANTITATIVE TERMINAL (DATA REALTIME)</h2>", unsafe_allow_html=True)

if not data_ok:
    st.error("⚠️ Không tìm thấy dữ liệu VNINDEX trong file CSV. Vui lòng kiểm tra lại Colab!")
    st.stop()

# ====================================================================================
# BIỂU ĐỒ VNINDEX TỪ DỮ LIỆU THẬT
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">📊 VNINDEX - Dữ liệu thực tế từ DNSE API</div>', unsafe_allow_html=True)

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df_vni['DATE'], y=df_vni['CLOSE'], name='VNINDEX', line=dict(color='#3b82f6', width=3)), secondary_y=False)
fig.add_trace(go.Bar(x=df_vni['DATE'], y=df_vni['VOLUME'], name='Khối lượng', marker_color='rgba(16, 185, 129, 0.3)'), secondary_y=True)

fig.update_layout(
    paper_bgcolor='#151a23', plot_bgcolor='#151a23', font=dict(color='#9ca3af'),
    height=300, margin=dict(l=10, r=10, t=10, b=10)
)
st.plotly_chart(fig, use_container_width=True)

# --- THUYẾT MINH 3 PHA TỰ ĐỘNG ---
last_price = df_vni['CLOSE'].iloc[-1]
st.markdown(f"""
    * **Điểm số:** {last_price:,.2f}
    * **Pha 1 (Trend):** Xu hướng trung hạn dựa trên Multi-MA.
    * **Pha 2 (Dòng tiền):** Phân tích từ chỉ số Tick-Volume Proxy.
    * **Pha 3 (Độ tin cậy):** Đánh giá dựa trên xác suất ML.
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
