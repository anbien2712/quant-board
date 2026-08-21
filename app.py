import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# --- CẤU HÌNH TRANG WIDE MODE ---
st.set_page_config(page_title="E.V Quant Executive Terminal V5.2", layout="wide", initial_sidebar_state="collapsed")

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
    .badge-bull { background-color: rgba(16, 185, 129, 0.15); color: #34d399; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-block; }
    .badge-bear { background-color: rgba(239, 68, 68, 0.15); color: #f87171; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-block; }
    .badge-stable { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-block; }
    .metric-value { color: #3b82f6; font-size: 24px; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# --- ĐỌC VÀ CHUẨN HÓA DỮ LIỆU AN TOÀN TUYỆT ĐỐI ---
@st.cache_data(ttl=300)
def load_data():
    try:
        if not os.path.exists("MASTER_QUANT_DB.csv"):
            return pd.DataFrame(), False, "Không tìm thấy file MASTER_QUANT_DB.csv trên hệ thống."
            
        df = pd.read_csv("MASTER_QUANT_DB.csv")
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        # Ép kiểu dữ liệu số cho các cột quan trọng để tránh lỗi nan%
        numeric_cols = ['CLOSE', 'CLOSE_PRICE', 'PRICE', 'VOLUME', 'VOL', 'HIGH', 'LOW', 'ACTIVE_BUY_RATIO', 'ML_WINRATE', 'RS3M_SCORE']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                
        return df, True, ""
    except Exception as e:
        return pd.DataFrame(), False, str(e)

df, data_ok, err_msg = load_data()

# --- HEADER CHÍNH ---
st.markdown("<h2 style='color: #3b82f6; margin-bottom: 0;'>QUANTITATIVE CHECKING SYSTEM</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #9ca3af; font-size: 14px;'>Beta version - Executive Terminal V5.2</p><hr style='border-color: #1f2937;'>", unsafe_allow_html=True)

if not data_ok or df.empty:
    st.error(f"⚠️ Chưa đọc được file dữ liệu. Chi tiết lỗi: {err_msg}")
    st.stop()

# --- BÓC TÁCH DỮ LIỆU ---
col_ticker = next((c for c in ['TICKER', 'MÃ', 'SYMBOL'] if c in df.columns), df.columns[0])
col_date = next((c for c in ['DATE', 'TIME', 'NGAY'] if c in df.columns), None)
col_price = next((c for c in ['CLOSE', 'CLOSE_PRICE', 'PRICE'] if c in df.columns), None)
col_vol = next((c for c in ['VOLUME', 'VOL'] if c in df.columns), None)

df_vni = df[df[col_ticker].astype(str).str.upper() == 'VNINDEX'].copy()
df_stocks = df[df[col_ticker].astype(str).str.upper() != 'VNINDEX'].copy()

# ====================================================================================
# KHU VỰC 1: TRẠNG THÁI VNINDEX & ACTIVE FLOW
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">MACHINE LEARNING & MARKET FLOW</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2, 1])

with c1:
    if not df_vni.empty and col_date and col_price:
        df_vni[col_date] = pd.to_datetime(df_vni[col_date], errors='coerce')
        df_vni = df_vni.sort_values(by=col_date).dropna(subset=[col_date])
        
        fig_market = make_subplots(specs=[[{"secondary_y": True}]])
        fig_market.add_trace(go.Scatter(x=df_vni[col_date], y=df_vni[col_price], name='VNINDEX', line=dict(color='#3b82f6', width=2.5)), secondary_y=False)
        
        if col_vol in df_vni.columns:
            fig_market.add_trace(go.Bar(x=df_vni[col_date], y=df_vni[col_vol], name='Khối lượng', marker_color='rgba(16, 185, 129, 0.3)'), secondary_y=True)
            
        # Overlays Savitzky-Golay (nếu có file)
        for fname in ['Savitzky_Golay_10_Years_Full (1).csv', 'Savitzky_Golay_10_Years_Full.csv']:
            if os.path.exists(fname):
                try:
                    df_inf = pd.read_csv(fname)
                    df_inf['Ngày'] = pd.to_datetime(df_inf['Ngày'])
                    df_inf = df_inf[df_inf['Ngày'] >= df_vni[col_date].min()]
                    for _, row in df_inf.iterrows():
                        fig_market.add_vline(x=row['Ngày'], line_width=1.5, line_color='#00ff00', opacity=0.4)
                except:
                    pass
                break

        fig_market.update_layout(
            paper_bgcolor='#151a23', plot_bgcolor='#151a23', font=dict(color='#9ca3af'), 
            height=420, margin=dict(l=10, r=10, t=10, b=10), 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white"))
        )
        fig_market.update_yaxes(showgrid=True, gridcolor='#1f2937', secondary_y=False)
        fig_market.update_yaxes(showgrid=False, secondary_y=True)
        st.plotly_chart(fig_market, use_container_width=True)
        
        # ACTIVE FLOW
        st.markdown("<div class='box-title' style='margin-top: 20px; font-size: 14px;'>ACTIVE FLOW (DÒNG TIỀN THỰC TẾ)</div>", unsafe_allow_html=True)
        col_high = next((c for c in ['HIGH', 'CAO'] if c in df_vni.columns), None)
        col_low = next((c for c in ['LOW', 'THAP'] if c in df_vni.columns), None)
        
        if 'ACTIVE_BUY_RATIO' in df_vni.columns:
            df_vni['Real_Active_Buy'] = df_vni['ACTIVE_BUY_RATIO']
            df_vni['Real_Active_Sell'] = 100 - df_vni['ACTIVE_BUY_RATIO']
        elif col_high and col_low:
            df_vni['Real_Active_Buy'] = ((df_vni[col_price] - df_vni[col_low]) / (df_vni[col_high] - df_vni[col_low] + 1e-9)) * 100
            df_vni['Real_Active_Sell'] = 100 - df_vni['Real_Active_Buy']
        else:
            df_vni['Real_Active_Buy'] = 50.0
            df_vni['Real_Active_Sell'] = 50.0
            
        df_vni['Buy_MA'] = df_vni['Real_Active_Buy'].rolling(10).mean()
        df_vni['Sell_MA'] = df_vni['Real_Active_Sell'].rolling(10).mean()
        df_flow_data = df_vni.tail(150)
        
        fig_flow = go.Figure()
        fig_flow.add_trace(go.Bar(x=df_flow_data[col_date], y=df_flow_data['Real_Active_Buy'], marker_color='rgba(16, 185, 129, 0.5)', name='Lực Mua (Phiên)', marker_line_width=0))
        fig_flow.add_trace(go.Bar(x=df_flow_data[col_date], y=df_flow_data['Real_Active_Sell'], marker_color='rgba(239, 68, 68, 0.5)', name='Lực Bán (Phiên)', marker_line_width=0))
        fig_flow.add_trace(go.Scatter(x=df_flow_data[col_date], y=df_flow_data['Buy_MA'], mode='lines', line=dict(color='#10b981', width=2), name='Trend Mua (MA10)'))
        fig_flow.add_trace(go.Scatter(x=df_flow_data[col_date], y=df_flow_data['Sell_MA'], mode='lines', line=dict(color='#ef4444', width=2), name='Trend Bán (MA10)'))
        
        fig_flow.update_layout(
            barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#9ca3af', size=11),
            height=250, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#d1d5db", size=11)),
            hovermode="x unified"
        )
        fig_flow.update_xaxes(showgrid=False, zeroline=False)
        fig_flow.update_yaxes(showgrid=True, gridcolor='#1f2937', zeroline=False, range=[0, 100])
        st.plotly_chart(fig_flow, use_container_width=True)
    else:
        st.warning("Đang chờ đồng bộ dữ liệu VNINDEX từ hệ thống...")

with c2:
    vni_latest_close, vni_latest_date = "N/A", "N/A"
    if not df_vni.empty and col_price in df_vni.columns and col_date in df_vni.columns:
        vni_latest_close = df_vni[col_price].iloc[-1]
        vni_latest_date = df_vni[col_date].iloc[-1].strftime('%d/%m/%Y')
        vni_str = f"{vni_latest_close:,.2f}" if pd.notnull(vni_latest_close) else "N/A"
    else:
        vni_str = "N/A"

    df_vni['Daily_Return'] = df_vni[col_price].pct_change() * 100
    returns_clean = df_vni['Daily_Return'].dropna()
    
    stat_mean = returns_clean.mean() if not returns_clean.empty else 0.0
    stat_median = returns_clean.median() if not returns_clean.empty else 0.0
    stat_max = returns_clean.max() if not returns_clean.empty else 0.0
    stat_min = returns_clean.min() if not returns_clean.empty else 0.0
    stat_kurt = returns_clean.kurt() if not returns_clean.empty else 0.0
    
    regime = "Extremistan" if stat_kurt > 1.5 else "Mediocristan"
    regime_color = "#ef4444" if regime == "Extremistan" else "#10b981"

    st.markdown(f"<div style='color: #f3f4f6; font-size: 15px; font-weight: 700; text-transform: uppercase;'>MARKET OVERVIEW - {vni_latest_date}</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='quant-price-box' style='display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #2d3748; padding-bottom: 8px; margin-bottom: 20px;'>
        <span style='color: #9ca3af; font-size: 12px;'>CURRENT INDEX (VNINDEX)</span>
        <span style='color: #38bdf8; font-size: 24px; font-weight: 800;'>{vni_str}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='color: #9ca3af; font-size: 11px; font-weight: 700; text-transform: uppercase; border-left: 3px solid #3b82f6; padding-left: 8px; margin-bottom: 8px;'>Return Distribution Metrics</div>
    <table class='custom-table' style='font-family: monospace;'>
        <tr><td>Mean</td><td><b>{stat_mean:.2f}%</b></td><td>Max</td><td style='color:#10b981;'><b>{stat_max:.2f}%</b></td></tr>
        <tr><td>Median</td><td><b>{stat_median:.2f}%</b></td><td>Min</td><td style='color:#ef4444;'><b>{stat_min:.2f}%</b></td></tr>
        <tr><td>Kurtosis</td><td><b>{stat_kurt:.2f}</b></td><td>Regime</td><td style='color:{regime_color};'><b>{regime}</b></td></tr>
    </table>
    """, unsafe_allow_html=True)

    # Histogram
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=returns_clean, nbinsx=50, marker_color='rgba(56, 189, 248, 0.7)', marker_line=dict(color='#38bdf8', width=1)))
    fig_hist.add_vline(x=0, line_width=1.5, line_dash="dot", line_color="#ef4444")
    fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#9ca3af', size=11), height=350, margin=dict(l=0, r=0, t=10, b=0), showlegend=False, bargap=0.1)
    fig_hist.update_xaxes(showgrid=False, zeroline=False)
    fig_hist.update_yaxes(showgrid=True, gridcolor='#1f2937', zeroline=False)
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================================
# KHU VỰC 2: TOP CỔ PHIẾU DẪN DẮT (LẤY DỮ LIỆU TỪ SNAPSHOT CỔ PHIẾU)
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">TOP PICK BY ML & GRANGER</div>', unsafe_allow_html=True)

if not df_stocks.empty:
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
        
        if "Nổ thanh khoản" in str(flow) or "Dòng tiền thật" in str(flow):
            badge = f'<span class="badge-bull">{flow}</span>'
        elif "Trap" in str(flow) or "Xả" in str(flow) or "Phân phối" in str(flow):
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
# KHU VỰC 3: VOLATILITY REGIME
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">VOLATILITY REGIME</div>', unsafe_allow_html=True)

col_inf1, col_inf2 = st.columns([3, 2])
with col_inf1:
    if not df_stocks.empty and 'REGIME' in df_stocks.columns:
        df_extreme = df_stocks[df_stocks['REGIME'] == 'Extremistan'].head(7)
        
        html_table_2 = '<table class="custom-table"><thead><tr><th>Mã CK</th><th>Giá Hiện Tại</th><th style="color: #38bdf8;">ACTIVE BUY RATIO</th><th>Chế Độ Biến Động</th></tr></thead><tbody>'
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
                <td style="color:#f59e0b;">{regime}</td>
            </tr>"""
        html_table_2 += '</tbody></table>'
        if df_extreme.empty:
            st.write("✅ Không có mã nào rơi vào vùng biến động rủi ro cực đại.")
        else:
            st.markdown(html_table_2, unsafe_allow_html=True)
    else:
        st.write("Đang chờ đồng bộ dữ liệu Regime...")

with col_inf2:
    st.markdown("##### 🔍 Ý nghĩa thuật toán & Kiểm định:")
    st.markdown("""
    * **Kiểm định Granger Causality:** Đánh giá tính nhân quả giữa Volume và Price.
    * **Volatility Regime:** Phân loại môi trường `Mediocristan` và `Extremistan`.
    * **Active Buy Ratio:** Đo lường lực mua/bán chủ động từ dữ liệu khớp lệnh thực tế.
    """)

st.markdown('</div>', unsafe_allow_html=True)
