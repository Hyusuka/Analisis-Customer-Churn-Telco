import pandas as pd
import matplotlib.pyplot as plt
import os
import streamlit as st

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Analisis Customer Churn Telco", layout="wide")
st.title("📊 Analisis Customer Churn Telco")

INPUT_FILE = "telco_churn.csv"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Load Data dengan Caching Streamlit
@st.cache_data
def load_data():
    df = pd.read_csv(INPUT_FILE)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
    df["ChurnFlag"] = df["Churn"].map({"Yes": 1, "No": 0})
    bins = [0, 6, 12, 24, 48, 72]
    labels = ["0-6 bln", "7-12 bln", "13-24 bln", "25-48 bln", "49-72 bln"]
    df["TenureGroup"] = pd.cut(df["tenure"], bins=bins, labels=labels, include_lowest=True)
    return df

df = load_data()

# 3. Metrik Utama (Metrics Summary)
overall_churn_rate = df["ChurnFlag"].mean() * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Pelanggan", f"{len(df):,}")
col2.metric("Churn Rate Keseluruhan", f"{overall_churn_rate:.1f}%")
col3.metric("Rata-rata Biaya Bulanan", f"${df['MonthlyCharges'].mean():.2f}")

st.divider()

# 4. Kalkulasi Data untuk Chart
churn_by_contract = df.groupby("Contract")["ChurnFlag"].mean().sort_values(ascending=False) * 100
churn_by_tenure = df.groupby("TenureGroup", observed=True)["ChurnFlag"].mean() * 100
churn_by_payment = df.groupby("PaymentMethod")["ChurnFlag"].mean().sort_values(ascending=False) * 100

plt.style.use("seaborn-v0_8-whitegrid")

# 5. Layout Visualisasi (Grid 2x2)
c1, c2 = st.columns(2)

with c1:
    fig, ax = plt.subplots(figsize=(6, 4))
    churn_by_contract.plot(kind="bar", color="#c0392b", ax=ax)
    ax.set_title("Churn Rate per Tipe Kontrak")
    ax.set_ylabel("Churn Rate (%)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with c2:
    fig, ax = plt.subplots(figsize=(6, 4))
    churn_by_tenure.plot(kind="bar", color="#2980b9", ax=ax)
    ax.set_title("Churn Rate per Kelompok Tenure")
    ax.set_ylabel("Churn Rate (%)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

c3, c4 = st.columns(2)

with c3:
    fig, ax = plt.subplots(figsize=(6, 4))
    churn_by_payment.plot(kind="bar", color="#8e44ad", ax=ax)
    ax.set_title("Churn Rate per Metode Pembayaran")
    ax.set_ylabel("Churn Rate (%)")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with c4:
    fig, ax = plt.subplots(figsize=(6, 4))
    df[df["Churn"] == "Yes"]["MonthlyCharges"].plot(kind="density", ax=ax, label="Churn", color="#c0392b")
    df[df["Churn"] == "No"]["MonthlyCharges"].plot(kind="density", ax=ax, label="Tidak Churn", color="#27ae60")
    ax.set_title("Distribusi Biaya Bulanan: Churn vs Tidak")
    ax.set_xlabel("Monthly Charges")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.divider()

# 6. Draft Memo / Executive Summary
top_contract = churn_by_contract.index[0]
top_contract_rate = churn_by_contract.iloc[0]
lowest_tenure_rate = churn_by_tenure.iloc[0]
top_payment = churn_by_payment.index[0]
top_payment_rate = churn_by_payment.iloc[0]

st.subheader("📝 Draft Memo Insight")
st.info(f"""
**Churn rate keseluruhan pelanggan adalah {overall_churn_rate:.1f}%.**

**Temuan utama:**
1. Kontrak **"{top_contract}"** punya churn rate tertinggi (**{top_contract_rate:.1f}%**).
2. Pelanggan di kelompok tenure **"0-6 bln"** churn paling tinggi (**{lowest_tenure_rate:.1f}%**).
3. Metode pembayaran **"{top_payment}"** berasosiasi dengan churn rate tertinggi (**{top_payment_rate:.1f}%**).

**Rekomendasi:**
- Fokuskan program retensi pada pelanggan baru (<6 bulan) dengan kontrak bulanan.
- Pertimbangkan insentif migrasi ke kontrak tahunan pada 3 bulan pertama.
- Evaluasi pengalaman pembayaran untuk metode "{top_payment}".
""")
