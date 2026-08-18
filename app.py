import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Đọc file CSV an toàn (có kiểm tra lỗi nếu chưa tìm thấy file)
try:
    df_master = pd.read_csv("MASTER_QUANT_DB.csv")
except FileNotFoundError:
    st.error("⚠️ Chưa tìm thấy file dữ liệu MASTER_QUANT_DB.csv trên GitHub. Vui lòng chạy lại Google Colab để đẩy file lên.")
    st.stop()
