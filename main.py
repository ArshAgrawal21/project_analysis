# =====================================================
# STREAMLIT PAGE CONFIG (MUST BE FIRST)
# =====================================================
import streamlit as st

st.set_page_config(
    page_title="📊 Stock Trend Analysis",
    layout="wide"
)

# =====================================================
# IMPORTS
# =====================================================
import pandas as pd
import yfinance as yf
from datetime import date
from plotly import graph_objs as go
import numpy as np
import os
import base64

# =====================================================
# BACKGROUND IMAGE (SAFE FOR CLOUD)
# =====================================================
def set_bg_local(image_path):
    if not os.path.exists(image_path):
        return  # Prevent crash on Streamlit Cloud

    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
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

# =====================================================
# USER DATABASE (CSV – TEMP STORAGE)
# =====================================================
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

# =====================================================
# SESSION STATE
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():
    st.markdown("<h1 style='text-align:center;'>🔐 Welcome Back</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:white;'>Login To Stock Trend Analysis WebApp</h4>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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
                    st.error("❌ Invalid credentials")

        st.markdown("---")
        if st.button("📝 Create New Account"):
            st.session_state.page = "signup"
            st.rerun()

# =====================================================
# SIGNUP PAGE
# =====================================================
def signup_page():
    st.markdown("<h1 style='text-align:center;'>📝 Create Account</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("signup_form"):
            email = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            confirm = st.text_input("🔒 Confirm Password", type="password")

            if st.form_submit_button("✅ Create Account"):
                users = load_users()
                if email in users["email"].values:
                    st.error("❌ User already exists")
                elif password != confirm:
                    st.error("❌ Passwords do not match")
                else:
                    save_user(email, password)
                    st.success("🎉 Account created")
                    st.session_state.page = "login"
                    st.rerun()

        if st.button("🔙 Back to Login"):
            st.session_state.page = "login"
            st.rerun()

# =====================================================
# DATA LOADING
# =====================================================
START = "2010-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

@st.cache_data(show_spinner=False)
def load_data(ticker):
    df = yf.download(ticker, START, TODAY)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.reset_index(inplace=True)
    return df

# =====================================================
# MAIN DASHBOARD
# =====================================================
def trend_app():
    st.title("📊 Stock Trend Analysis Dashboard")

    stock = st.selectbox("Select Stock", ["AAPL", "GOOG", "MSFT", "TSLA", "AMZN"])
    df = load_data(stock)

    if df.empty:
        st.error("No data available")
        return

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", df.Date.min())
    with col2:
        end_date = st.date_input("End Date", df.Date.max())

    df = df[(df.Date >= pd.to_datetime(start_date)) & (df.Date <= pd.to_datetime(end_date))]

    df["SMA20"] = df.Close.rolling(20).mean()
    df["EMA20"] = df.Close.ewm(span=20).mean()
    df["STD"] = df.Close.rolling(20).std()
    df["UB"] = df["SMA20"] + 2 * df["STD"]
    df["LB"] = df["SMA20"] - 2 * df["STD"]

    tabs = st.tabs([
        "📌 Market Summary",
        "📈 Moving Averages",
        "📉 Trend Line",
        "📊 Bollinger Bands",
        "🧩 Time Series Decomposition",
        "ℹ️ About"
    ])

    with tabs[0]:
        fig = go.Figure()
        for col in ["Open", "High", "Low", "Close"]:
            fig.add_trace(go.Scatter(x=df.Date, y=df[col], name=col))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.Date, y=df.Close, name="Close"))
        fig.add_trace(go.Scatter(x=df.Date, y=df.SMA20, name="SMA 20"))
        fig.add_trace(go.Scatter(x=df.Date, y=df.EMA20, name="EMA 20"))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        x = np.arange(len(df))
        trend = np.poly1d(np.polyfit(x, df.Close, 1))(x)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.Date, y=df.Close, name="Close"))
        fig.add_trace(go.Scatter(x=df.Date, y=trend, name="Trend Line"))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.Date, y=df.Close, name="Close"))
        fig.add_trace(go.Scatter(x=df.Date, y=df.UB, name="Upper Band"))
        fig.add_trace(go.Scatter(x=df.Date, y=df.LB, name="Lower Band"))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[4]:
        ts = df.set_index("Date")["Close"]
        trend_ts = ts.rolling(30).mean()
        seasonal = ts - trend_ts
        residual = seasonal - seasonal.mean()

        st.line_chart(trend_ts, height=200)
        st.line_chart(seasonal, height=200)
        st.line_chart(residual, height=200)

    with tabs[5]:
        st.markdown("""
        **Founders**
        - Arsh Agrawal  
        - Prajjwal Tiwari  
        - Tushar Gaur  
        """)

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()

# =====================================================
# ROUTING
# =====================================================
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
else:
    trend_app()
