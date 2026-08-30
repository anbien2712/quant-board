import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter, find_peaks
import datetime
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =================================================================================
# CẤU HÌNH TRANG WEB & CUSTOM CSS (GIAO DIỆN FINTECH)
# ==========================================
st.set_page_config(page_title="Finaura Quant Terminal", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS ép giao diện giống phong cách Fintech (Nền tối, Xanh Neon)
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    /* Chỉnh màu chữ của các tab */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 18px;
        font-weight: 600;
        color: #A0A0A0;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom-color: #CCFF00 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p {
        color: #CCFF00 !important;
    }
    /* Các thẻ Card */
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #333333;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ FINAURA QUANT TERMINAL")
st.markdown("<p style='color: #A0A0A0; font-size: 16px;'>Hệ thống Phân tích Vĩ mô VNINDEX: Wyckoff 5 Phases | Order Flow X-Ray | Dynamic Regime</p>", unsafe_allow_html=True)

# =================================================================================
# HÀM TẢI & XỬ LÝ DỮ LIỆU (GIỮ NGUYÊN 100% LOGIC GỐC CỦA BẠN)
# =================================================================================
@st.cache_data(ttl=3600)
def load_and_process_data():
    # 1. TẢI DỮ LIỆU VNINDEX
    final_end_ts = int(datetime.datetime.now().timestamp())
    final_start_ts = int((datetime.datetime.now() - datetime.timedelta(days=365 * 3)).timestamp())
    api_url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/index?symbol=VNINDEX&resolution=1D&from={final_start_ts}&to={final_end_ts}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if data.get('t'):
            df_vni = pd.DataFrame({
                'DATE': pd.to_datetime(data['t'], unit='s'),
                'OPEN': data['o'], 'HIGH': data['h'], 'LOW': data['l'],
                'CLOSE': data['c'], 'VOLUME': data['v']
            })
            df_vni['DATE'] = pd.to_datetime(df_vni['DATE'].dt.date)
            df_vni = df_vni.dropna().reset_index(drop=True)
        else:
            df_vni = pd.DataFrame()
    else:
        df_vni = pd.DataFrame()

    # 2. XỬ LÝ FILE ORDER FLOW
    file_path = "data/MuaBanChuDong_Explore.csv"
    if os.path.exists(file_path):
        df_of = pd.read_csv(file_path)
        df_of['Ngay'] = pd.to_datetime(df_of['Ngay'])
        df_market_of = df_of.groupby('Ngay').agg({'MuaCD': 'sum', 'BanCD': 'sum', 'Net': 'sum', 'Tong': 'sum'}).reset_index()
        df_market_of['NetRatio_Market'] = (df_market_of['Net'] / df_market_of['Tong']) * 100
        df_ai = pd.merge(df_vni, df_market_of, left_on='DATE', right_on='Ngay', how='inner')
    else:
        df_ai = df_vni.copy()
        df_ai['Net'] = 0

    # --- 9 ĐẶC TRƯNG VECTOR ---
    df_ai['R1'] = df_ai['CLOSE'].pct_change(1) * 100
    df_ai['R3'] = df_ai['CLOSE'].pct_change(3) * 100
    df_ai['R5'] = df_ai['CLOSE'].pct_change(5) * 100
    w_ret = df_ai['R1']*0.5 + df_ai['R3']*0.3 + df_ai['R5']*0.2
    z_ret = (w_ret - w_ret.rolling(20).mean()) / (w_ret.rolling(20).std() + 1e-9)
    df_ai['F1'] = np.select([z_ret > 1.5, z_ret.between(0.5, 1.5), z_ret < -1.5, z_ret.between(-1.5, -0.5)], [2, 1, -2, -1], default=0)

    for m in [10, 20, 50, 100]: df_ai[f'MA{m}'] = df_ai['CLOSE'].rolling(m).mean()
    d10 = (df_ai['CLOSE'] - df_ai['MA10']) / df_ai['MA10'] * 100
    d20 = (df_ai['CLOSE'] - df_ai['MA20']) / df_ai['MA20'] * 100
    d50 = (df_ai['CLOSE'] - df_ai['MA50']) / df_ai['MA50'] * 100
    d100 = (df_ai['CLOSE'] - df_ai['MA100']) / df_ai['MA100'] * 100
    w_dev = d10*0.3 + d20*0.3 + d50*0.2 + d100*0.2
    align = ((df_ai['MA10']>df_ai['MA20']).astype(int) + (df_ai['MA20']>df_ai['MA50']).astype(int) + (df_ai['MA50']>df_ai['MA100']).astype(int)) / 3
    ma_raw = w_dev + ((align * 2 - 1) * 5)
    z_ma = (ma_raw - ma_raw.rolling(20).mean()) / (ma_raw.rolling(20).std() + 1e-9)
    df_ai['F2'] = np.select([z_ma > 1.5, z_ma.between(0.5, 1.5), z_ma < -1.5, z_ma.between(-1.5, -0.5)], [2, 1, -2, -1], default=0)

    vol_prev = df_ai['VOLUME'].rolling(20).mean().shift(1)
    v_spike = df_ai['VOLUME'] / (vol_prev + 1e-9)
    s_gt = (v_spike > 1.5).rolling(20).sum()
    s_lt = (v_spike < 0.8).rolling(20).sum()
    avg_s = v_spike.rolling(20).mean()
    df_ai['F3'] = np.select([(s_gt >= 3) & (v_spike > 1.2), (avg_s > 1.1) & (s_gt >= 1), (s_lt >= 10) & (avg_s < 0.8), (avg_s < 0.9)], [2, 1, -2, -1], default=0)
    timeframes = [1, 3, 5, 7, 30, 60]
    for n in timeframes:
        roll_high = df_ai['HIGH'].rolling(window=n, min_periods=1).max()
        roll_low = df_ai['LOW'].rolling(window=n, min_periods=1).min()
        df_ai[f'HL_{n}D'] = (roll_high - roll_low) / (df_ai['CLOSE'] + 1e-9) * 100
    brk = df_ai['HL_5D'] / (df_ai['HL_60D'] + 1e-9)
    cr = (df_ai['HIGH'] - df_ai['LOW']) + 1e-9
    u_wick = (df_ai['HIGH'] - df_ai[['OPEN', 'CLOSE']].max(axis=1)) / cr
    l_wick = (df_ai[['OPEN', 'CLOSE']].min(axis=1) - df_ai['LOW']) / cr
    body = np.where(df_ai['CLOSE'] > df_ai['OPEN'], 1, -1)
    df_ai['F4'] = np.select([(brk > 0.5) & (u_wick > 0.45), (brk > 0.3) & (body == 1) & (u_wick < 0.2), (brk > 0.5) & (l_wick > 0.45), (brk > 0.3) & (body == -1) & (l_wick < 0.2)], [2, 1, -2, -1], default=0)

    macd = df_ai['CLOSE'].ewm(span=12, adjust=False).mean() - df_ai['CLOSE'].ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    hist = macd - sig
    d_hist = hist - hist.shift(1)
    df_ai['F5'] = np.select([(macd > 0) & (hist > 0) & (d_hist > 0), (macd <= 0) & (hist > 0) & (d_hist > 0), (macd < 0) & (hist < 0) & (d_hist < 0), (macd >= 0) & (hist < 0) & (d_hist < 0)], [2, 1, -2, -1], default=0)

    delta = df_ai['CLOSE'].diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rsi = 100 - (100 / (1 + gain / (loss + 1e-9)))
    rsi_sig = rsi.rolling(14).mean()
    df_ai['F6'] = np.select([rsi > 70, (rsi > 55) & (rsi > rsi_sig), rsi < 30, (rsi < 45) & (rsi < rsi_sig)], [2, 1, -2, -1], default=0)

    ma20, b_std = df_ai['CLOSE'].rolling(20).mean(), df_ai['CLOSE'].rolling(20).std()
    pct_b = (df_ai['CLOSE'] - (ma20 - b_std * 2)) / (4 * b_std + 1e-9)
    bw = (4 * b_std) / (ma20 + 1e-9)
    bw_ma = bw.rolling(20).mean()
    df_ai['F7'] = np.select([pct_b > 0.95, pct_b < 0.05, bw < bw_ma, (pct_b > 0.5) & (pct_b <= 0.95) & (bw >= bw_ma), (pct_b >= 0.05) & (pct_b <= 0.5) & (bw >= bw_ma)], [2, -2, 0, 1, -1], default=0)
    df_ai['F8'] = np.where(df_ai['Net'] > 0, 1, -1)

    skew = df_ai['CLOSE'].pct_change(3).rolling(20).skew().fillna(0)
    kurt = df_ai['CLOSE'].pct_change(3).rolling(20).kurt().fillna(0)
    market_regime = np.where(kurt.abs() > 2.0, 'Extremistan', 'Mediocristan')
    df_ai['F9'] = np.select([(skew > 0.8) & (market_regime == 'Mediocristan'), (skew > 0.2) & (skew <= 0.8), (skew < -0.8) & (kurt > 2.0), (skew >= -0.8) & (skew < -0.2)], [2, 1, -2, -1], default=0)

    score_cols = [f'F{i}' for i in range(1, 10)]
    df_ai['Composite_Score'] = df_ai[score_cols].sum(axis=1)

    # --- MÁY TRẠNG THÁI WYCKOFF ---
    wyckoff_phases = []
    current_phase = 'Phase E (Trend)'
    days_in_phase = 0
    for i in range(len(df_ai)):
        f1, f2, f3, f4, f5, f6, f7, f9 = df_ai.loc[i, ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F9']]
        comp_score = df_ai.loc[i, 'Composite_Score']
        vector_norm = abs(f1) + abs(f3) + abs(f6) + abs(f7) + abs(f9)
        if current_phase == 'Phase E (Trend)' and vector_norm >= 6 and (f6 in [-2, 2] or f9 in [-2, 2]):
            current_phase, days_in_phase = 'Phase A (Climax/Stop)', 0
        elif current_phase == 'Phase A (Climax/Stop)':
            days_in_phase += 1
            if days_in_phase > 3 and abs(comp_score) <= 4 and f3 <= 0: current_phase, days_in_phase = 'Phase B (Building Cause)', 0
        elif current_phase == 'Phase B (Building Cause)':
            days_in_phase += 1
            if days_in_phase >= 15 and ((f3 == -2) or (f4 in [-2, 2]) or (f7 in [-2, 2])): current_phase, days_in_phase = 'Phase C (Shakeout/Test)', 0
            elif days_in_phase > 5 and abs(f2) == 2: current_phase, days_in_phase = 'Phase E (Trend)', 0
        elif current_phase == 'Phase C (Shakeout/Test)':
            days_in_phase += 1
            if days_in_phase <= 7 and abs(f1) >= 1 and abs(f5) >= 1: current_phase, days_in_phase = 'Phase D (Trend in TR)', 0
            elif days_in_phase > 7: current_phase = 'Phase B (Building Cause)'
        elif current_phase == 'Phase D (Trend in TR)':
            days_in_phase += 1
            if abs(f2) == 2 and abs(f1) == 2: current_phase, days_in_phase = 'Phase E (Trend)', 0
            elif days_in_phase > 10 and abs(f1) == 0: current_phase = 'Phase B (Building Cause)'
        wyckoff_phases.append(current_phase)
    df_ai['Wyckoff_Phase'] = wyckoff_phases

    # --- BỘ LỌC ĐỈNH ĐÁY VÀ DYNAMIC REGIME ---
    df_ai['P_Smooth'] = savgol_filter(df_ai['CLOSE'], window_length=15, polyorder=3)
    df_ai['Velocity'] = np.gradient(df_ai['P_Smooth'])
    df_ai['Inflection'] = ((df_ai['Velocity'] * df_ai['Velocity'].shift(1)) < 0)
    df_ai['Inflection_Type'] = np.where(~df_ai['Inflection'], 'None', np.where(df_ai['Velocity'] > 0, 'Đáy', 'Đỉnh'))

    df_ai['HPR_3'] = df_ai['CLOSE'].pct_change(3) * 100
    df_ai['Regime_Zone'] = (df_ai['Inflection_Type'] != 'None').astype(int).cumsum()

    def calc_moments(group):
        group['Dyn_Skew'] = group['HPR_3'].expanding(min_periods=4).skew()
        group['Dyn_Kurt'] = group['HPR_3'].expanding(min_periods=4).kurt()
        return group
    df_ai = df_ai.groupby('Regime_Zone', group_keys=False).apply(calc_moments)
    df_ai[['Dyn_Skew', 'Dyn_Kurt']] = df_ai[['Dyn_Skew', 'Dyn_Kurt']].ffill().fillna(0)
    df_ai['Market_Regime'] = np.where((df_ai['Dyn_Kurt'] > 1.5) | (df_ai['Dyn_Skew'].abs() > 1.2), 'Extremistan (Rủi Ro)', 'Mediocristan (Bình Yên)')

    return df_ai

with st.spinner('Loading Core Engine...'):
    df_full = load_and_process_data()

# Lọc dữ liệu 1 năm cho hiển thị đẹp
one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=365)
df = df_full[df_full['DATE'] >= pd.to_datetime(one_year_ago)].copy().reset_index(drop=True)
if 'Net' in df.columns: df['CVD'] = df['Net'].cumsum()

