# pip install streamlit yfinance plotly pandas numpy

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date
from plotly import graph_objs as go
import numpy as np
import os

## image background
import base64

# -------------------------------------------------
# BACKGROUND IMAGE (SLIGHT BLUR ONLY)
# -------------------------------------------------
def set_bg_local(image_path):
    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <style>
        /* Background image */
        .stApp {{
            background-image:
                
                url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
   



set_bg_local("image3.jpg")

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(page_title="📊 Stock Trend Analysis", layout="wide")

# -------------------------------------------------------------------
# USER DATABASE
# -------------------------------------------------------------------
USERS_FILE = "users.csv"

if not os.path.exists(USERS_FILE):
    pd.DataFrame(
        {"email": ["admin@gmail.com"], "password": ["admin123"]}
    ).to_csv(USERS_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_user(email, password):
    df = load_users()
    df = pd.concat(
        [df, pd.DataFrame({"email": [email], "password": [password]})],
        ignore_index=True
    )
    df.to_csv(USERS_FILE, index=False)

# -------------------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

# -------------------------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------------------------
def login_page():
    
    st.markdown("<h1 style='text-align:center;'>🔐 Welcome Back</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:white;'>Login To  Stock Trend Analysis WebApp</h4>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Login")
        with st.form("login_form"):
            email = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            if st.form_submit_button("🚀 Login"):
                users = load_users()
                if ((users.email == email) & (users.password == password)).any():
                    st.session_state.logged_in = True
                    st.session_state.page = "trend"
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
        
        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("📝 Create New Account"):
            st.session_state.page = "signup"
            st.rerun()


# -------------------------------------------------------------------
# SIGNUP PAGE
# -------------------------------------------------------------------
def signup_page():
   
    st.markdown("<h1 style='text-align:center;'>📝 Create Account</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:white;'>Signup To  Stock Trend Analysis WebApp</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Sign Up")
        with st.form("signup_form"):
            email = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            confirm = st.text_input("🔒 Confirm Password", type="password")

            if st.form_submit_button("✅ Create Account"):
                users = load_users()
                if email in users["email"].values:
                    st.error("❌ Username already exists")
                elif password != confirm:
                    st.error("❌ Passwords do not match")
                else:
                    save_user(email, password)
                    st.success("🎉 Account created")
                    st.session_state.page = "login"
                    st.rerun()
        st.markdown("---")
        if st.button("🔙 Back to Login"):
            st.session_state.page = "login"
            st.rerun()

# -------------------------------------------------------------------
# DATA LOADING
# -------------------------------------------------------------------
START = "2010-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

@st.cache_data
def load_data(ticker):
    df = yf.download(ticker, START, TODAY)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.reset_index(inplace=True)
    return df

# -------------------------------------------------------------------
# MAIN APP
# -------------------------------------------------------------------
def trend_app():
    st.title("📊 Stock Trend Analysis Dashboard")

    stock = st.selectbox("Select Stock", ("AAPL", "GOOG", "MSFT", "TSLA", "AMZN"))
    df = load_data(stock)

    if df.empty:
        st.error("No data available")
        return

    # ---------------- DATE FILTER (GLOBAL) ----------------
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=df["Date"].min().date(),
            min_value=df["Date"].min().date(),
            max_value=df["Date"].max().date()
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=df["Date"].max().date(),
            min_value=df["Date"].min().date(),
            max_value=df["Date"].max().date()
        )

    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ].copy()  # avoid SettingWithCopyWarning

    # ---------------- INDICATORS (ON FILTERED DATA) ----------------
    filtered_df["SMA20"] = filtered_df["Close"].rolling(20).mean()
    filtered_df["EMA20"] = filtered_df["Close"].ewm(span=20, adjust=False).mean()
    filtered_df["MB"] = filtered_df["Close"].rolling(20).mean()
    filtered_df["STD"] = filtered_df["Close"].rolling(20).std()
    filtered_df["UB"] = filtered_df["MB"] + 2 * filtered_df["STD"]
    filtered_df["LB"] = filtered_df["MB"] - 2 * filtered_df["STD"]

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📌 Market Summary",
        "📈 Moving Averages",
        "📉 Trend Line",
        "📊 Bollinger Bands",
        "🧩 Time Series Decomposition",
        "ℹ️ About"
    ])

    # =====================================================
    # MARKET SUMMARY
    # =====================================================
    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.Open, name="Open"))
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.High, name="High"))
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.Low, name="Low"))
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.Close, name="Close"))
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # MOVING AVERAGES
    # =====================================================
    with tab2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.Close, name="Close"))
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.SMA20, name="SMA 20"))
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.EMA20, name="EMA 20"))
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # TREND LINE
    # =====================================================
    with tab3:
        x = np.arange(len(filtered_df))
        y = filtered_df["Close"].values
        coef = np.polyfit(x, y, 1)
        trend = coef[0] * x + coef[1]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.Close, name="Close"))
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=trend, name="Trend Line"))
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # BOLLINGER BANDS
    # =====================================================
    with tab4:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.Close, name="Close"))
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.UB, name="Upper Band"))
        fig.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.LB, name="Lower Band"))
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # TIME SERIES DECOMPOSITION
    # =====================================================
    with tab5:
        ts = filtered_df.set_index("Date")["Close"]
        trend_ts = ts.rolling(window=30, min_periods=1).mean()
        seasonal_ts = ts - trend_ts
        residual_ts = seasonal_ts - seasonal_ts.mean()

        # ---- TREND ----
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=trend_ts.index, y=trend_ts, name="Trend"))
        fig_trend.update_layout(title="Trend Component", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig_trend, use_container_width=True)

        # ---- SEASONAL ----
        fig_seasonal = go.Figure()
        fig_seasonal.add_trace(go.Scatter(x=seasonal_ts.index, y=seasonal_ts, name="Seasonal"))
        fig_seasonal.update_layout(title="Seasonal Component", xaxis_title="Date", yaxis_title="Seasonality")
        st.plotly_chart(fig_seasonal, use_container_width=True)

        # ---- RESIDUAL ----
        fig_residual = go.Figure()
        fig_residual.add_trace(go.Scatter(x=residual_ts.index, y=residual_ts, name="Residual"))
        fig_residual.update_layout(title="Residual Component", xaxis_title="Date", yaxis_title="Residual")
        st.plotly_chart(fig_residual, use_container_width=True)

    # =====================================================
    # ABOUT TAB
    # =====================================================
    with tab6:
        st.subheader("About the Project")
        st.markdown("""
        **Stock Trend Analysis App** is designed to help users analyze stock market trends with various technical indicators, including Moving Averages, Trend Lines, Bollinger Bands, and Time Series Decomposition.

        Users can visualize stock prices, trading volumes, and historical data interactively.

        **Founders:**
        - Arsh Agrawal
        - Prajjwal Tiwari
        - Tushar Gaur
        """)

    # ---------------- LOGOUT BUTTON AT THE BOTTOM ----------------
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()

# -------------------------------------------------------------------
# ROUTING
# -------------------------------------------------------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "trend":
    trend_app()
