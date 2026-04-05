# pip install streamlit yfinance plotly pandas numpy

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date
from plotly import graph_objs as go
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
    
# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(
    page_title="📊 Stock Trend Analysis Pro",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# CUSTOM CSS STYLES
# -------------------------------------------------------------------
st.markdown("""
<style>
    /* Main background and text colors */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
        color: white;
    }
    
    /* Title styling */
    .title {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Card styling */
    .metric-card {
        # background: rgba(255, 255, 255, 0.95);
        # border-radius: 15px;
        # padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        color:black;
        border: none;
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    }
    
    /* Recommendation box styling */
    .recommendation-box {
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        text-align: center;
        border: 3px solid #333;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Success/Warning/Error colors */
    .success { background: linear-gradient(135deg, #4CAF50, #45a049); }
    .warning { background: linear-gradient(135deg, #FF9800, #F57C00); }
    .danger { background: linear-gradient(135deg, #f44336, #d32f2f); }
    .info { background: linear-gradient(135deg, #2196F3, #1976D2); }
    
    /* Chart styling */
    .js-plotly-plot .plotly .modebar {
        background: rgba(255,255,255,0.8);
        border-radius: 5px;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 20px;
        background: rgba(0,0,0,0.3);
        border-radius: 10px;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

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

def load_data(ticker):
    df = yf.download(ticker, START, TODAY)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.reset_index(inplace=True)
    return df

# def load_data(ticker):
#     yf.set_tz_cache_location("/tmp")
#     stock = yf.Ticker(ticker)
#     df = stock.history(period="max", interval="1d")
#     df.reset_index(inplace=True)
#     return df

# -------------------------------------------------------------------
# PRICE PREDICTION & TREND ANALYSIS
# -------------------------------------------------------------------
def predict_prices(df, days_ahead=30):
    """Predict stock prices using Linear Regression"""
    df_temp = df.copy()
    df_temp['Days'] = np.arange(len(df_temp))
    
    X = df_temp[['Days']].values
    y = df_temp['Close'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    last_day = X[-1][0]
    future_days = np.arange(last_day + 1, last_day + days_ahead + 1).reshape(-1, 1)
    predictions = model.predict(future_days)
    
    future_dates = pd.date_range(start=df_temp['Date'].max() + pd.Timedelta(days=1), periods=days_ahead)
    
    return future_dates, predictions

def analyze_trend(df):
    """Analyze current trend direction and strength"""
    recent_data = df.tail(60)  # Last 60 days for better trend analysis
    
    # Calculate trend using linear regression
    x = np.arange(len(recent_data))
    y = recent_data['Close'].values
    slope = np.polyfit(x, y, 1)[0]
    
    # Calculate momentum (30 days)
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-30]
    momentum = ((current_price - prev_price) / prev_price) * 100
    
    # Calculate RSI (Relative Strength Index) - improved version
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    
    rs = avg_gain / avg_loss.replace(0, 0.001)  # Avoid division by zero
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    
    return {
        'slope': slope,
        'momentum': momentum,
        'current_price': current_price,
        'rsi': current_rsi
    }

def generate_recommendation(df, predictions):
    """Generate BUY/SELL/HOLD recommendation"""
    trend = analyze_trend(df)
    
    current_price = trend['current_price']
    predicted_avg = predictions.mean()
    predicted_final = predictions[-1]
    momentum = trend['momentum']
    rsi = trend['rsi']
    
    price_change_pct = ((predicted_final - current_price) / current_price) * 100
    
    # Scoring system (adjusted for better balance)
    score = 0
    reasons = []
    
    # Price trend analysis (weighted more heavily)
    if predicted_final > current_price * 1.05:  # 5%+ increase
        score += 3
        reasons.append(f"✅ Strong price increase predicted ({price_change_pct:.2f}%)")
    elif predicted_final > current_price:
        score += 2
        reasons.append(f"✅ Price increase predicted ({price_change_pct:.2f}%)")
    elif predicted_final < current_price * 0.95:  # 5%+ decrease
        score -= 3
        reasons.append(f"❌ Significant price decrease predicted ({price_change_pct:.2f}%)")
    elif predicted_final < current_price:
        score -= 2
        reasons.append(f"❌ Price decrease predicted ({price_change_pct:.2f}%)")
    else:
        reasons.append(f"⚖️ Price predicted to remain stable ({price_change_pct:.2f}%)")
    
    # Momentum analysis
    if momentum > 10:
        score += 2
        reasons.append(f"✅ Strong positive momentum ({momentum:.2f}%)")
    elif momentum > 2:
        score += 1
        reasons.append(f"✅ Positive momentum ({momentum:.2f}%)")
    elif momentum < -10:
        score -= 2
        reasons.append(f"❌ Strong negative momentum ({momentum:.2f}%)")
    elif momentum < -2:
        score -= 1
        reasons.append(f"❌ Negative momentum ({momentum:.2f}%)")
    else:
        reasons.append(f"⚖️ Neutral momentum ({momentum:.2f}%)")
    
    # RSI analysis
    if rsi < 30:
        score += 2
        reasons.append("✅ RSI oversold - strong buying opportunity")
    elif rsi < 45:
        score += 1
        reasons.append("✅ RSI in buying territory")
    elif rsi > 70:
        score -= 2
        reasons.append("❌ RSI overbought - potential sell signal")
    elif rsi > 55:
        score -= 1
        reasons.append("❌ RSI in selling territory")
    else:
        reasons.append(f"⚖️ RSI neutral ({rsi:.2f})")
    
    # Trend direction (longer term)
    if trend['slope'] > 0.1:  # Strong uptrend
        score += 2
        reasons.append("✅ Strong uptrend detected")
    elif trend['slope'] > 0:
        score += 1
        reasons.append("✅ Uptrend detected")
    elif trend['slope'] < -0.1:  # Strong downtrend
        score -= 2
        reasons.append("❌ Strong downtrend detected")
    elif trend['slope'] < 0:
        score -= 1
        reasons.append("❌ Downtrend detected")
    else:
        reasons.append("⚖️ Sideways trend")
    
    # Generate recommendation with adjusted thresholds
    if score >= 4:
        recommendation = "🟢 STRONG BUY"
        color = "#00ff00"  # Bright green
        confidence = min(95, 60 + (score * 5))
    elif score >= 2:
        recommendation = "🟢 BUY"
        color = "#90EE90"  # Light green
        confidence = min(85, 50 + (score * 5))
    elif score <= -4:
        recommendation = "🔴 STRONG SELL"
        color = "#ff0000"  # Bright red
        confidence = min(95, 60 + (abs(score) * 5))
    elif score <= -2:
        recommendation = "🔴 SELL"
        color = "#FFB6C1"  # Light red
        confidence = min(85, 50 + (abs(score) * 5))
    else:
        recommendation = "🟡 HOLD"
        color = "#FFA500"  # Orange
        confidence = max(30, 50 + (score * 5))
    
    return {
        'recommendation': recommendation,
        'color': color,
        'score': score,
        'confidence': confidence,
        'reasons': reasons,
        'price_change_pct': price_change_pct
    }



# -------------------------------------------------------------------
# MAIN APP
# -------------------------------------------------------------------
def trend_app():
    # Header Section
    st.markdown('<h1 class="title">🚀 Stock Trend Analysis Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2em; color: rgba(255,255,255,0.8); margin-bottom: 30px;">Advanced AI-Powered Stock Analysis & Trading Signals</p>', unsafe_allow_html=True)
    
    # Stock Selection Section
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 📈 Select Stock")
        stock = st.selectbox("Stock Symbol", ("AAPL", "GOOG", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX", "AMD", "CRM", "ORCL", "INTC", "CSCO", "ADBE", "PYPL", "UBER", "SPOT", "SQ", "SHOP", "COIN"), label_visibility="collapsed")
    
    # Load data immediately after stock selection
    df = load_data(stock)
    
    with col2:
        st.markdown("### 📊 Current Price")
        try:
            current_price = df['Close'].iloc[-1]
            st.metric("", f"${current_price:.2f}", 
                     f"{((current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100):+.2f}%")
        except:
            st.metric("", "Loading...")
    
    with col3:
        st.markdown("### 📅 Data Range")
        st.metric("", f"{len(df)} Days", f"Since {df['Date'].min().strftime('%Y')}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Stats Row
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 📈 52W High")
        high_52w = df['High'].tail(252).max() if len(df) >= 252 else df['High'].max()
        st.metric("", f"${high_52w:.2f}")
    
    with col2:
        st.markdown("### 📉 52W Low")
        low_52w = df['Low'].tail(252).min() if len(df) >= 252 else df['Low'].min()
        st.metric("", f"${low_52w:.2f}")
    
    with col3:
        st.markdown("### 📊 Avg Volume")
        avg_vol = df['Volume'].tail(30).mean()
        st.metric("", f"{avg_vol:,.0f}")
    
    with col4:
        st.markdown("### 📈 Volatility")
        returns = df['Close'].pct_change().tail(30).std() * 100
        st.metric("", f"{returns:.2f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)

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

    col1, col2 = st.columns(2)
        
    with col1:
            # st.markdown("#### 📅 Time Period Selection")
            start_date = st.date_input(
                "Start Date",
                value=df["Date"].min().date(),
                min_value=df["Date"].min().date(),
                max_value=df["Date"].max().date(),
                key="overview_start"
            )
        
    with col2:
            end_date = st.date_input(
                "End Date", 
                value=df["Date"].max().date(),
                min_value=df["Date"].min().date(),
                max_value=df["Date"].max().date(),
                key="overview_end"
            )
        
    filtered_df = df[
            (df["Date"] >= pd.to_datetime(start_date)) & 
            (df["Date"] <= pd.to_datetime(end_date))
        ]
    
    # Enhanced Tabs with better styling
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Market Overview",
        "📈 Technical Analysis", 
        "📉 Trend Patterns",
        "🎯 Bollinger Signals",
        "🧩 Seasonal Trends",
        "🚀 AI Predictions",
        "ℹ️ About & Help"
    ])
     
    # ===============================================================
    # 📊 MARKET OVERVIEW (Enhanced)
    # ===============================================================
    with tab1:
        st.markdown("### 📊 Comprehensive Market Analysis")
        
       
        
        # Enhanced Price Chart
        st.markdown("#### 💹 Price Movement Analysis")
        fig_price = go.Figure()
        
        # Add candlestick chart
        fig_price.add_trace(go.Candlestick(
            x=filtered_df.Date,
            open=filtered_df.Open,
            high=filtered_df.High,
            low=filtered_df.Low,
            close=filtered_df.Close,
            name="OHLC"
        ))
        
        fig_price.update_layout(
            title=f"{stock} Price Action (Candlestick Chart)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig_price, use_container_width=True)
        
        # Volume Analysis
        st.markdown("#### 📊 Volume Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_volume = go.Figure()
            fig_volume.add_trace(go.Bar(
                x=filtered_df.Date, 
                y=filtered_df.Volume, 
                name="Volume",
                marker_color='skyblue'
            ))
            fig_volume.update_layout(
                title="Trading Volume",
                template="plotly_dark",
                height=300
            )
            st.plotly_chart(fig_volume, use_container_width=True)
        
        with col2:
            # Volume metrics
            st.markdown("### 📈 Volume Metrics")
            avg_volume = filtered_df['Volume'].mean()
            max_volume = filtered_df['Volume'].max()
            min_volume = filtered_df['Volume'].min()
            
            st.metric("Average Volume", f"{avg_volume:,.0f}")
            st.metric("Peak Volume", f"{max_volume:,.0f}")
            st.metric("Lowest Volume", f"{min_volume:,.0f}")
            
            # Volume trend
            recent_vol = filtered_df['Volume'].tail(30).mean()
            older_vol = filtered_df['Volume'].head(len(filtered_df)-30).mean() if len(filtered_df) > 30 else avg_volume
            vol_change = ((recent_vol - older_vol) / older_vol) * 100 if older_vol > 0 else 0
            
            st.metric("Volume Trend (30d)", f"{vol_change:+.1f}%", 
                     delta=f"{vol_change:+.1f}%" if abs(vol_change) > 5 else "Stable")
    # ===============================================================
    # 📈 TECHNICAL ANALYSIS
    # ===============================================================
    with tab2:
        st.markdown("### 📈 Advanced Technical Indicators")
        
        # Moving Averages Section
        st.subheader("Moving Average & Crossover Signals")

        fig_ma = go.Figure()

        # Close Price
        fig_ma.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=filtered_df.Close,
            name="Close Price",
            line=dict(color="white")
        ))

        # SMA
        fig_ma.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=filtered_df.SMA20,
            name="SMA 20",
            line=dict(color="orange")
        ))

        # EMA
        fig_ma.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=filtered_df.EMA20,
            name="EMA 20",
            line=dict(color="cyan")
        ))

        # -----------------------------
        # BUY SIGNAL LOOP
        # -----------------------------
        sma_buy = []
        ema_buy = []

        for i in range(len(filtered_df)):

            sma_buy.append(None)
            ema_buy.append(None)

            if i == 0:
                continue

            # SMA crossover BUY
            if (
                filtered_df['Close'].iloc[i] > filtered_df['SMA20'].iloc[i]
                and filtered_df['Close'].iloc[i-1] <= filtered_df['SMA20'].iloc[i-1]
            ):
                sma_buy[i] = filtered_df['Close'].iloc[i]

            # EMA crossover BUY
            if (
                filtered_df['Close'].iloc[i] > filtered_df['EMA20'].iloc[i]
                and filtered_df['Close'].iloc[i-1] <= filtered_df['EMA20'].iloc[i-1]
            ):
                ema_buy[i] = filtered_df['Close'].iloc[i]

        # -----------------------------
        # PLOT BUY SIGNALS
        # -----------------------------
        fig_ma.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=sma_buy,
            mode='markers',
            name='SMA Buy',
            marker=dict(color='green', size=9, symbol="triangle-up")
        ))

        fig_ma.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=ema_buy,
            mode='markers',
            name='EMA Buy',
            marker=dict(color='blue', size=9, symbol="triangle-up")
        ))

        # Layout (ONLY THIS CHART)
        fig_ma.update_layout(
            title="Moving Average Crossover Strategy",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=600
        )

        # IMPORTANT: inside tab2
        st.plotly_chart(fig_ma, use_container_width=True)
        
    with tab3:

        st.subheader("Trend Line Analysis")

        # create index
        x = np.arange(len(filtered_df))
        y = filtered_df["Close"].values

        # linear regression trend
        coef = np.polyfit(x, y, 1)
        trend = coef[0] * x + coef[1]

        # trend direction
        slope = coef[0]

        if slope > 0:
            trend_text = "UPTREND 📈 (BUY)"
            color = "green"
        elif slope < 0:
            trend_text = "DOWNTREND 📉 (SELL)"
            color = "red"
        else:
            trend_text = "SIDEWAYS ➖ (HOLD)"
            color = "yellow"

        st.markdown(f"### Trend Direction: {trend_text}")

        # plot
        fig = go.Figure()

        # close price
        fig.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=filtered_df.Close,
            name="Close Price",
            line=dict(color="white")
        ))

        # trend line
        fig.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=trend,
            name="Trend Line",
            line=dict(color=color, width=3)
        ))

        fig.update_layout(
            title="Stock Trend Line",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    # ===============================================================
    # 📊 BOLLINGER BANDS
    # ===============================================================
    with tab4:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=filtered_df.Close,
            name="Close"
        ))

        fig.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=filtered_df.UB,
            name="Upper Band"
        ))

        fig.add_trace(go.Scatter(
            x=filtered_df.Date,
            y=filtered_df.LB,
            name="Lower Band"
        ))

        fig.update_layout(
            title="Bollinger Bands",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    # ===============================================================
    # 🧩 TIME SERIES DECOMPOSITION
    # ===============================================================
    with tab5:
        ts = filtered_df.set_index("Date")["Close"]

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
    # 🚀 AI PREDICTIONS & SIGNALS 
    # ===============================================================
        with tab6:

            left, center, right = st.columns([0.1,3,0.1])

            with center:
                st.markdown("### 🚀 AI-Powered Trading Signals")
                st.markdown("**Advanced Algorithm**: Combining ML predictions with technical analysis for optimal trading decisions")
                
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)

                st.markdown("#### ⏱️ Prediction Horizon")
                days_ahead = st.slider("Prediction Days", 7, 90, 30)

                st.markdown("#### 🎯 Generate Analysis")
                run_ai = st.button(
                    "🚀 Run AI Analysis",
                    type="primary",
                    use_container_width=True
                )

                if run_ai:
                    with st.spinner("🤖 AI analyzing market data..."):
                        import time
                        time.sleep(1)

                        future_dates, predictions = predict_prices(df, days_ahead)
                        recommendation = generate_recommendation(df, predictions)

                        pred_df = pd.DataFrame({
                            'Date': future_dates,
                            'Predicted_Close': predictions
                        })

                        st.markdown("---")

                        st.markdown(f"""
                        <div class='recommendation-box' style='background: {recommendation["color"]}; text-align:center;'>
                            <h1 style='color: #000;'>{recommendation['recommendation']}</h1>
                            <p style='color: #000;'>Confidence: {recommendation['confidence']:.0f}%</p>
                            <p style='color: #000;'>Expected Change: {recommendation['price_change_pct']:+.2f}%</p>
                            <p style='color: #000;'>AI Score: {recommendation['score']:+d}/8</p>
                        </div>
                        """, unsafe_allow_html=True)                    
                    # AI Analysis Breakdown
                    st.markdown("### 🤖 AI Analysis Breakdown")
                    for reason in recommendation['reasons']:
                        st.write(reason)
                    
                    # Enhanced Prediction Chart
                    st.markdown("### 📈 AI Price Prediction Chart")
                    fig_pred = go.Figure()
                    fig_pred.add_trace(go.Scatter(
                        x=df.Date, y=df.Close, name="Historical Prices", 
                        line=dict(color='white', width=3),
                        fill='tozeroy', fillcolor='rgba(255,255,255,0.1)'
                    ))
                    fig_pred.add_trace(go.Scatter(
                        x=pred_df.Date, y=pred_df.Predicted_Close, name="AI Predictions", 
                        line=dict(color='#FF6B6B', width=3, dash='dash')
                    ))
                    
                    # Add confidence interval
                    upper_bound = predictions * 1.05  # 5% upper bound
                    lower_bound = predictions * 0.95  # 5% lower bound
                    
                    fig_pred.add_trace(go.Scatter(
                        x=list(pred_df.Date) + list(pred_df.Date[::-1]),
                        y=list(upper_bound) + list(lower_bound[::-1]),
                        fill='toself',
                        fillcolor='rgba(255, 107, 107, 0.2)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Confidence Interval (5%)'
                    ))
                    
                    fig_pred.update_layout(
                        title=f"{stock} - AI Price Prediction & Confidence Interval",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        template="plotly_dark",
                        height=500,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_pred, use_container_width=True)
                    
                    # Prediction Statistics Dashboard
                    st.markdown("### 📊 Prediction Analytics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}")
                    
                    with col2:
                        avg_pred = predictions.mean()
                        st.metric("Avg Prediction", f"${avg_pred:.2f}")
                    
                    with col3:
                        price_change = predictions[-1] - df['Close'].iloc[-1]
                        pct_change = (price_change / df['Close'].iloc[-1]) * 100
                        st.metric("Price Change", f"${price_change:.2f}", f"{pct_change:+.2f}%")
                    
                    with col4:
                        volatility = predictions.std() / predictions.mean() * 100
                        st.metric("Prediction Risk", f"{volatility:.2f}%")
                    
                    # Technical Indicators Dashboard
                    st.markdown("### 📉 Technical Indicators")
                    trend_data = analyze_trend(df)
                    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
                    
                    with t_col1:
                        trend_dir = "📈 Bullish" if trend_data['slope'] > 0 else "📉 Bearish"
                        st.metric("Trend Direction", trend_dir)
                    
                    with t_col2:
                        st.metric("Momentum (30d)", f"{trend_data['momentum']:+.2f}%")
                    
                    with t_col3:
                        rsi_status = "Oversold" if trend_data['rsi'] < 30 else "Overbought" if trend_data['rsi'] > 70 else "Neutral"
                        st.metric("RSI Status", f"{trend_data['rsi']:.2f}")
                    
                    with t_col4:
                        st.metric("RSI Signal", rsi_status)
                    
                    # Detailed Predictions Table
                    st.markdown("### 📋 Detailed AI Predictions")
                    st.dataframe(
                        pred_df.style.format({'Predicted_Close': '${:.2f}'}),
                        use_container_width=True
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)
    # ===============================================================
    # ℹ️ ABOUT & HELP
    # ===============================================================
    with tab7:
        st.markdown("### 📖 About Stock Trend Analysis Pro")
        
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h4>🎯 What We Do</h4>
        <p><strong>Stock Trend Analysis Pro</strong> is an advanced AI-powered platform designed to help investors and traders make informed decisions through comprehensive technical analysis and machine learning predictions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚀 Key Features")
            st.markdown("""
            - **📊 Real-time Market Data** - Live stock prices and historical data
            - **🤖 AI Price Predictions** - Machine learning based forecasting
            - **📈 Technical Indicators** - Moving averages, RSI, Bollinger Bands
            - **🎯 Smart Buy/Sell Signals** - AI-generated trading recommendations
            - **📉 Advanced Charts** - Interactive candlestick and trend charts
            - **📋 Comprehensive Analytics** - Volume analysis and market insights
            """)
        
        with col2:
            st.markdown("#### 🛠️ Technical Stack")
            st.markdown("""
            - **Frontend**: Streamlit (Python)
            - **Data Source**: Yahoo Finance API
            - **Visualization**: Plotly.js
            - **AI/ML**: Scikit-learn (Linear Regression)
            - **Analysis**: Pandas, NumPy
            - **Styling**: Custom CSS
            """)
        
        st.markdown("---")
        
        st.markdown("#### 👥 Meet the Founders")
        founder_col1, founder_col2, founder_col3 = st.columns(3)
        
        with founder_col1:
            st.markdown("""
            <div style='text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>
            <h3>Arsh Agrawal</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with founder_col2:
            st.markdown("""
            <div style='text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>
            <h3>Prajjwal Tiwari</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with founder_col3:
            st.markdown("""
            <div style='text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>
            <h3>Tushar Gaur</h3>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("#### ⚠️ Important Disclaimer")
        st.markdown("""
        <div style='background: rgba(255,0,0,0.1); border: 1px solid rgba(255,0,0,0.3); padding: 15px; border-radius: 10px;'>
        <strong>This application is for educational and informational purposes only.</strong>
        
        - Not intended as financial advice or investment recommendations
        - Past performance does not guarantee future results
        - Always conduct your own research and consult with financial professionals
        - We are not responsible for any investment decisions made based on this tool
        </div>
        """, unsafe_allow_html=True)
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: rgba(255,255,255,0.7);'>
        <h3 style='margin-bottom: 10px;'>🚀 Stock Trend Analysis Pro</h3>
        <p><strong>Powered by AI & Advanced Technical Analysis</strong></p>
        <p>Built with ❤️ by Arsh Agrawal, Prajjwal Tiwari & Tushar Gaur</p>
        <p style='font-size: 0.9em; margin-top: 15px;'>⚠️ <em>Disclaimer: This tool is for educational purposes only. Not financial advice. Always do your own research.</em></p>
        <p style='font-size: 0.8em; margin-top: 10px;'>Data provided by Yahoo Finance | Last updated: {current_date}</p>
    </div>
    """.format(current_date=date.today().strftime("%B %d, %Y")), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
