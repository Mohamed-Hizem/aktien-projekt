# 📈 Stock Market Analysis Dashboard

An interactive stock market dashboard built with Python, SQL, Streamlit, and Plotly — covering **AAPL, MSFT, TSLA, and SAP.DE** from 2020 to 2024.

---

## 🚀 Live Demo

👉 [Click here to open the dashboard](#) *(replace with your Streamlit Cloud link)*

---

## 📊 Features

- **Interactive price charts** — Line, Area, and Bar chart modes
- **KPI cards** — Total return, current price, and all-time high per stock
- **Date range filter** — Zoom into any time period from 2020 to 2024
- **Stock selector** — Compare any combination of the 4 tickers
- **Raw data table** — Toggle to inspect the underlying data
- **Dark theme** — Clean professional dark UI

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| SQLite | Data storage |
| Pandas | Data manipulation |
| Plotly | Interactive charts |
| Streamlit | Web dashboard framework |
| Power BI | Additional BI dashboard |
| yfinance | Historical stock data download |

---

## 📁 Project Structure

```
aktien_projekt/
├── app.py                      # Streamlit dashboard
├── analyse-checkpoint.ipynb    # Data pipeline & analysis notebook
├── aktien_dashboard.xlsx       # Excel export with summary & charts
├── Aktienkurs_Projekt.pdf      # Power BI dashboard (PDF export)
├── requirements.txt            # Python dependencies
└── db/
    └── aktien.db               # SQLite database (OHLCV + metrics)
```

---

## ⚙️ Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/aktien-projekt.git
cd aktien-projekt

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Then open your browser at `http://localhost:8501`

---

## 📓 Data Pipeline

The Jupyter notebook `analyse-checkpoint.ipynb` covers the full pipeline:

1. **Download** — Historical OHLCV data via `yfinance`
2. **Transform** — Wide to long format, data cleaning
3. **Store** — SQLite database with `kurse` and `kennzahlen` tables
4. **Analyse** — Moving averages (MA7, MA30, MA90), daily returns, volatility
5. **Export** — Excel dashboard + Power BI report

---

## 👤 Author

**Mohamed** — Data Science Portfolio Project
