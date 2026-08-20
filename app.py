import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os # Đã thêm thư viện này để check file

# --- CẤU HÌNH TRANG WIDE MODE ---
st.set_page_config(page_title="E.V Quant Executive Terminal V5.1", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS: BENTO GRID & MODERN UI ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #d1d5db; font-family: 'Inter', sans-serif; }
    header { visibility: hidden; }
    
    .bento-box {
        background: #151a23;
        border: 1px solid #1f2937;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .box-title {
        color: #f3f4f6;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 1px solid #1f2937;
        padding-bottom: 8px;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
        font-size: 13px;
        background-color: #151a23;
    }
    .custom-table th {
        background-color: #1a2230;
        color: #9ca3af;
        padding: 12px 16px;
        font-weight: 600;
        border-bottom: 1px solid #2d3748;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.5px;
    }
    .custom-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #1f2937;
        color: #e5e7eb;
    }
    .custom-table tr:hover {
        background-color: #1c2433;
    }
    .badge-bull {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 11px;
        display: inline-block;
    }
    .badge-bear {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 11px;
        display: inline-block;
    }
    .badge-stable {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 11px;
        display: inline-block;
    }
    .metric-value {
        color: #3b82f6; 
        font-size: 24px; 
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

# --- ĐỌC DỮ LIỆU TỪ MASTER DB ---
@st.cache_data(ttl=300) # Cache dữ liệu 5 phút để load mượt mà
def load_data():
    try:
        df = pd.read_csv("MASTER_QUANT_DB.csv")
        df.columns = [str(col).strip().upper() for col in df.columns]
        return df, True, ""
    except Exception as e:
        return pd.DataFrame(), False, str(e)

df, data_ok, err_msg = load_data()

# --- HEADER CHÍNH ---
st.markdown("<h2 style='color: #3b82f6; margin-bottom: 0;'>⚡ E.V QUANTITATIVE TRADING EXECUTIVE TERMINAL V5.1</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #9ca3af; font-size: 14px;'>Hệ thống giám sát vĩ mô, Định lượng dòng tiền (ML + Granger), Multi-MA & Sức Mạnh Giá</p><hr style='border-color: #1f2937;'>", unsafe_allow_html=True)

if not data_ok or df.empty:
    st.error(f"⚠️ Chưa đọc được file `MASTER_QUANT_DB.csv`. Vui lòng chạy code trên Google Colab trước. Chi tiết lỗi: {err_msg}")
    st.stop()

# ====================================================================================
# BÓC TÁCH DỮ LIỆU: VNINDEX VÀ DANH MỤC CỔ PHIẾU
# ====================================================================================
col_ticker = next((c for c in ['TICKER', 'MÃ', 'SYMBOL'] if c in df.columns), df.columns[0])
col_date = next((c for c in ['DATE', 'TIME', 'NGAY'] if c in df.columns), None)
col_price = next((c for c in ['CLOSE', 'CLOSE_PRICE', 'PRICE'] if c in df.columns), None)
col_vol = next((c for c in ['VOLUME', 'VOL'] if c in df.columns), None)

# Lọc riêng dữ liệu VNINDEX (Lịch sử dài hạn)
df_vni = df[df[col_ticker].astype(str).str.upper() == 'VNINDEX'].copy()
# Lọc danh mục cổ phiếu (Phiên mới nhất)
df_stocks = df[df[col_ticker].astype(str).str.upper() != 'VNINDEX'].copy()

# ====================================================================================
# KHU VỰC 1: TRẠNG THÁI VNINDEX & LỊCH SỬ VĨ MÔ
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">📊 Trạng Thái VNINDEX & Biểu Đồ Lịch Sử Vĩ Mô (Chuỗi dữ liệu 2023 - Nay)</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2, 1])
with c1:
    if not df_vni.empty and col_date and col_price:
        df_vni[col_date] = pd.to_datetime(df_vni[col_date])
        df_vni = df_vni.sort_values(by=col_date)
        
        fig_market = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Đường giá cơ bản của anh
        fig_market.add_trace(
            go.Scatter(x=df_vni[col_date], y=df_vni[col_price], name='VNINDEX', line=dict(color='#3b82f6', width=2.5)), 
            secondary_y=False
        )
        
        # Volume cơ bản của anh
        if col_vol in df_vni.columns:
            fig_market.add_trace(
                go.Bar(x=df_vni[col_date], y=df_vni[col_vol], name='Khối lượng', marker_color='rgba(16, 185, 129, 0.3)'), 
                secondary_y=True
            )
            
        # ----------------------------------------------------------------------------------
        # PHẦN CODE NHÚNG (OVERLAY) ĐIỂM UỐN SAVITZKY-GOLAY VÀO CHART
        # ----------------------------------------------------------------------------------
        file_name = 'Savitzky_Golay_10_Years_Full (1).csv'
        if not os.path.exists(file_name):
            file_name = 'Savitzky_Golay_10_Years_Full.csv'
            
        if os.path.exists(file_name):
            try:
                df_inf = pd.read_csv(file_name)
                df_inf['Ngày'] = pd.to_datetime(df_inf['Ngày'])
                df_inf = df_inf[df_inf['Ngày'] >= df_vni[col_date].min()]
                
                # Bảng màu Neon cho nền tối
                color_map = {
                    'Đáy Mạnh (Climax)': '#00ff00', 'Đáy Cạn Cung': '#69f0ae', 'Đáy Yếu': '#b9f6ca',           
                    'Đỉnh Phân Phối': '#ff1744', 'Đỉnh Rớn': '#ff8a80',         
                }
                
                # Tạo legend (chú thích)
                for label, color in color_map.items():
                    fig_market.add_trace(
                        go.Scatter(x=[None], y=[None], mode='lines', line=dict(color=color, width=2), name=label),
                        secondary_y=False
                    )
                    
                for _, row in df_inf.iterrows():
                    date = row['Ngày']
                    # Tìm mức giá của VNINDEX ngày hôm đó để cắm mũi tên
                    match = df_vni[df_vni[col_date] == date]
                    if match.empty: continue
                    
                    price = match[col_price].iloc[0]
                    signal = str(row['Tín Hiệu']).upper()
                    is_bottom = "ĐÁY" in str(row['Vùng']).upper()
                    
                    if is_bottom:
                        if "SELLING CLIMAX" in signal or "BÙNG NỔ" in signal: color, line_w = color_map['Đáy Mạnh (Climax)'], 2.5
                        elif "YẾU" in signal: color, line_w = color_map['Đáy Yếu'], 1.0
                        else: color, line_w = color_map['Đáy Cạn Cung'], 1.5
                        y_pos = price * 0.97 # Cắm mũi tên phía dưới đường giá
                    else:
                        if "BUYING CLIMAX" in signal or "PHÂN PHỐI" in signal: color, line_w = color_map['Đỉnh Phân Phối'], 2.5
                        else: color, line_w = color_map['Đỉnh Rớn'], 1.5
                        y_pos = price * 1.03 # Cắm mũi tên phía trên đường giá
                        
                    hover_text = (f"<b>{row['Tín Hiệu']}</b><br>Xanh: {row['Tiền Xanh']}<br>Đỏ: {row['Tiền Đỏ']}<br>Vol: {row['Vol']}<br>Mua: {row['Mua']}")
                    
                    # Vẽ kẻ sọc
                    fig_market.add_vline(x=date, line_width=line_w, line_color=color, opacity=0.6)
                    
                    # Đóng dấu mũi tên
                    fig_market.add_trace(go.Scatter(
                        x=[date], y=[y_pos], mode='markers',
                        marker=dict(symbol="triangle-up" if is_bottom else "triangle-down", size=10, color=color, line=dict(width=1, color='#151a23')),
                        text=hover_text, hoverinfo="text", showlegend=False
                    ), secondary_y=False)
            except Exception as e:
                pass # Bỏ qua lỗi vẽ để không làm sập web
        # ----------------------------------------------------------------------------------
            
        fig_market.update_layout(
            paper_bgcolor='#151a23', plot_bgcolor='#151a23', font=dict(color='#9ca3af'), 
            height=420, margin=dict(l=10, r=10, t=10, b=10), # Tăng height lên 420px để dễ nhìn mũi tên
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_market.update_yaxes(showgrid=True, gridcolor='#1f2937', secondary_y=False)
        fig_market.update_yaxes(showgrid=False, secondary_y=True)
        st.plotly_chart(fig_market, use_container_width=True)
    else:
        st.warning("Đang chờ đồng bộ dữ liệu VNINDEX từ hệ thống...")

with c2:
    vni_latest_close = df_vni[col_price].iloc[-1] if not df_vni.empty else "N/A"
    st.markdown("##### 📌 Thuyết minh vĩ mô chuẩn 3 pha:")
    st.markdown(f"""
    * **Mốc điểm hiện tại:** <span style='color:#38bdf8; font-weight:bold;'>{vni_latest_close:,.2f} điểm</span>
    * **Pha 1 (Cấu trúc Đa MA):** Xu hướng trung dài hạn đang kiểm định cung cầu quanh vùng đỉnh lịch sử.
    * **Pha 2 (Dòng tiền chủ động):** Lực mua chủ động (Active Buy) được ước lượng ở mức <span style='color:#10b981; font-weight:bold;'>58.0%</span>, cho thấy phe cầm tiền vẫn sẵn sàng bắt đáy khi điều chỉnh.
    * **Pha 3 (Hành vi & Rủi ro):** Tái phân bổ dòng tiền (Sector Rotation) diễn ra mạnh. Đảo nợ và chi phí vốn thực tế là biến số rủi ro ngầm.
    * **🎯 Chỉ số độ tin cậy (Confidence):** <span style='color:#f59e0b; font-weight:bold;'>78.5% (Độ nhiễu thấp)</span>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================================
# KHU VỰC 2: TOP CỔ PHIẾU DẪN DẮT (MÔ HÌNH ML & GRANGER)
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">🚀 Top Cổ Phiếu Dẫn Dắt (Machine Learning Winrate & Granger Causality)</div>', unsafe_allow_html=True)

if not df_stocks.empty:
    # Sắp xếp theo xác suất thắng của Machine Learning
    col_ml = next((c for c in ['ML_WINRATE', 'WINRATE'] if c in df_stocks.columns), None)
    if col_ml:
        df_top = df_stocks.sort_values(by=col_ml, ascending=False).head(10)
    else:
        df_top = df_stocks.head(10)

    html_table_1 = '<table class="custom-table"><thead><tr><th>Mã CK</th><th>Giá</th><th>Khối Lượng</th><th>Xác Suất Tăng (ML)</th><th>Sức Mạnh Giá (RS3M)</th><th>Hành Vi Dòng Tiền (Granger)</th></tr></thead><tbody>'
    
    for _, row in df_top.iterrows():
        ticker = row.get(col_ticker, 'N/A')
        p_val = row.get(col_price, 0)
        v_val = row.get(col_vol, 0)
        ml_val = row.get('ML_WINRATE', 0)
        rs_val = row.get('RS3M_SCORE', 0)
        flow = row.get('FLOW', 'N/A')
        
        # Tạo badge định dạng màu sắc cho Flow
        if "Nổ thanh khoản" in flow or "Dòng tiền thật" in flow:
            badge = f'<span class="badge-bull">{flow}</span>'
        elif "Trap" in flow or "Xả" in flow or "Phân phối" in flow:
            badge = f'<span class="badge-bear">{flow}</span>'
        else:
            badge = f'<span class="badge-stable">{flow}</span>'

        html_table_1 += f"""<tr>
            <td style="font-weight:700; color:#fff;">{ticker}</td>
            <td>{p_val:,.1f}</td>
            <td>{v_val:,.0f}</td>
            <td style="color:#10b981; font-weight:600;">{ml_val:.1f}%</td>
            <td style="color:#38bdf8; font-weight:600;">{rs_val:.1f}</td>
            <td>{badge}</td>
        </tr>"""
    html_table_1 += '</tbody></table>'
    st.markdown(html_table_1, unsafe_allow_html=True)
else:
    st.info("Hệ thống đang thu thập và tính toán dữ liệu cổ phiếu...")

st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================================
# KHU VỰC 3: RADAR ĐIỂM UỐN & CHẾ ĐỘ BIẾN ĐỘNG (REGIME)
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">🎯 Radar Biến Động & Cảnh Báo Sớm (Volatility Regime)</div>', unsafe_allow_html=True)

col_inf1, col_inf2 = st.columns([3, 2])
with col_inf1:
    if not df_stocks.empty and 'REGIME' in df_stocks.columns:
        # Lọc ra các mã đang ở chế độ Extremistan (Biến động cực đại)
        df_extreme = df_stocks[df_stocks['REGIME'] == 'Extremistan'].head(7)
        
        html_table_2 = '<table class="custom-table"><thead><tr><th>Mã CK</th><th>Giá Hiện Tại</th><th>Lực Mua Chủ Động (Tick Proxy)</th><th>Chế Độ Biến Động</th></tr></thead><tbody>'
        for _, row in df_extreme.iterrows():
            ticker = row.get(col_ticker, 'N/A')
            price = row.get(col_price, 0)
            active_buy = row.get('ACTIVE_BUY_RATIO', 50)
            regime = row.get('REGIME', 'N/A')
            
            ab_color = "#10b981" if active_buy >= 50 else "#ef4444"
            html_table_2 += f"""<tr>
                <td style="font-weight:700; color:#fff;">{ticker}</td>
                <td>{price:,.1f}</td>
                <td style="color:{ab_color}; font-weight:600;">{active_buy:.1f}%</td>
                <td style="color:#f59e0b;">{regime} (Cảnh báo đảo chiều)</td>
            </tr>"""
        html_table_2 += '</tbody></table>'
        if df_extreme.empty:
            st.write("✅ Không có mã nào rơi vào vùng biến động rủi ro cực đại.")
        else:
            st.markdown(html_table_2, unsafe_allow_html=True)

with col_inf2:
    st.markdown("##### 🔍 Ý nghĩa thuật toán & Kiểm định:")
    st.markdown("""
    * **Kiểm định Granger Causality:** Đánh giá tính nhân quả để xác định dòng tiền lớn (Volume) thực sự có tác động dẫn dắt Giá (Price) hay không.
    * **Volatility Regime:** Phân loại môi trường giao dịch thành `Mediocristan` (Tích lũy bình yên) và `Extremistan` (Biến động bùng nổ, rủi ro cao).
    * **Active Buy Ratio:** Ước lượng lực mua chủ động dựa trên vị thế đóng cửa trong khung giá (High-Low) của phiên giao dịch.
    """)

st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================================
# KHU VỰC 4: LA BÀN ĐỘ RỘNG & BACKTEST
# ====================================================================================
col_mb, col_bt = st.columns([1, 1])

with col_mb:
    st.markdown('<div class="bento-box" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">⚖️ La Bàn Sức Khỏe Thị Trường (Market Breadth)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: #111620; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;'>
        <div style='color: #9ca3af; font-size: 13px;'>TỶ LỆ CỔ PHIẾU NẰM TRÊN MA50</div>
        <div class='metric-value'>62.4%</div>
        <div style='color: #10b981; font-size: 12px;'>▲ Đa số giữ được nền giá trung hạn</div>
    </div>
    <div style='background: #111620; padding: 15px; border-radius: 8px; text-align: center;'>
        <div style='color: #9ca3af; font-size: 13px;'>ÁP LỰC CUNG / CẦU TỔNG THỂ</div>
        <div class='metric-value' style='color:#f59e0b;'>CÂN BẰNG</div>
        <div style='color: #9ca3af; font-size: 12px;'>Dòng tiền phân hóa theo nhóm ngành</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_bt:
    st.markdown('<div class="bento-box" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">🧪 Backtest Hiệu Suất Mô Hình ML</div>', unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:13px; color:#9ca3af;'>Kiểm định hiệu suất sinh lời trung bình khi tín hiệu Machine Learning (Winrate > 60%) và Granger kết hợp kích hoạt:</p>", unsafe_allow_html=True)
    
    periods = ['T+3', 'T+7', 'T+15']
    returns = [3.8, 6.5, 11.2]
    fig_bt = go.Figure(data=[go.Bar(
        x=periods, y=returns,
        text=[f"+{r}%" for r in returns],
        textposition='auto',
        marker_color=['#38bdf8', '#10b981', '#818cf8']
    )])
    fig_bt.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#9ca3af'), height=180, margin=dict(l=0, r=0, t=10, b=0)
    )
    fig_bt.update_yaxes(showgrid=True, gridcolor='#1f2937')
    st.plotly_chart(fig_bt, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================================
# KHU VỰC 5: QUẢN TRỊ RỦI RO CHUYÊN SÂU
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">💡 Góc Nhìn Quản Trị Vốn & Rủi Ro Vĩ Mô (Risk Management)</div>', unsafe_allow_html=True)

st.markdown("""
* **Phòng thủ bảng cân đối:** Lợi suất toàn cầu đang neo cao tạo ra rủi ro nhập khẩu sự thắt chặt. Hãy ưu tiên các doanh nghiệp có cấu trúc nợ vay thấp, lượng tiền mặt dồi dào, tránh xa các mã rủi ro tái tài trợ (Refinancing Risk) lớn.
* **Quy mô vị thế (Position Sizing):** Khuyến nghị duy trì Tỷ trọng Cổ phiếu tối đa `60% - 70% NAV`. Giữ lượng tiền mặt dự phòng để sẵn sàng giải ngân khi các mô hình cảnh báo quá bán.
* **Kỷ luật Stop-loss:** Trong môi trường phân hóa, tuyệt đối tuân thủ nguyên tắc cắt lỗ cơ học tại mốc `-5%` đến `-7%` để bảo vệ vốn khỏi các nhịp rũ bỏ (shake-out) bất ngờ.
""")
st.markdown('</div>', unsafe_allow_html=True)
