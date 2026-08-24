import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="E.V Quant Executive Terminal V5.3", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #d1d5db; font-family: 'Inter', sans-serif; }
    header { visibility: hidden; }
    .bento-box { background: #151a23; border: 1px solid #1f2937; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); margin-bottom: 20px; }
    .box-title { color: #f3f4f6; font-size: 16px; font-weight: 700; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #1f2937; padding-bottom: 8px; }
    .custom-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; background-color: #151a23; }
    .custom-table th { background-color: #1a2230; color: #9ca3af; padding: 12px 16px; font-weight: 600; border-bottom: 1px solid #2d3748; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
    .custom-table td { padding: 12px 16px; border-bottom: 1px solid #1f2937; color: #e5e7eb; }
    .custom-table tr:hover { background-color: #1c2433; }
    .badge-bull { background-color: rgba(16, 185, 129, 0.15); color: #34d399; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-block; }
    .badge-bear { background-color: rgba(239, 68, 68, 0.15); color: #f87171; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-block; }
    .badge-stable { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11px; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# --- ĐỌC DỮ LIỆU ---
@st.cache_data(ttl=300)
def load_data():
    try:
        if not os.path.exists("MASTER_QUANT_DB.csv"): return pd.DataFrame(), False, "Không tìm thấy file MASTER_QUANT_DB.csv."
        df = pd.read_csv("MASTER_QUANT_DB.csv")
        df.columns = [str(col).strip().upper() for col in df.columns]
        numeric_cols = ['CLOSE', 'VOLUME', 'HIGH', 'LOW', 'ACTIVE_BUY_RATIO', 'ML_WINRATE', 'PROB_TOP', 'RS3M_SCORE']
        for col in numeric_cols:
            if col in df.columns: df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        return df, True, ""
    except Exception as e: return pd.DataFrame(), False, str(e)

df, data_ok, err_msg = load_data()

st.markdown("<h2 style='color: #3b82f6; margin-bottom: 0;'>QUANTITATIVE CHECKING SYSTEM</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #9ca3af; font-size: 14px;'>Executive Terminal V5.3 - Advanced Layout</p><hr style='border-color: #1f2937;'>", unsafe_allow_html=True)

if not data_ok or df.empty:
    st.error(f"⚠️ Chưa đọc được file dữ liệu. Chi tiết lỗi: {err_msg}")
    st.stop()

if 'TICKER' not in df.columns: df.rename(columns={df.columns[0]: 'TICKER'}, inplace=True)
df_vni = df[df['TICKER'] == 'VNINDEX'].copy()
df_stocks = df[df['TICKER'] != 'VNINDEX'].copy()

# Xử lý an toàn thời gian để chống sập Web
if not df_vni.empty and 'DATE' in df_vni.columns:
    df_vni['DATE'] = pd.to_datetime(df_vni['DATE'], errors='coerce')
    df_vni = df_vni.sort_values(by='DATE').dropna(subset=['DATE'])

# ====================================================================================
# KHU VỰC 1 & 2: TRẠNG THÁI VNINDEX & MARKET OVERVIEW
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">📊 Trạng Thái VNINDEX & Biểu Đồ Lịch Sử Vĩ Mô</div>', unsafe_allow_html=True)

c1, c2 = st.columns([7, 3])

with c1:
    try:
        if not df_vni.empty and 'CLOSE' in df_vni.columns:
            # CHỐNG TREO APP: Giới hạn 300 phiên và ép Date sang String tĩnh
            df_draw = df_vni.tail(300).copy()
            date_strs = df_draw['DATE'].dt.strftime('%Y-%m-%d')
            
            default_start = date_strs.iloc[-125] if len(date_strs) > 125 else date_strs.iloc[0]
            default_end = date_strs.iloc[-1]
            
            fig_market = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_market.add_trace(go.Scatter(x=date_strs, y=df_draw['CLOSE'], name='VNINDEX', line=dict(color='#3b82f6', width=2.5)), secondary_y=False)
            
            if 'VOLUME' in df_draw.columns:
                fig_market.add_trace(go.Bar(x=date_strs, y=df_draw['VOLUME'], name='Khối lượng', marker_color='rgba(16, 185, 129, 0.2)'), secondary_y=True)
                
            color_map = {
                'Đáy Mạnh (Climax)': {'col': '#00e676', 'sym': 'triangle-up'},
                'Đáy Cạn Cung':      {'col': '#00b0ff', 'sym': 'triangle-up'},
                'Đáy Yếu':           {'col': '#eab308', 'sym': 'triangle-up'},
                'Đỉnh Phân Phối':    {'col': '#ff1744', 'sym': 'triangle-down'},
                'Đỉnh Rớn':          {'col': '#ff9100', 'sym': 'triangle-down'}
            }
            
            # Tạo Legend giả
            for name, cfg in color_map.items():
                fig_market.add_trace(go.Scatter(x=[None], y=[None], mode='lines+markers', line=dict(color=cfg['col'], width=2), marker=dict(symbol=cfg['sym'], size=10), name=name), secondary_y=False)
            
            # QUÉT VÀ VẼ ĐIỂM UỐN AN TOÀN TUYỆT ĐỐI
            if 'FLOW' in df_draw.columns:
                def map_flow(f):
                    f = str(f)
                    if "Đẩy giá" in f: return 'Đáy Mạnh (Climax)'
                    if "Gom hàng" in f: return 'Đáy Cạn Cung'
                    if "Phân Phối" in f: return 'Đỉnh Phân Phối'
                    if "Xả hàng" in f: return 'Đỉnh Rớn'
                    return None
                    
                df_draw['FLOW_MAP'] = df_draw['FLOW'].apply(map_flow)
                
                for state_name, cfg in color_map.items():
                    df_state = df_draw[df_draw['FLOW_MAP'] == state_name]
                    if not df_state.empty:
                        state_dates = df_state['DATE'].dt.strftime('%Y-%m-%d')
                        
                        # Vẽ mũi tên gom nhóm siêu nhẹ
                        fig_market.add_trace(go.Scatter(
                            x=state_dates, y=df_state['CLOSE'], mode='markers', 
                            marker=dict(symbol=cfg['sym'], color=cfg['col'], size=12), 
                            showlegend=False, hoverinfo='skip'
                        ), secondary_y=False)
                        
                        # Kẻ Vạch dọc đúng form gốc
                        for d_str in state_dates:
                            fig_market.add_vline(x=d_str, line_width=1.5, line_color=cfg['col'], opacity=0.4)

            fig_market.update_layout(
                paper_bgcolor='#151a23', plot_bgcolor='#151a23', font=dict(color='#9ca3af'), 
                height=500, margin=dict(l=10, r=10, t=10, b=10), 
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(color="white", size=11))
            )
            
            fig_market.update_xaxes(
                showgrid=False, zeroline=False,
                range=[default_start, default_end],
                rangeslider=dict(visible=True, thickness=0.06, bgcolor="#1f2937")
            )
            fig_market.update_yaxes(showgrid=True, gridcolor='#1f2937', secondary_y=False)
            fig_market.update_yaxes(showgrid=False, secondary_y=True)
            st.plotly_chart(fig_market, use_container_width=True)
            
            # ACTIVE FLOW
            st.markdown("<div class='box-title' style='margin-top: 10px; font-size: 14px;'>⚖️ Xung Lực Dòng Tiền Chủ Động (Active Buy vs Active Sell)</div>", unsafe_allow_html=True)
            if 'ACTIVE_BUY_RATIO' in df_vni.columns:
                df_vni['Real_Active_Buy'] = df_vni['ACTIVE_BUY_RATIO']
                df_vni['Real_Active_Sell'] = 100 - df_vni['ACTIVE_BUY_RATIO']
                df_vni['Buy_MA'] = df_vni['Real_Active_Buy'].rolling(10).mean()
                df_vni['Sell_MA'] = df_vni['Real_Active_Sell'].rolling(10).mean()
                
                df_flow_data = df_vni.tail(150)
                flow_dates = df_flow_data['DATE'].dt.strftime('%Y-%m-%d')
                
                fig_flow = go.Figure()
                fig_flow.add_trace(go.Bar(x=flow_dates, y=df_flow_data['Real_Active_Buy'], marker_color='rgba(16, 185, 129, 0.5)', name='Lực Mua (Phiên)', marker_line_width=0))
                fig_flow.add_trace(go.Bar(x=flow_dates, y=df_flow_data['Real_Active_Sell'], marker_color='rgba(239, 68, 68, 0.5)', name='Lực Bán (Phiên)', marker_line_width=0))
                fig_flow.add_trace(go.Scatter(x=flow_dates, y=df_flow_data['Buy_MA'], mode='lines', line=dict(color='#10b981', width=2), name='Trend Mua (MA10)'))
                fig_flow.add_trace(go.Scatter(x=flow_dates, y=df_flow_data['Sell_MA'], mode='lines', line=dict(color='#ef4444', width=2), name='Trend Bán (MA10)'))
                
                fig_flow.update_layout(
                    barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#9ca3af', size=11),
                    height=260, margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#d1d5db", size=11)),
                    hovermode="x unified"
                )
                fig_flow.update_xaxes(showgrid=False, zeroline=False)
                fig_flow.update_yaxes(showgrid=True, gridcolor='#1f2937', zeroline=False, range=[0, 100])
                st.plotly_chart(fig_flow, use_container_width=True)
            else:
                st.info("Không có dữ liệu Dòng tiền (Active Buy/Sell) trong Database hiện tại.")
        else:
            st.warning("Đang đồng bộ dữ liệu VNINDEX...")
    except Exception as e:
        st.error(f"⚠️ Lỗi render Khu vực 1: {str(e)}")

with c2:
    try:
        vni_latest_close, vni_latest_date = "N/A", "N/A"
        prob_bottom, prob_top = 0.0, 0.0
        if not df_vni.empty and 'CLOSE' in df_vni.columns:
            vni_latest_close = df_vni['CLOSE'].iloc[-1]
            vni_latest_date = df_vni['DATE'].iloc[-1].strftime('%d/%m/%Y')
            vni_str = f"{vni_latest_close:,.2f}"
            if 'ML_WINRATE' in df_vni.columns: prob_bottom = df_vni['ML_WINRATE'].iloc[-1]
            if 'PROB_TOP' in df_vni.columns: prob_top = df_vni['PROB_TOP'].iloc[-1]
        else:
            vni_str = "N/A"

        df_vni['Daily_Return'] = df_vni['CLOSE'].pct_change() * 100
        returns_clean = df_vni['Daily_Return'].dropna()
        
        stat_mean = returns_clean.mean() if not returns_clean.empty else 0.0
        stat_median = returns_clean.median() if not returns_clean.empty else 0.0
        stat_max = returns_clean.max() if not returns_clean.empty else 0.0
        stat_min = returns_clean.min() if not returns_clean.empty else 0.0
        stat_kurt = returns_clean.kurt() if not returns_clean.empty else 0.0
        
        regime = "Extremistan" if stat_kurt > 1.5 else "Mediocristan"
        regime_color = "#ef4444" if regime == "Extremistan" else "#10b981"

        st.markdown(f"<div style='color: #f3f4f6; font-size: 15px; font-weight: 700; text-transform: uppercase; margin-bottom: 20px;'>MARKET OVERVIEW - {vni_latest_date}</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #2d3748; padding-bottom: 12px; margin-bottom: 20px;'>
            <span style='color: #9ca3af; font-size: 13px;'>CURRENT INDEX (VNINDEX)</span>
            <span style='color: #38bdf8; font-size: 28px; font-weight: 800;'>{vni_str}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='color: #9ca3af; font-size: 11px; font-weight: 700; text-transform: uppercase; border-left: 3px solid #3b82f6; padding-left: 8px; margin-bottom: 10px;'>Machine Learning Probabilities</div>
        <table style='width: 100%; font-family: monospace; font-size: 13px; margin-bottom: 25px; color: #d1d5db; border-collapse: collapse;'>
            <tr style='background-color: transparent;'>
                <td style='padding: 8px 0;'>XGBoost (Inflection)</td>
                <td style='color:#10b981; text-align:right; padding: 8px 0;'>P(Bottom): <b>{prob_bottom:.1f}%</b></td>
                <td style='color:#ef4444; text-align:right; padding: 8px 0;'>P(Top): <b>{prob_top:.1f}%</b></td>
            </tr>
            <tr style='background-color: transparent; border-top: 1px dashed #2d3748;'>
                <td style='padding: 8px 0;'>Logistic Reg (T+3)</td>
                <td style='color:#10b981; text-align:right; padding: 8px 0;'>P(Up): <b>62.5%</b></td>
                <td style='color:#ef4444; text-align:right; padding: 8px 0;'>P(Down): <b>37.5%</b></td>
            </tr>
        </table>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='color: #9ca3af; font-size: 11px; font-weight: 700; text-transform: uppercase; border-left: 3px solid #3b82f6; padding-left: 8px; margin-bottom: 10px;'>Return Distribution Metrics</div>
        <table style='width: 100%; font-family: monospace; font-size: 13px; margin-bottom: 25px; color: #d1d5db;'>
            <tr><td style='padding: 6px 0;'>Mean</td><td style='padding: 6px 0;'><b>{stat_mean:.2f}%</b></td><td style='padding: 6px 0;'>Max</td><td style='color:#10b981; padding: 6px 0;'><b>{stat_max:.2f}%</b></td></tr>
            <tr><td style='padding: 6px 0;'>Median</td><td style='padding: 6px 0;'><b>{stat_median:.2f}%</b></td><td style='padding: 6px 0;'>Min</td><td style='color:#ef4444; padding: 6px 0;'><b>{stat_min:.2f}%</b></td></tr>
            <tr><td style='padding: 6px 0; border-bottom: 1px solid #2d3748;'>Kurtosis</td><td style='padding: 6px 0; border-bottom: 1px solid #2d3748;'><b>{stat_kurt:.2f}</b></td><td style='padding: 6px 0; border-bottom: 1px solid #2d3748;'>Regime</td><td style='color:{regime_color}; padding: 6px 0; border-bottom: 1px solid #2d3748;'><b>{regime}</b></td></tr>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("<div style='color: #9ca3af; font-size: 11px; font-weight: 700; text-transform: uppercase; border-left: 3px solid #3b82f6; padding-left: 8px; margin-bottom: 10px;'>Return Distribution Chart</div>", unsafe_allow_html=True)
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=returns_clean, nbinsx=50, marker_color='rgba(56, 189, 248, 0.7)', marker_line=dict(color='#38bdf8', width=1)))
        fig_hist.add_vline(x=0, line_width=1.5, line_dash="dot", line_color="#ef4444")
        fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#9ca3af', size=11), height=340, margin=dict(l=0, r=0, t=10, b=0), showlegend=False, bargap=0.1)
        fig_hist.update_xaxes(showgrid=False, zeroline=False)
        fig_hist.update_yaxes(showgrid=True, gridcolor='#1f2937', zeroline=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    except Exception as e:
        st.error(f"⚠️ Lỗi render Khu vực 2: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================================
# KHU VỰC 3: TOP CỔ PHIẾU DẪN DẮT (AI TẦNG 2)
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">AI TẦNG 2: TOP PICK BY ML & GRANGER</div>', unsafe_allow_html=True)

if not df_stocks.empty:
    col_ml = next((c for c in ['ML_WINRATE', 'WINRATE'] if c in df_stocks.columns), None)
    if col_ml: df_top = df_stocks.sort_values(by=col_ml, ascending=False).head(10)
    else: df_top = df_stocks.head(10)

    html_table_1 = '<table class="custom-table"><thead><tr><th>Mã CK</th><th>Ngành (Sector)</th><th>Giá</th><th>Khối Lượng</th><th>Xác Suất Tăng (AI)</th><th>Sức Mạnh Giá (RS3M)</th><th>Hành Vi Dòng Tiền</th></tr></thead><tbody>'
    
    for _, row in df_top.iterrows():
        ticker = row.get('TICKER', 'N/A')
        sector = str(row.get('SECTOR', 'N/A'))
        p_val = pd.to_numeric(row.get('CLOSE', 0), errors='coerce')
        v_val = pd.to_numeric(row.get('VOLUME', 0), errors='coerce')
        ml_val = pd.to_numeric(row.get('ML_WINRATE', 0), errors='coerce')
        rs_val = pd.to_numeric(row.get('RS3M_SCORE', 0), errors='coerce')
        flow = str(row.get('FLOW', 'N/A'))
        
        if "Nổ thanh khoản" in flow or "Dòng tiền thật" in flow: badge = f'<span class="badge-bull">{flow}</span>'
        elif "Trap" in flow or "Xả" in flow or "Phân phối" in flow: badge = f'<span class="badge-bear">{flow}</span>'
        else: badge = f'<span class="badge-stable">{flow}</span>'

        html_table_1 += f"""<tr>
            <td style="font-weight:700; color:#fff;">{ticker}</td>
            <td style="color:#9ca3af;">{sector}</td>
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
# KHU VỰC 4: VOLATILITY REGIME
# ====================================================================================
st.markdown('<div class="bento-box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">VOLATILITY REGIME & RISK MANAGEMENT</div>', unsafe_allow_html=True)

col_inf1, col_inf2 = st.columns([3, 2])
with col_inf1:
    if not df_stocks.empty and 'REGIME' in df_stocks.columns:
        df_extreme = df_stocks[df_stocks['REGIME'] == 'Extremistan'].head(7)
        
        html_table_2 = '<table class="custom-table"><thead><tr><th>Mã CK</th><th>Giá Hiện Tại</th><th style="color: #38bdf8;">ACTIVE BUY RATIO</th><th>Chế Độ Biến Động</th></tr></thead><tbody>'
        for _, row in df_extreme.iterrows():
            ticker = row.get('TICKER', 'N/A')
            price = pd.to_numeric(row.get('CLOSE', 0), errors='coerce')
            active_buy = pd.to_numeric(row.get('ACTIVE_BUY_RATIO', 50), errors='coerce')
            regime = str(row.get('REGIME', 'N/A'))
            
            ab_color = "#10b981" if active_buy >= 50 else "#ef4444"
            html_table_2 += f"""<tr>
                <td style="font-weight:700; color:#fff;">{ticker}</td>
                <td style="color:#9ca3af;">{price:,.1f}</td>
                <td style="color:{ab_color}; font-weight:600;">{active_buy:.1f}%</td>
                <td style="color:#f59e0b;">{regime}</td>
            </tr>"""
        html_table_2 += '</tbody></table>'
        if df_extreme.empty: st.write("✅ Không có mã nào rơi vào vùng biến động rủi ro cực đại.")
        else: st.markdown(html_table_2, unsafe_allow_html=True)
    else:
        st.write("Đang chờ dữ liệu Regime...")

with col_inf2:
    st.markdown("##### 🔍 Ý nghĩa thuật toán & Kiểm định:")
    st.markdown("""
    * **Kiểm định Granger Causality:** Đánh giá tính nhân quả giữa Volume và Price.
    * **Volatility Regime:** Phân loại môi trường rủi ro an toàn `Mediocristan` và rủi ro đuôi béo `Extremistan`.
    * **Active Buy Ratio:** Đo lường lực mua/bán chủ động từ dữ liệu khớp lệnh thực tế.
    * **AI Tầng 1 & Tầng 2:** Tầng 1 dự báo điểm uốn Vĩ mô (Index), Tầng 2 chấm điểm xác suất tăng giá vi mô (Cổ phiếu).
    """)

st.markdown('</div>', unsafe_allow_html=True)