# Tạo Metrics Top Bar
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="Mức giá hiện tại (VNINDEX)", value=f"{df['CLOSE'].iloc[-1]:,.2f}", delta=f"{df['CLOSE'].iloc[-1] - df['CLOSE'].iloc[-2]:.2f}")
with col2: st.metric(label="Thanh khoản thị trường (Phiên cuối)", value=f"{df['VOLUME'].iloc[-1]/1e6:,.0f} M", delta=f"{(df['VOLUME'].iloc[-1]-df['VOLUME'].iloc[-2])/1e6:.0f} M")
with col3: st.metric(label="Khối lượng Mua/Bán Ròng (Phiên cuối)", value=f"{df['Net'].iloc[-1]/1e6:,.0f} M", delta="Tích cực" if df['Net'].iloc[-1] > 0 else "Tiêu cực", delta_color="normal" if df['Net'].iloc[-1] > 0 else "inverse")
with col4: st.metric(label="Giai đoạn Wyckoff Vĩ mô", value=df['Wyckoff_Phase'].iloc[-1])

# =================================================================================
# THIẾT KẾ PLOTLY CHART (THAY THẾ MATPLOTLIB)
# =================================================================================
# Bảng màu phong cách Fintech
COLORS = {
    'bg': '#121212', 'paper': '#1E1E1E', 'grid': '#333333',
    'price': '#FFFFFF', 'smooth': '#CCFF00', 'cvd': '#D4F84F',
    'up': '#00E676', 'down': '#FF1744', 'inflect': '#FF00FF',
    'phases': {
        'Phase A (Climax/Stop)': 'rgba(255, 23, 68, 0.15)',
        'Phase B (Building Cause)': 'rgba(128, 128, 128, 0.1)',
        'Phase C (Shakeout/Test)': 'rgba(255, 196, 0, 0.15)',
        'Phase D (Trend in TR)': 'rgba(0, 176, 255, 0.15)',
        'Phase E (Trend)': 'rgba(0, 230, 118, 0.15)'
    }
}

