import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import os

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Market Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    /* Main background */
    .stApp {
        background-color: #0A0E1A;
        color: #E8EDF5;
        font-family: 'DM Sans', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F1525;
        border-right: 1px solid #1E2A45;
    }

    /* Title */
    .main-title {
        font-family: 'Space Mono', monospace;
        font-size: 2.2rem;
        font-weight: 700;
        color: #4DFFB4;
        letter-spacing: -1px;
        margin-bottom: 0;
    }

    .sub-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 1rem;
        color: #5A6A8A;
        margin-top: 0;
        margin-bottom: 2rem;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #0F1525 0%, #151E35 100%);
        border: 1px solid #1E2A45;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: border-color 0.3s;
    }

    .kpi-card:hover {
        border-color: #4DFFB4;
    }

    .kpi-label {
        font-size: 0.75rem;
        color: #5A6A8A;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        font-family: 'Space Mono', monospace;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4DFFB4;
        font-family: 'Space Mono', monospace;
    }

    .kpi-value.red { color: #FF4D6A; }
    .kpi-value.blue { color: #4D9FFF; }
    .kpi-value.yellow { color: #FFD74D; }

    /* Section headers */
    .section-header {
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
        color: #5A6A8A;
        letter-spacing: 3px;
        text-transform: uppercase;
        border-bottom: 1px solid #1E2A45;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Ticker badge */
    .ticker-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        margin: 2px;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Metric styling */
    [data-testid="stMetric"] {
        background: #0F1525;
        border: 1px solid #1E2A45;
        border-radius: 12px;
        padding: 1rem;
    }

    [data-testid="stMetricValue"] {
        color: #4DFFB4;
        font-family: 'Space Mono', monospace;
    }

    /* Divider */
    hr {
        border-color: #1E2A45;
    }
/* ── MOBILE RESPONSIVE ── */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.4rem !important;
            letter-spacing: -0.5px;
        }
        .sub-title {
            font-size: 0.8rem !important;
        }
        .kpi-card {
            padding: 0.8rem !important;
        }
        .kpi-value {
            font-size: 1.3rem !important;
        }
        .kpi-label {
            font-size: 0.65rem !important;
        }
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
    }
 /* Force sidebar toggle button to always show */
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    button[kind="header"] {
        display: block !important;
        visibility: visible !important;
    }   
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    db_path = 'db/aktien.db'
    
    if not os.path.exists(db_path):
        st.error("❌ aktien.db not found in db/ folder. See README.")
        st.stop()

    conn = sqlite3.connect(db_path)

    # Main price data
    df = pd.read_sql('''
        SELECT datum, ticker, open_kurs, hoch, tief, schluss, volumen
        FROM kurse
        ORDER BY ticker, datum
    ''', conn)

    # Metrics table (MA, volatility, daily return)
    df_kz = pd.read_sql('''
        SELECT datum, ticker, MA_7, MA_30, MA_90, rendite, volatilitaet
        FROM kennzahlen
        ORDER BY ticker, datum
    ''', conn)

    conn.close()

    df['datum'] = pd.to_datetime(df['datum'], utc=True).dt.tz_localize(None)
    df_kz['datum'] = pd.to_datetime(df_kz['datum'], utc=True).dt.tz_localize(None)

    # Merge so charts can use MAs directly
    df = df.merge(df_kz, on=['datum', 'ticker'], how='left')

    return df


df = load_data()
st.sidebar.success(f"✅ DB loaded: {len(df):,} rows")
st.sidebar.caption(f"Tickers: {', '.join(df['ticker'].unique())}")

# Normalize column names
if 'close' in df.columns and 'schluss' not in df.columns:
    df.rename(columns={'close': 'schluss'}, inplace=True)
if 'date' in df.columns and 'datum' not in df.columns:
    df.rename(columns={'date': 'datum'}, inplace=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="main-title">📈 STOCKS</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">2020 — 2024 Analysis</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Ticker selection
    st.markdown('<p class="section-header">Select Stocks</p>', unsafe_allow_html=True)
    all_tickers = sorted(df['ticker'].unique().tolist())

    ticker_colors = {
        'AAPL':   '#4DFFB4',
        'MSFT':   '#4D9FFF',
        'TSLA':   '#FF4D6A',
        'SAP.DE': '#FFD74D',
        'SAP':    '#FFD74D',
    }

    selected_tickers = st.multiselect(
        "Tickers",
        options=all_tickers,
        default=all_tickers,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Date range
    st.markdown('<p class="section-header">Date Range</p>', unsafe_allow_html=True)
    min_date = df['datum'].min().date()
    max_date = df['datum'].max().date()

    start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
    end_date   = st.date_input("To",   value=max_date, min_value=min_date, max_value=max_date)

    st.markdown("---")

    # Chart type
    st.markdown('<p class="section-header">Chart Type</p>', unsafe_allow_html=True)
    chart_type = st.radio(
        "Chart",
        ["Line Chart", "Area Chart", "Bar Chart"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown('<p style="color:#5A6A8A;font-size:0.75rem;text-align:center;">IBM Data Science Project<br>Built with Python + Streamlit</p>', unsafe_allow_html=True)


# ── FILTER DATA ───────────────────────────────────────────────────────────────
if not selected_tickers:
    st.error("Please select at least one stock!")
    st.stop()

mask = (
    df['ticker'].isin(selected_tickers) &
    (df['datum'].dt.date >= start_date) &
    (df['datum'].dt.date <= end_date)
)
filtered = df[mask].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">STOCK MARKET ANALYSIS</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Interactive Dashboard · 2020–2024 · Mohamed Hizem Data Science Project</p>', unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Key Metrics</p>', unsafe_allow_html=True)

kpi_cols = st.columns([1,1,1,1], gap="small")

for i, ticker in enumerate(selected_tickers[:4]):
    t_data = filtered[filtered['ticker'] == ticker]
    if len(t_data) == 0:
        continue
    start_price = t_data['schluss'].iloc[0]
    end_price   = t_data['schluss'].iloc[-1]
    ret         = ((end_price - start_price) / start_price * 100)
    max_price   = t_data['schluss'].max()
    color_class = 'red' if ret < 0 else ''
    color       = ticker_colors.get(ticker, '#4DFFB4')

    with kpi_cols[i % 4]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{ticker}</div>
            <div class="kpi-value" style="color:{color};">{ret:+.1f}%</div>
            <div style="color:#5A6A8A;font-size:0.8rem;margin-top:0.3rem;">
                ${end_price:.2f} · Max ${max_price:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── MAIN CHART ────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Price History</p>', unsafe_allow_html=True)

fig = go.Figure()

for ticker in selected_tickers:
    t_data = filtered[filtered['ticker'] == ticker].sort_values('datum')
    color  = ticker_colors.get(ticker, '#4DFFB4')

    if chart_type == "Line Chart":
        fig.add_trace(go.Scatter(
            x=t_data['datum'],
            y=t_data['schluss'],
            name=ticker,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{ticker}</b><br>Date: %{{x|%Y-%m-%d}}<br>Price: $%{{y:.2f}}<extra></extra>"
        ))

    elif chart_type == "Area Chart":
        fig.add_trace(go.Scatter(
            x=t_data['datum'],
            y=t_data['schluss'],
            name=ticker,
            fill='tozeroy',
            line=dict(color=color, width=2),
            fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)",
            hovertemplate=f"<b>{ticker}</b><br>Date: %{{x|%Y-%m-%d}}<br>Price: $%{{y:.2f}}<extra></extra>"
        ))

    elif chart_type == "Bar Chart":
        monthly = t_data.resample('ME', on='datum')['schluss'].mean().reset_index()
        fig.add_trace(go.Bar(
            x=monthly['datum'],
            y=monthly['schluss'],
            name=ticker,
            marker_color=color,
            hovertemplate=f"<b>{ticker}</b><br>Month: %{{x|%Y-%m}}<br>Avg: $%{{y:.2f}}<extra></extra>"
        ))

fig.update_layout(
    plot_bgcolor='#0A0E1A',
    paper_bgcolor='#0A0E1A',
    font=dict(color='#5A6A8A', family='DM Sans'),
    legend=dict(
        bgcolor='#0F1525',
        bordercolor='#1E2A45',
        borderwidth=1,
        font=dict(color='#E8EDF5')
    ),
    xaxis=dict(
        gridcolor='#1E2A45',
        showgrid=True,
        zeroline=False,
        color='#5A6A8A'
    ),
    yaxis=dict(
        gridcolor='#1E2A45',
        showgrid=True,
        zeroline=False,
        color='#5A6A8A',
        title='Price (USD / EUR)'
    ),
    hovermode='x unified',
    height=450,
    margin=dict(l=0, r=0, t=10, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ── BOTTOM ROW ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

# ── RETURNS BAR CHART ─────────────────────────────────────────────────────────
with col1:
    st.markdown('<p class="section-header">Total Return by Stock</p>', unsafe_allow_html=True)

    returns_data = []
    for ticker in selected_tickers:
        t_data = filtered[filtered['ticker'] == ticker]
        if len(t_data) < 2:
            continue
        start = t_data['schluss'].iloc[0]
        end   = t_data['schluss'].iloc[-1]
        ret   = (end - start) / start * 100
        returns_data.append({'Ticker': ticker, 'Return (%)': round(ret, 2)})

    if returns_data:
        ret_df = pd.DataFrame(returns_data).sort_values('Return (%)', ascending=True)
        colors_list = [ticker_colors.get(t, '#4DFFB4') for t in ret_df['Ticker']]

        fig2 = go.Figure(go.Bar(
            x=ret_df['Return (%)'],
            y=ret_df['Ticker'],
            orientation='h',
            marker_color=colors_list,
            hovertemplate="<b>%{y}</b><br>Return: %{x:.2f}%<extra></extra>"
        ))
        fig2.update_layout(
            plot_bgcolor='#0A0E1A',
            paper_bgcolor='#0A0E1A',
            font=dict(color='#5A6A8A', family='DM Sans'),
            xaxis=dict(gridcolor='#1E2A45', color='#5A6A8A', title='Return (%)'),
            yaxis=dict(gridcolor='#1E2A45', color='#E8EDF5'),
            height=300,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── VOLATILITY CHART ──────────────────────────────────────────────────────────
with col2:
    st.markdown('<p class="section-header">Average Price by Stock</p>', unsafe_allow_html=True)

    avg_data = []
    for ticker in selected_tickers:
        t_data = filtered[filtered['ticker'] == ticker]
        if len(t_data) == 0:
            continue
        avg_data.append({
            'Ticker': ticker,
            'Average': round(t_data['schluss'].mean(), 2),
            'Max':     round(t_data['schluss'].max(), 2),
            'Min':     round(t_data['schluss'].min(), 2),
        })

    if avg_data:
        avg_df = pd.DataFrame(avg_data)
        colors_list2 = [ticker_colors.get(t, '#4DFFB4') for t in avg_df['Ticker']]

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name='Average',
            x=avg_df['Ticker'],
            y=avg_df['Average'],
            marker_color=colors_list2,
            hovertemplate="<b>%{x}</b><br>Avg: $%{y:.2f}<extra></extra>"
        ))
        fig3.update_layout(
            plot_bgcolor='#0A0E1A',
            paper_bgcolor='#0A0E1A',
            font=dict(color='#5A6A8A', family='DM Sans'),
            xaxis=dict(gridcolor='#1E2A45', color='#E8EDF5'),
            yaxis=dict(gridcolor='#1E2A45', color='#5A6A8A', title='Price (USD/EUR)'),
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)

# ── DATA TABLE ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-header">Raw Data</p>', unsafe_allow_html=True)

show_data = st.toggle("Show raw data table", value=False)
if show_data:
    display_df = filtered[['datum', 'ticker', 'schluss']].copy()
    display_df.columns = ['Date', 'Ticker', 'Close Price']
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    display_df['Close Price'] = display_df['Close Price'].round(2)
    st.dataframe(
        display_df.sort_values('Date', ascending=False),
        use_container_width=True,
        height=300
    )

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style="text-align:center;color:#5A6A8A;font-size:0.75rem;font-family:'Space Mono',monospace;">
MOHAMED · STOCK MARKET ANALYSIS · PYTHON + SQL + STREAMLIT + PLOTLY
</p>
""", unsafe_allow_html=True)
