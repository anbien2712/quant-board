import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from scipy.signal import savgol_filter
import datetime
import os

# =================================================================================
# CẤU HÌNH TRANG WEB
# =================================================================================
st.set_page_config(page_title="E.V Quant Terminal", layout="wide")
st.title("🧠 E.V QUANT TERMINAL (BẢN GỐC TỪ TÁC GIẢ)")

# =================================================================================
# HÀM TẢI & XỬ LÝ DỮ LIỆU (GIỮ NGUYÊN 100% LOGIC V8.0 VÀ V10.0 CỦA BẠN)
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
    file_path = "data/MuaBanChuDong_Explore.csv.gz"
    if os.path.exists(file_path):
        df_of = pd.read_csv(file_path)
        df_of['Ngay'] = pd.to_datetime(df_of['Ngay'])
        df_market_of = df_of.groupby('Ngay').agg({'MuaCD': 'sum', 'BanCD': 'sum', 'Net': 'sum', 'Tong': 'sum'}).reset_index()
        df_market_of['NetRatio_Market'] = (df_market_of['Net'] / df_market_of['Tong']) * 100
        df_ai = pd.merge(df_vni, df_market_of, left_on='DATE', right_on='Ngay', how='inner')
    else:
        st.warning(f"⚠️ Không tìm thấy file {file_path}. Vui lòng upload lên GitHub.")
        df_ai = df_vni.copy()
        df_ai['Net'] = 0

    # --- 9 ĐẶC TRƯNG VECTOR (GIỮ NGUYÊN CÔNG THỨC) ---
    df_ai['R1'] = df_ai['CLOSE'].pct_change(1) * 100
    df_ai['R3'] = df_ai['CLOSE'].pct_change(3) * 100
    df_ai['R5'] = df_ai['CLOSE'].pct_change(5) * 100
    w_ret = df_ai['R1']*0.5 + df_ai['R3']*0.3 + df_ai['R5']*0.2
    z_ret = (w_ret - w_ret.rolling(20).mean()) / (w_ret.rolling(20).std() + 1e-9)
    df_ai['F1'] = np.select([z_ret > 1.5, z_ret.between(0.5, 1.5), z_ret < -1.5, z_ret.between(-1.5, -0.5)], [2, 1, -2, -1], default=0)

    for m in [10, 20, 50, 100]:
        df_ai[f'MA{m}'] = df_ai['CLOSE'].rolling(m).mean()
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
    
    # ---> ĐOẠN ANH CẦN CHÈN VÀO LÀ TỪ ĐÂY...
    timeframes = [1, 3, 5, 7, 30, 60]
    for n in timeframes:
        roll_high = df_ai['HIGH'].rolling(window=n, min_periods=1).max()
        roll_low = df_ai['LOW'].rolling(window=n, min_periods=1).min()
        df_ai[f'HL_{n}D'] = (roll_high - roll_low) / (df_ai['CLOSE'] + 1e-9) * 100
    brk = df_ai['HL_5D'] / (df_ai['HL_60D'] + 1e-9)
    # ... ĐẾN ĐÂY <---

    cr = (df_ai['HIGH'] - df_ai['LOW']) + 1e-9
    u_wick = (df_ai['HIGH'] - df_ai[['OPEN', 'CLOSE']].max(axis=1)) / cr
    l_wick = (df_ai[['OPEN', 'CLOSE']].min(axis=1) - df_ai['LOW']) / cr
    body = np.where(df_ai['CLOSE'] > df_ai['OPEN'], 1, -1)
    df_ai['F4'] = np.select([(brk > 0.5) & (u_wick > 0.45), (brk > 0.3) & (body == 1) & (u_wick < 0.2), (brk > 0.5) & (l_wick > 0.45), (brk > 0.3) & (body == -1) & (l_wick < 0.2)], [2, 1, -2, -1], default=0)

    ef = df_ai['CLOSE'].ewm(span=12, adjust=False).mean()
    es = df_ai['CLOSE'].ewm(span=26, adjust=False).mean()
    macd = ef - es
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

    ma20 = df_ai['CLOSE'].rolling(20).mean()
    b_std = df_ai['CLOSE'].rolling(20).std()
    b_up = ma20 + b_std * 2
    b_low = ma20 - b_std * 2
    b_diff = b_up - b_low
    pct_b = (df_ai['CLOSE'] - b_low) / (b_diff + 1e-9)
    bw = b_diff / (ma20 + 1e-9)
    bw_ma = bw.rolling(20).mean()
    df_ai['F7'] = np.select([pct_b > 0.95, pct_b < 0.05, bw < bw_ma, (pct_b > 0.5) & (pct_b <= 0.95) & (bw >= bw_ma), (pct_b >= 0.05) & (pct_b <= 0.5) & (bw >= bw_ma)], [2, -2, 0, 1, -1], default=0)

    df_ai['F8'] = np.where(df_ai['Net'] > 0, 1, -1)

    hpr = df_ai['CLOSE'].pct_change(3) * 100
    skew = hpr.rolling(20).skew().fillna(0)
    kurt = hpr.rolling(20).kurt().fillna(0)
    market_regime = np.where(kurt.abs() > 2.0, 'Extremistan', 'Mediocristan')
    df_ai['F9'] = np.select([(skew > 0.8) & (market_regime == 'Mediocristan'), (skew > 0.2) & (skew <= 0.8), (skew < -0.8) & (kurt > 2.0), (skew >= -0.8) & (skew < -0.2)], [2, 1, -2, -1], default=0)

    score_cols = [f'F{i}' for i in range(1, 10)]
    df_ai['Composite_Score'] = df_ai[score_cols].sum(axis=1)

    # --- MÁY TRẠNG THÁI WYCKOFF (TỪ BẢN CODE V8.0 GỐC) ---
    wyckoff_phases = []
    current_phase = 'Phase E (Trend)'
    days_in_phase = 0

    for i in range(len(df_ai)):
        f1, f2, f3, f4, f5, f6, f7, f9 = df_ai.loc[i, ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F9']]
        comp_score = df_ai.loc[i, 'Composite_Score']
        
        vector_norm = abs(f1) + abs(f3) + abs(f6) + abs(f7) + abs(f9)

        if current_phase == 'Phase E (Trend)':
            if vector_norm >= 6 and (f6 in [-2, 2] or f9 in [-2, 2]):
                current_phase = 'Phase A (Climax/Stop)'
                days_in_phase = 0

        elif current_phase == 'Phase A (Climax/Stop)':
            days_in_phase += 1
            if days_in_phase > 3 and abs(comp_score) <= 4 and f3 <= 0:
                current_phase = 'Phase B (Building Cause)'
                days_in_phase = 0

        elif current_phase == 'Phase B (Building Cause)':
            days_in_phase += 1
            if days_in_phase >= 15:
                if (f3 == -2) or (f4 in [-2, 2]) or (f7 in [-2, 2]):
                    current_phase = 'Phase C (Shakeout/Test)'
                    days_in_phase = 0
            elif days_in_phase > 5 and abs(f2) == 2:
                current_phase = 'Phase E (Trend)'
                days_in_phase = 0

        elif current_phase == 'Phase C (Shakeout/Test)':
            days_in_phase += 1
            if days_in_phase <= 7 and abs(f1) >= 1 and abs(f5) >= 1:
                current_phase = 'Phase D (Trend in TR)'
                days_in_phase = 0
            elif days_in_phase > 7:
                current_phase = 'Phase B (Building Cause)'

        elif current_phase == 'Phase D (Trend in TR)':
            days_in_phase += 1
            if abs(f2) == 2 and abs(f1) == 2:
                current_phase = 'Phase E (Trend)'
                days_in_phase = 0
            elif days_in_phase > 10 and abs(f1) == 0:
                current_phase = 'Phase B (Building Cause)'

        wyckoff_phases.append(current_phase)

    df_ai['Wyckoff_Phase'] = wyckoff_phases

    # --- BỘ LỌC ĐỈNH ĐÁY VÀ DYNAMIC REGIME (TỪ BẢN CODE V10.0 GỐC) ---
    df_ai['P_Smooth'] = savgol_filter(df_ai['CLOSE'], window_length=15, polyorder=3)
    df_ai['Velocity'] = np.gradient(df_ai['P_Smooth'])
    df_ai['Velocity_Prev'] = df_ai['Velocity'].shift(1)
    df_ai['Inflection'] = ((df_ai['Velocity'] * df_ai['Velocity_Prev']) < 0)

    def classify_basic_inflection(row):
        if not row['Inflection']: return 'None'
        return 'Đáy' if row['Velocity'] > 0 else 'Đỉnh'

    df_ai['Inflection_Type'] = df_ai.apply(classify_basic_inflection, axis=1)

    df_ai['HPR_3'] = df_ai['CLOSE'].pct_change(3) * 100
    df_ai['Regime_Zone'] = (df_ai['Inflection_Type'] != 'None').astype(int).cumsum()

    def calculate_dynamic_moments(group):
        group['Dyn_Skew'] = group['HPR_3'].expanding(min_periods=4).skew()
        group['Dyn_Kurt'] = group['HPR_3'].expanding(min_periods=4).kurt()
        return group

    df_ai = df_ai.groupby('Regime_Zone', group_keys=False).apply(calculate_dynamic_moments)
    df_ai['Dyn_Skew'] = df_ai['Dyn_Skew'].ffill().fillna(0)
    df_ai['Dyn_Kurt'] = df_ai['Dyn_Kurt'].ffill().fillna(0)

    condition_extremistan = (df_ai['Dyn_Kurt'] > 1.5) | (df_ai['Dyn_Skew'].abs() > 1.2)
    df_ai['Market_Regime'] = np.where(condition_extremistan, 'Extremistan (Rủi Ro)', 'Mediocristan (Bình Yên)')

    return df_ai

# Chạy hàm tạo dữ liệu
with st.spinner('Đang tổng hợp Dữ liệu Vĩ mô & Order Flow...'):
    df_full = load_and_process_data()

# Lấy 1 năm gần nhất cho đồ thị (để tránh rác như bản gốc của bạn)
one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=365)
df_plot = df_full[df_full['DATE'] >= pd.to_datetime(one_year_ago)].copy().reset_index(drop=True)
if 'Net' in df_plot.columns:
    df_plot['CVD'] = df_plot['Net'].cumsum() # Reset CVD scale

