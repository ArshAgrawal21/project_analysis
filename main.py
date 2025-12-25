# pip install streamlit yfinance plotly pandas numpy

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date
from plotly import graph_objs as go
import numpy as np
import os

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
# MODERN LOGIN PAGE
# -------------------------------------------------------------------
def login_page():
    st.markdown("<h1 style='text-align:center;'>🔐 Welcome Back</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:red;'>Login To  Stock Trend Analysis WebApp</h4>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Login")
        with st.form("login_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            login_btn = st.form_submit_button("🚀 Login")

            if login_btn:
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
# MODERN SIGNUP PAGE
# -------------------------------------------------------------------
def signup_page():
    st.markdown("<h1 style='text-align:center;'>📝 Create Account</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:red;'>Signup To  Stock Trend Analysis WebApp</h4>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Sign Up")
        with st.form("signup_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            confirm = st.text_input("🔒 Confirm Password", type="password")
            signup_btn = st.form_submit_button("✅ Create Account")

            if signup_btn:
                if email == "" or password == "":
                    st.error("❌ Fields cannot be empty")
                elif password != confirm:
                    st.error("❌ Passwords do not match")
                else:
                    save_user(email, password)
                    st.success("🎉 Account created successfully!")
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

# def load_data(ticker):
#     df = yf.download(ticker, START, TODAY)
#     if isinstance(df.columns, pd.MultiIndex):
#         df.columns = df.columns.get_level_values(0)
#     df.reset_index(inplace=True)
#     return df

def load_data(ticker):
    yf.set_tz_cache_location("/tmp")
    stock = yf.Ticker(ticker)
    df = stock.history(period="max", interval="1d")
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
        st.error("❌ No data available")
        return

    # Indicators
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["MB"] = df["Close"].rolling(20).mean()
    df["STD"] = df["Close"].rolling(20).std()
    df["UB"] = df["MB"] + 2 * df["STD"]
    df["LB"] = df["MB"] - 2 * df["STD"]

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📌 Market Summary",
        "📈 Moving Averages",
        "📉 Trend Line",
        "📊 Bollinger Bands",
        "🧩 Time Series Decomposition",
        "ℹ️ About"
    ])

    # ===============================================================
    # 📌 MARKET SUMMARY (OPEN, HIGH, LOW, CLOSE, VOLUME)
    # ===============================================================
    with tab1:
        st.subheader("Market Summary")
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
        ]

        # ---- PRICE GRAPH (OHLC) ----
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.Open, name="Open"))
        fig_price.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.High, name="High"))
        fig_price.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.Low, name="Low"))
        fig_price.add_trace(go.Scatter(x=filtered_df.Date, y=filtered_df.Close, name="Close"))
        fig_price.update_layout(title=f"{stock} Price Movement (OHLC)", xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig_price, use_container_width=True)

        # ---- VOLUME GRAPH ----
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Bar(x=filtered_df.Date, y=filtered_df.Volume, name="Volume"))
        fig_volume.update_layout(title=f"{stock} Trading Volume", xaxis_title="Date", yaxis_title="Volume")
        st.plotly_chart(fig_volume, use_container_width=True)

    # ===============================================================
    # 📈 MOVING AVERAGES
    # ===============================================================
    with tab2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.Date, y=df.Close, name="Close"))
        fig.add_trace(go.Scatter(x=df.Date, y=df.SMA20, name="SMA 20"))
        fig.add_trace(go.Scatter(x=df.Date, y=df.EMA20, name="EMA 20"))
        fig.update_layout(title="Moving Averages")
        st.plotly_chart(fig, use_container_width=True)

    # ===============================================================
    # 📉 TREND LINE
    # ===============================================================
    with tab3:
        x = np.arange(len(df))
        y = df["Close"].values
        coef = np.polyfit(x, y, 1)
        trend = coef[0] * x + coef[1]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.Date, y=df.Close, name="Close"))
        fig.add_trace(go.Scatter(x=df.Date, y=trend, name="Trend Line"))
        fig.update_layout(title="Trend Line Analysis")
        st.plotly_chart(fig, use_container_width=True)

    # ===============================================================
    # 📊 BOLLINGER BANDS
    # ===============================================================
    with tab4:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.Date, y=df.Close, name="Close"))
        fig.add_trace(go.Scatter(x=df.Date, y=df.UB, name="Upper Band"))
        fig.add_trace(go.Scatter(x=df.Date, y=df.LB, name="Lower Band"))
        fig.update_layout(title="Bollinger Bands")
        st.plotly_chart(fig, use_container_width=True)

    # ===============================================================
    # 🧩 TIME SERIES DECOMPOSITION
    # ===============================================================
    with tab5:
        ts = df.set_index("Date")["Close"]
        trend = ts.rolling(30).mean()
        seasonal = ts - trend
        residual = seasonal - seasonal.mean()
        st.markdown("**Trend Component**")
        st.line_chart(trend.dropna())
        st.markdown("**Seasonal Component**")
        st.line_chart(seasonal.dropna())
        st.markdown("**Residual Component**")
        st.line_chart(residual.dropna())

    # ===============================================================
    # ℹ️ ABOUT
    # ===============================================================
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

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"

# -------------------------------------------------------------------
# ROUTING
# -------------------------------------------------------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "trend":
    if st.session_state.logged_in:
        trend_app()
    else:
        login_page()
