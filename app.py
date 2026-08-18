import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="E.V Quant Terminal", layout="wide")

# --- KIỂM TRA VÀ ĐỌC FILE AN TOÀN ---
try:
    df_master = pd.read_csv("MASTER_QUANT_DB.csv")
    data_loaded = True
except Exception as e:
    data_loaded = False
    error_msg = str(e)

# --- GIAO DIỆN CHÍNH ---
st.title("⚡ E.V QUANTITATIVE TRADING TERMINAL")
st.markdown("---")

if data_loaded:
    st.success(f"✅ Đã kết nối dữ liệu thành công! Tổng số mã trong Database: {len(df_master)}")
    
    # Hiển thị bảng dữ liệu mẫu từ Colab đẩy lên
    st.subheader("📊 Dữ liệu Định lượng Thời gian thực")
    st.dataframe(df_master, use_container_width=True)
else:
    st.error("⚠️ Chưa tìm thấy hoặc không đọc được file `MASTER_QUANT_DB.csv`.")
    st.info("💡 Hướng dẫn khắc phục: Hãy quay lại Google Colab, chạy lại cell đẩy file lên GitHub, sau đó tải lại trang này.")
    with st.expander("Chi tiết lỗi kỹ thuật từ hệ thống"):
        st.code(error_msg)