# =================================================================================
# GIAO DIỆN WEB: CHIA 2 TABS CHÍNH
# =================================================================================
plt.style.use('dark_background')
tab1, tab2 = st.tabs(["📊 PHẦN 1&2: WYCKOFF PHASES & ORDER FLOW", "⚠️ PHẦN 3: BẢN ĐỒ RỦI RO (REGIME)"])

# ---------------------------------------------------------------------------------
# TAB 1: WYCKOFF & ORDER FLOW (TỪ V8.0 GỐC)
# ---------------------------------------------------------------------------------
with tab1:
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(24, 14), gridspec_kw={'height_ratios': [2, 1]}, sharex=True)
    plt.subplots_adjust(hspace=0.05)

    ax1.plot(df_plot['DATE'], df_plot['CLOSE'], color='white', linewidth=2, zorder=5, label='VNINDEX')

    phase_colors = {
        'Phase A (Climax/Stop)': 'crimson',       
        'Phase B (Building Cause)': 'dimgray',    
        'Phase C (Shakeout/Test)': 'goldenrod',   
        'Phase D (Trend in TR)': 'dodgerblue',    
        'Phase E (Trend)': 'limegreen'            
    }

    start_idx = 0
    for i in range(1, len(df_plot)):
        if df_plot.loc[i, 'Wyckoff_Phase'] != df_plot.loc[i-1, 'Wyckoff_Phase'] or i == len(df_plot) - 1:
            phase = df_plot.loc[i-1, 'Wyckoff_Phase']
            color = phase_colors.get(phase, 'black')
            ax1.axvspan(df_plot.loc[start_idx, 'DATE'], df_plot.loc[i, 'DATE'], color=color, alpha=0.35, zorder=1)
            start_idx = i

    ax1.set_title('E.V QUANT TERMINAL: WYCKOFF PHASES & ORDER FLOW X-RAY', fontsize=22, fontweight='bold', color='white', pad=20)
    ax1.set_ylabel('Điểm số VNINDEX', fontsize=14, color='white')
    ax1.yaxis.grid(True, linestyle='--', alpha=0.3)

    legend_patches = [mpatches.Patch(color=color, alpha=0.5, label=phase) for phase, color in phase_colors.items()]
    ax1.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, 1.08), ncol=5, frameon=False, fontsize=14)

    colors = np.where(df_plot['Net'] > 0, 'limegreen', 'crimson')
    ax2.bar(df_plot['DATE'], df_plot['Net'] / 1e9, color=colors, alpha=0.8, width=1, label='Net Order Flow (Tỷ Cổ phiếu)')

    ax3 = ax2.twinx()
    if 'CVD' in df_plot.columns:
        ax3.plot(df_plot['DATE'], df_plot['CVD'] / 1e9, color='gold', linewidth=2.5, label='CVD (Tích lũy Lực Mua Ròng)')

    ax2.set_ylabel('Net Delta (Tỷ CP)', fontsize=12, color='white')
    ax3.set_ylabel('CVD Line (Gold)', fontsize=12, color='gold')
    ax2.yaxis.grid(True, linestyle='--', alpha=0.2)

    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=12)

    st.pyplot(fig1)