tab1, tab2 = st.tabs(["📊 WYCKOFF PHASES & ORDER FLOW", "⚠️ DYNAMIC MARKET REGIME"])

with tab1:
    # Chart 1: VNINDEX & Wyckoff
    fig1 = go.Figure()

    # Vẽ các dải màu Wyckoff Phases
    start_idx = 0
    for i in range(1, len(df)):
        if df.loc[i, 'Wyckoff_Phase'] != df.loc[i-1, 'Wyckoff_Phase'] or i == len(df) - 1:
            phase = df.loc[i-1, 'Wyckoff_Phase']
            fig1.add_vrect(x0=df.loc[start_idx, 'DATE'], x1=df.loc[i, 'DATE'],
                           fillcolor=COLORS['phases'].get(phase, 'rgba(0,0,0,0)'),
                           layer="below", line_width=0, name=phase)
            start_idx = i

    fig1.add_trace(go.Scatter(x=df['DATE'], y=df['CLOSE'], mode='lines', line=dict(color=COLORS['price'], width=2), name='VNINDEX'))
    fig1.add_trace(go.Scatter(x=df['DATE'], y=df['P_Smooth'], mode='lines', line=dict(color=COLORS['smooth'], width=1.5, dash='dash'), name='SG Filter'))

    inflections = df[df['Inflection'] == True]
    fig1.add_trace(go.Scatter(x=inflections['DATE'], y=inflections['P_Smooth'], mode='markers', marker=dict(color=COLORS['inflect'], size=10), name='Điểm Uốn'))

    fig1.update_layout(
        title="WYCKOFF 5 PHASES & SG DYNAMICS", title_font=dict(size=20, color='white'),
        plot_bgcolor=COLORS['bg'], paper_bgcolor=COLORS['paper'],
        xaxis=dict(showgrid=True, gridcolor=COLORS['grid'], rangeslider=dict(visible=True, thickness=0.08)), # <--- SLICER Ở ĐÂY
        yaxis=dict(showgrid=True, gridcolor=COLORS['grid']),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: SG Velocity & Order Flow (Subplots)
    fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                         subplot_titles=("ĐỘNG HỌC SG FILTER (Vận Tốc)", "MUA BÁN CHỦ ĐỘNG (Order Flow) & CVD"),
                         specs=[[{"secondary_y": False}], [{"secondary_y": True}]])

    # Velocity (Tô màu xanh/đỏ)
    pos_v = df['Velocity'].copy(); pos_v[pos_v < 0] = 0
    neg_v = df['Velocity'].copy(); neg_v[neg_v > 0] = 0
    fig2.add_trace(go.Scatter(x=df['DATE'], y=pos_v, fill='tozeroy', line=dict(color=COLORS['up'], width=1), name='Hướng Lên'), row=1, col=1)
    fig2.add_trace(go.Scatter(x=df['DATE'], y=neg_v, fill='tozeroy', line=dict(color=COLORS['down'], width=1), name='Hướng Xuống'), row=1, col=1)
    fig2.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)

    # Order Flow Bar
    colors_net = np.where(df['Net'] > 0, COLORS['up'], COLORS['down'])
    fig2.add_trace(go.Bar(x=df['DATE'], y=df['Net'], marker_color=colors_net, name='Net Delta'), row=2, col=1, secondary_y=False)
    # CVD Line
    if 'CVD' in df.columns:
        fig2.add_trace(go.Scatter(x=df['DATE'], y=df['CVD'], mode='lines', line=dict(color=COLORS['cvd'], width=2.5), name='CVD (Tích lũy)'), row=2, col=1, secondary_y=True)

    fig2.update_layout(
        plot_bgcolor=COLORS['bg'], paper_bgcolor=COLORS['paper'], height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )
    fig2.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    fig2.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    # Chart 3: Market Regime
    fig3 = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                         subplot_titles=("VNINDEX & RANH GIỚI RESET", "LỢI NHUẬN T+3 (HPR_3)", "CHỈ SỐ HÌNH THÁI (Skewness/Kurtosis)"))

    # Giá & Ranh giới
    fig3.add_trace(go.Scatter(x=df['DATE'], y=df['CLOSE'], mode='lines', line=dict(color=COLORS['price'], width=2), name='VNINDEX'), row=1, col=1)
    for idx, row in inflections.iterrows():
        c = COLORS['up'] if row['Inflection_Type'] == 'Đáy' else COLORS['down']
        fig3.add_vline(x=row['DATE'], line_dash="dash", line_color=c, opacity=0.6, row=1, col=1)
        fig3.add_trace(go.Scatter(x=[row['DATE']], y=[row['CLOSE']], mode='markers', marker=dict(color=c, size=10), showlegend=False), row=1, col=1)

    # Lợi nhuận T+3
    colors_hpr = np.where(df['HPR_3'] > 0, COLORS['up'], COLORS['down'])
    fig3.add_trace(go.Bar(x=df['DATE'], y=df['HPR_3'], marker_color=colors_hpr, name='HPR T+3'), row=2, col=1)

    # Skew & Kurt
    fig3.add_trace(go.Scatter(x=df['DATE'], y=df['Dyn_Skew'], mode='lines', line=dict(color='#00E5FF', width=2), name='Skewness'), row=3, col=1)
    fig3.add_trace(go.Scatter(x=df['DATE'], y=df['Dyn_Kurt'], mode='lines', line=dict(color='#D500F9', width=2, dash='dash'), name='Kurtosis'), row=3, col=1)

    # Tô màu nền Extremistan
    start_idx = 0
    for i in range(1, len(df)):
        if df.loc[i, 'Market_Regime'] != df.loc[i-1, 'Market_Regime'] or i == len(df) - 1:
            regime = df.loc[i-1, 'Market_Regime']
            c = 'rgba(255, 23, 68, 0.1)' if 'Extremistan' in regime else 'rgba(0, 230, 118, 0.05)'
            fig3.add_vrect(x0=df.loc[start_idx, 'DATE'], x1=df.loc[i, 'DATE'], fillcolor=c, layer="below", line_width=0, row=3, col=1)
            start_idx = i

    fig3.update_layout(
        plot_bgcolor=COLORS['bg'], paper_bgcolor=COLORS['paper'], height=700,
        xaxis3=dict(rangeslider=dict(visible=True, thickness=0.05)), # <--- SLICER CHO REGIME CHART
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig3.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    fig3.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])

    st.plotly_chart(fig3, use_container_width=True)