# ---------------------------------------------------------------------------------
# TAB 2: BẢN ĐỒ RỦI RO (TỪ V10.0 GỐC)
# ---------------------------------------------------------------------------------
with tab2:
    fig2, (ax4, ax5, ax6) = plt.subplots(3, 1, figsize=(24, 16), gridspec_kw={'height_ratios': [2, 1, 1.5]}, sharex=True)
    plt.subplots_adjust(hspace=0.1)

    ax4.plot(df_plot['DATE'], df_plot['CLOSE'], color='white', linewidth=2, label='VNINDEX')
    ax4.set_title('PHẦN 3: BẢN ĐỒ RỦI RO (DYNAMIC T+3 MARKET REGIME)', fontsize=22, fontweight='bold', color='gold', pad=20)
    ax4.set_ylabel('VNINDEX', fontsize=14, color='white')
    ax4.yaxis.grid(True, linestyle='--', alpha=0.3)

    inflections = df_plot[df_plot['Inflection_Type'] != 'None']
    for idx, row in inflections.iterrows():
        color = 'limegreen' if row['Inflection_Type'] == 'Đáy' else 'crimson'
        ax4.axvline(x=row['DATE'], color=color, linestyle='--', linewidth=1.5, alpha=0.8)
        ax4.scatter(row['DATE'], row['CLOSE'], color=color, s=150, zorder=5)

    colors_hpr = np.where(df_plot['HPR_3'] > 0, 'limegreen', 'crimson')
    ax5.bar(df_plot['DATE'], df_plot['HPR_3'], color=colors_hpr, alpha=0.7, width=1.5, label='Lợi nhuận T+3 (%)')
    ax5.axhline(0, color='white', linewidth=1)
    ax5.set_ylabel('T+3 Return (%)', fontsize=12, color='white')
    ax5.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax5.legend(loc='upper left', frameon=False, fontsize=12)

    ax6.fill_between(df_plot['DATE'], -3, 3, where=(df_plot['Market_Regime'] == 'Extremistan (Rủi Ro)'), color='darkred', alpha=0.3, label='Vùng Extremistan (Rủi ro cao)')
    ax6.fill_between(df_plot['DATE'], -3, 3, where=(df_plot['Market_Regime'] == 'Mediocristan (Bình Yên)'), color='darkgreen', alpha=0.2, label='Vùng Mediocristan (An toàn)')

    ax6.plot(df_plot['DATE'], df_plot['Dyn_Skew'], color='cyan', linewidth=2.5, label='Độ Lệch Histogram (Skewness)')
    ax6.axhline(1.2, color='cyan', linestyle=':', alpha=0.5)
    ax6.axhline(-1.2, color='cyan', linestyle=':', alpha=0.5)

    ax6.plot(df_plot['DATE'], df_plot['Dyn_Kurt'], color='magenta', linewidth=2, linestyle='--', label='Độ Nhọn Đuôi Béo (Kurtosis)')
    ax6.axhline(1.5, color='magenta', linestyle=':', alpha=0.5)
    ax6.axhline(0, color='gray', linewidth=1)

    ax6.set_ylabel('Chỉ số Hình thái (Skew/Kurt)', fontsize=12, color='white')
    ax6.set_ylim(-3.5, 3.5)
    ax6.yaxis.grid(True, linestyle='--', alpha=0.3)

    handles, labels = ax6.get_legend_handles_labels()
    ax6.legend(handles, labels, loc='upper left', ncol=4, frameon=True, facecolor='black', fontsize=11)

    ax6.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    ax6.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=12)

    st.pyplot(fig2)
