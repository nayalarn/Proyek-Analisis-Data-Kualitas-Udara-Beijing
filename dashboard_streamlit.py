"""Dashboard Kualitas Udara Beijing (PM2.5), Mar 2013 - Feb 2017.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# ------------------------------------------------------------------ konfigurasi
st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", page_icon="🌫️", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AMBANG = 75  # baku mutu PM2.5 harian China (GB 3095-2012, Grade II), µg/m3
BIRU, MERAH, ABU = "#1F4E79", "#D1495B", "#B8C0CC"
KATEGORI = ["Sangat Baik", "Baik", "Tercemar Ringan", "Tercemar Sedang", "Tercemar Berat", "Tercemar Parah"]
WARNA_KAT = ["#2A9D8F", "#8AB17D", "#E9C46A", "#F4A261", "#E76F51", "#8B1E3F"]
NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
sns.set_theme(style="whitegrid")


# ------------------------------------------------------------------ data
@st.cache_data
def load_daily():
    file_path = os.path.join(BASE_DIR, "main_data.csv")
    if not os.path.exists(file_path):
        st.error(f"File tidak ditemukan: {file_path}. Pastikan file 'main_data.csv' berada di dalam folder yang sama dengan dashboard.py")
        st.stop()
        
    df = pd.read_csv(file_path, parse_dates=["date"])
    df["lewat_ambang"] = df["PM2.5"] > AMBANG
    df["month"] = df["date"].dt.month
    
    if "musim" not in df.columns:
        kondisi = [
            df['month'].isin([12, 1, 2]),
            df['month'].isin([3, 4, 5]),
            df['month'].isin([6, 7, 8]),
            df['month'].isin([9, 10, 11])
        ]
        pilihan = ["Dingin (Des-Feb)", "Semi (Mar-Mei)", "Panas (Jun-Agu)", "Gugur (Sep-Nov)"]
        df["musim"] = np.select(kondisi, pilihan, default="Semi (Mar-Mei)")

    if "kategori_udara" not in df.columns:
        bins = [-1, 35, 75, 115, 150, 250, 9999]
        df["kategori_udara"] = pd.cut(df["PM2.5"], bins=bins, labels=KATEGORI)
        
    if "periode" not in df.columns:
        df["periode"] = df["date"].apply(lambda x: f"{x.year}-{x.year+1}" if x.month >= 3 else f"{x.year-1}-{x.year}")
        
    return df


@st.cache_data
def load_hourly():
    file_path = os.path.join(BASE_DIR, "hourly_profile.csv")
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["hour", "month", "station", "PM2.5"])
    df = pd.read_csv(file_path)
    
    # Standardisasi nama kolom jam dan bulan 
    if "jam" in df.columns:
        df = df.rename(columns={"jam": "hour"})
    if "bulan" in df.columns:
        df = df.rename(columns={"bulan": "month"})
    return df


def persen_lewat(d):
    valid = d["PM2.5"].notna().sum()
    return (d["PM2.5"] > AMBANG).sum() / valid * 100 if valid else np.nan


def rapikan(ax, hapus_grid_x=True):
    sns.despine(ax=ax)
    if hapus_grid_x:
        ax.grid(axis="x", visible=False)


daily = load_daily()
hourly = load_hourly()

# ------------------------------------------------------------------ sidebar
st.sidebar.title("Filter Data")

semua_stasiun = sorted(daily["station"].unique())

with st.sidebar.expander("Stasiun Pemantauan", expanded=True):
    stasiun = st.multiselect(
        "Stasiun:", 
        semua_stasiun, 
        default=semua_stasiun,
        label_visibility="collapsed" 
    )

with st.sidebar.expander("Waktu & Musim", expanded=True):
    # Filter Tanggal
    tgl_min, tgl_max = daily["date"].min().date(), daily["date"].max().date()
    rentang = st.date_input(
        "Rentang Tanggal:", 
        value=(tgl_min, tgl_max), 
        min_value=tgl_min, 
        max_value=tgl_max
    )
    if isinstance(rentang, (tuple, list)):
        tgl_awal, tgl_akhir = rentang if len(rentang) == 2 else (rentang[0], tgl_max)
    else:
        tgl_awal, tgl_akhir = rentang, tgl_max

    st.markdown("---")

    # Filter Musim
    urutan_musim = ["Dingin (Des-Feb)", "Semi (Mar-Mei)", "Panas (Jun-Agu)", "Gugur (Sep-Nov)"]
    musim_pilih = st.multiselect("Pilih Musim:", urutan_musim, default=urutan_musim)

st.sidebar.markdown("---")
st.sidebar.info(
    f"💡 **Info Data:** Ambang harian PM2.5 = **{AMBANG} µg/m³** (GB 3095-2012 Grade II)."
)
st.sidebar.caption("Sumber: Beijing Multi-Site Air Quality Data (12 stasiun, harian).")

df = daily[
    daily["station"].isin(stasiun)
    & (daily["date"] >= pd.Timestamp(tgl_awal))
    & (daily["date"] <= pd.Timestamp(tgl_akhir))
    & daily["musim"].isin(musim_pilih)
]


# ------------------------------------------------------------------ header
st.markdown(
    "<h1 style='text-align: center; font-size: 55px; font-weight: bold; margin-bottom: 20px;'>"
    "Dashboard Kualitas Udara Beijing: PM2.5 2013-2017"
    "</h1>", 
    unsafe_allow_html=True
)

if df.empty or df["PM2.5"].notna().sum() == 0:
    st.warning("Tidak ada data untuk kombinasi filter ini. Ubah pilihan stasiun, tanggal, atau musim.")
    st.stop()

# ------------------------------------------------------------------ KPI
#  MENGHITUNG NILAI DATA
rata = df["PM2.5"].mean()
persen_ambang = (rata / AMBANG - 1) * 100
status_ambang = f"{persen_ambang:+.0f}% vs ambang 75"
hari_lewat = f"{persen_lewat(df):.1f}%"
hari_tercemar = f"{(df['PM2.5'] > 150).sum() / df['PM2.5'].notna().sum() * 100:.1f}%"
maks_harian = f"{df['PM2.5'].max():.0f} µg/m³"

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #1F4E79;">
            <p style="font-size: 32px; font-weight: bold; margin-bottom: 5px; color: #333333; line-height: 1.2;">Rata-rata PM2.5</p>
            <p style="font-size: 36px; margin-bottom: 2px; color: #1F4E79;">{rata:.1f} µg/m³</p>
            <p style="font-size: 16px; margin-bottom: 0px; color: #D1495B; font-weight: 500;">{status_ambang}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #1F4E79;">
            <p style="font-size: 32px; font-weight: bold; margin-bottom: 5px; color: #333333; line-height: 1.2;">Hari melewati ambang</p>
            <p style="font-size: 36px; margin-bottom: 2px; color: #1F4E79;">{hari_lewat}</p>
            <p style="font-size: 16px; margin-bottom: 0px; color: #777777;">&nbsp;</p> 
        </div>
        """,
        unsafe_allow_html=True
    )

with k3:
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #1F4E79;">
            <p style="font-size: 32px; font-weight: bold; margin-bottom: 5px; color: #333333; line-height: 1.2;">Hari tercemar berat/parah</p>
            <p style="font-size: 36px; margin-bottom: 2px; color: #1F4E79;">{hari_tercemar}</p>
            <p style="font-size: 16px; margin-bottom: 0px; color: #777777;">&nbsp;</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with k4:
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #1F4E79;">
            <p style="font-size: 32px; font-weight: bold; margin-bottom: 5px; color: #333333; line-height: 1.2;">Maksimum harian</p>
            <p style="font-size: 36px; margin-bottom: 2px; color: #1F4E79;">{maks_harian}</p>
            <p style="font-size: 16px; margin-bottom: 0px; color: #777777;">&nbsp;</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- MODIFIKASI TAMPILAN TAB MODERN & ESTETIK ---
st.markdown(
    """
    <style>
    div[data-testid="stTabs"] {
        gap: 10px !important;
        margin-top: 20px !important;
        margin-bottom: 25px !important;
    }

    button[data-baseweb="tab"] {
        background-color: #f1f3f5 !important;
        border: 1px solid #e9ecef !important;
        border-radius: 30px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important; 
    }

    button[data-baseweb="tab"] p {
        font-size: 20px !important; 
        font-weight: 600 !important;
        color: #495057 !important;
    }

    button[data-baseweb="tab"]:hover {
        background-color: #e2e6ea !important;
        border-color: #ced4da !important;
        transform: translateY(-2px) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #1F4E79 !important; 
        border-color: #1F4E79 !important;
        box-shadow: 0 4px 12px rgba(31, 78, 121, 0.24) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #ffffff !important;
    }

    div[data-baseweb="tab-list"] {
        border-bottom: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Stasiun", "Tren & Musim", "Angin & Cuaca", "Pola Jam", "Kesimpulan"]
)


# ------------------------------------------------------------------ Q1
with tab1:
    st.subheader("Pertanyaan 1: Stasiun mana yang paling tercemar?")
    tb = (
        df.groupby("station")
        .apply(lambda d: pd.Series({"Rata-rata PM2.5": d["PM2.5"].mean(), "% hari > 75": persen_lewat(d)}), include_groups=False)
        .sort_values("% hari > 75")
    )
    
    fig, axes = plt.subplots(1, 2, figsize=(12, max(3.5, 0.5 * len(tb) + 1.5)), sharey=True)
    warna = [MERAH if v > 40 else BIRU for v in tb["% hari > 75"]]
    
    axes[0].barh(tb.index, tb["Rata-rata PM2.5"], color=warna)
    axes[0].axvline(AMBANG, color="black", ls="--", lw=1)
    axes[0].set_title("Rata-rata PM2.5 (µg/m³)", loc="left")
    
    axes[1].barh(tb.index, tb["% hari > 75"], color=warna)
    axes[1].set_title("% hari melewati ambang 75 µg/m³", loc="left")
    
    for y, v in enumerate(tb["Rata-rata PM2.5"]):
        axes[0].text(v * 0.98, y, f"{v:.1f}", va="center", ha="right", color="white", fontsize=9, fontweight="bold")
    for y, v in enumerate(tb["% hari > 75"]):
        axes[1].text(v * 0.98, y, f"{v:.1f}%", va="center", ha="right", color="white", fontsize=9, fontweight="bold")
        
    rapikan(axes[0])
    rapikan(axes[1])
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Merah = lebih dari 40% hari melewati ambang, biru = 40% atau kurang. Garis putus-putus = ambang 75 µg/m³.")

    st.markdown("**Komposisi kategori kualitas udara harian per stasiun**")
    komp = pd.crosstab(df["station"], df["kategori_udara"], normalize="index") * 100
    komp = komp.reindex(columns=KATEGORI, fill_value=0).loc[tb.index]
    fig, ax = plt.subplots(figsize=(11, max(3.5, 0.45 * len(komp) + 1.5)))
    komp.plot(kind="barh", stacked=True, color=WARNA_KAT, width=0.8, ax=ax)
    ax.set_xlabel("Persentase hari (%)")
    ax.set_ylabel("")
    ax.legend(title="Kategori", bbox_to_anchor=(1.01, 1), loc="upper left", frameon=False)
    rapikan(ax)
    ax.grid(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    with st.expander("Lihat tabel data"):
        st.dataframe(tb.sort_values("% hari > 75", ascending=False).round(2))

# ------------------------------------------------------------------ Q2
# ------------------------------------------------------------------ Q2
with tab2:
    st.subheader("Pertanyaan 2: Bagaimana tren dan pola musiman PM2.5?")
    bulanan = df.assign(bln=df["date"].dt.to_period("M").dt.to_timestamp()).groupby("bln")["PM2.5"].mean()
    klim = df.groupby("month")["PM2.5"].mean().reindex(range(1, 13))

    c1, c2 = st.columns([1.7, 1])
    with c1:
        fig, ax = plt.subplots(figsize=(8, 4.2))
        ax.plot(bulanan.index, bulanan.values, color=BIRU, lw=2)
        ax.fill_between(bulanan.index, bulanan.values, color=BIRU, alpha=0.12)
        ax.axhline(AMBANG, color=MERAH, ls="--", lw=1.2)
        ax.text(bulanan.index[-1], AMBANG - 8, "Ambang 75", color=MERAH, ha="right", fontsize=9)
        pk = bulanan.idxmax()
        ax.scatter([pk], [bulanan.max()], color=MERAH, zorder=5)
        ax.annotate(f"Puncak {pk:%b %Y}: {bulanan.max():.0f}", (pk, bulanan.max()), xytext=(8, -4),
                    textcoords="offset points", fontsize=9, color=MERAH)
        ax.set_title("Rata-rata PM2.5 bulanan", loc="left")
        ax.set_ylabel("PM2.5 (µg/m³)")
        rapikan(ax)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        
    with c2:
        fig, ax = plt.subplots(figsize=(5, 4.2))
        warna = [MERAH if (v == v and v > AMBANG) else ABU for v in klim.values]
        ax.bar(NAMA_BULAN, klim.fillna(0).values, color=warna)
        ax.axhline(AMBANG, color="black", ls="--", lw=1)
        for i, v in enumerate(klim.values):
            if v == v:
                ax.text(i, v + 1.5, f"{v:.0f}", ha="center", fontsize=8)
        ax.set_title("Per bulan kalender (merah > 75)", loc="left")
        ax.tick_params(axis="x", labelsize=8)
        rapikan(ax)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("**Perbandingan antarperiode 12 bulan (Mar-Feb) dan antarmusim**")
    d1, d2 = st.columns(2)
    
    with d1:
        per = df.groupby("periode").apply(
            lambda d: pd.Series({"Rata-rata PM2.5": d["PM2.5"].mean(), "% hari > 75": persen_lewat(d)}), include_groups=False
        )
        if len(per) > 1:
            per["Perubahan vs sebelumnya (%)"] = per["Rata-rata PM2.5"].pct_change() * 100
        else:
            per["Perubahan vs sebelumnya (%)"] = 0.0
            
        st.markdown("### Ringkasan per Periode")
        st.dataframe(per.round(2))
        
    with d2:
        musim_stats = df.groupby("musim").apply(
            lambda d: pd.Series({"Rata-rata PM2.5": d["PM2.5"].mean(), "% hari > 75": persen_lewat(d)}), include_groups=False
        ).reindex(urutan_musim).dropna()
        
        st.markdown("### Ringkasan per Musim")
        st.dataframe(musim_stats.round(2))

# ------------------------------------------------------------------ Q3
with tab3:
    st.subheader("Pertanyaan 3: Seberapa besar pengaruh angin dan cuaca terhadap PM2.5?")
    faktor = {"WSPM": "Kecepatan angin", "TEMP": "Suhu", "PRES": "Tekanan", "DEWP": "Titik embun", "RAIN": "Curah hujan"}
    kor = df[["PM2.5"] + list(faktor)].corr(method="spearman")["PM2.5"].drop("PM2.5").sort_values()

    c1, c2 = st.columns(2)
    with c1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh([faktor[i] for i in kor.index], kor.values, color=[BIRU if v < 0 else MERAH for v in kor.values])
        for y, v in enumerate(kor.values):
            ax.text(v + (0.015 if v >= 0 else -0.015), y, f"{v:+.2f}", va="center",
                    ha="left" if v >= 0 else "right", fontsize=10)
        ax.axvline(0, color="black", lw=0.8)
        ax.set_xlim(-0.65, 0.65)
        ax.set_title("Korelasi Spearman dengan PM2.5", loc="left")
        ax.set_xlabel("Biru = menurunkan, merah = menaikkan PM2.5")
        rapikan(ax)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with c2:
        kelas = pd.cut(df["WSPM"], bins=[0, 1, 2, 3, 4, np.inf], labels=["< 1", "1-2", "2-3", "3-4", "> 4"], right=False)
        ang = (
            df.assign(kelas=kelas).dropna(subset=["PM2.5", "kelas"])
            .groupby("kelas", observed=True)
            .apply(lambda d: pd.Series({"rata": d["PM2.5"].mean(), "persen": persen_lewat(d)}))
        )
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(ang.index.astype(str), ang["rata"], color=[MERAH if v > AMBANG else BIRU for v in ang["rata"]])
        ax.axhline(AMBANG, color="black", ls="--", lw=1)
        for i, (v, p) in enumerate(zip(ang["rata"], ang["persen"])):
            ax.text(i, v + 2, f"{v:.0f}\n({p:.0f}% hari)", ha="center", fontsize=8.5)
        ax.set_ylim(0, max(ang["rata"].max() * 1.3, AMBANG * 1.3))
        ax.set_xlabel("Kecepatan angin harian (m/s)")
        ax.set_ylabel("PM2.5 (µg/m³)")
        ax.set_title("PM2.5 menurut kecepatan angin", loc="left")
        rapikan(ax)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("**PM2.5 menurut arah angin dominan**")
    arah = df.groupby("wd")["PM2.5"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.bar(arah.index, arah.values, color=[MERAH if v > AMBANG else ABU for v in arah.values])
    ax.axhline(AMBANG, color="black", ls="--", lw=1)
    ax.set_ylabel("PM2.5 (µg/m³)")
    rapikan(ax)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Angin lemah (< 2 m/s) adalah pemicu utama hari tercemar, sehingga dipakai sebagai indikator peringatan dini.")

# ------------------------------------------------------------------ Pola jam
with tab4:
    st.subheader("Kapan PM2.5 paling tinggi? Pola jam x bulan")
    hp = hourly[hourly["station"].isin(stasiun)].copy()
    
    if hp.empty:
        st.warning("Pilih minimal satu stasiun dan pastikan file 'hourly_profile.csv' tersedia.")
    else:
        kolom_jam = "hour" if "hour" in hp.columns else "jam"
        kolom_bulan = "month" if "month" in hp.columns else "bulan"
        
        if kolom_jam in hp.columns and kolom_bulan in hp.columns:
            heat = hp.pivot_table(index=kolom_jam, columns=kolom_bulan, values="PM2.5", aggfunc="mean")
            
            heat.columns = [NAMA_BULAN[int(c) - 1] for c in heat.columns if 1 <= int(c) <= 12]
        
            fig, ax = plt.subplots(figsize=(11, 5.5))
            sns.heatmap(heat, cmap="YlOrRd", cbar_kws={"label": "PM2.5 (µg/m³)"}, ax=ax)
            ax.set_xlabel("Bulan")
            ax.set_ylabel("Jam (0-23)")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning(f"Kolom waktu tidak ditemukan. Kolom yang tersedia di file Anda adalah: {list(hp.columns)}")


# ------------------------------------------------------------------ Kesimpulan
with tab5:
    st.subheader("Kesimpulan & Rekomendasi (seluruh data, Mar 2013 - Feb 2017)")
    st.markdown(
        """
<div style="font-size: 19px; line-height: 1.6; color: #31333F;">
    <h3 style="margin-top: 20px; font-size: 24px; color: #FF4B4B;"> Kesimpulan</h3>
    <ol>
        <li style="margin-bottom: 10px;">Rata-rata PM2.5 dari seluruh stasiun adalah 79,9 µg/m³, sedikit lebih tinggi dari ambang harian 75 µg/m³. Stasiun Dongsi memiliki rata-rata tertinggi, yaitu 86,1 µg/m³. Namun, sembilan stasiun perkotaan memiliki hasil yang hampir sama, dengan sekitar 41–43% hari melewati ambang. Sementara itu, Dingling, Huairou, dan Changping memiliki persentase lebih rendah, yaitu sekitar 32–36%. Dari hasil ini, terlihat bahwa masalah PM2.5 tidak hanya terjadi di satu stasiun, tetapi juga ditemukan di banyak wilayah.</li>
        <li style="margin-bottom: 10px;">Rata-rata PM2.5 pada musim dingin mencapai 95,9 µg/m³, lebih tinggi 48% dibandingkan musim panas yang sebesar 64,6 µg/m³. Pada bulan Oktober sampai Maret, rata-rata PM2.5 juga selalu berada di atas ambang harian. Jika dilihat berdasarkan periode tahunan, rata-ratanya sempat turun dari 87,2 menjadi 72,9 µg/m³, tetapi kemudian naik lagi menjadi 78,1 µg/m³ pada periode terakhir. Artinya, penurunan PM2.5 belum terjadi secara konsisten.</li>
        <li style="margin-bottom: 10px;">Dari variabel cuaca yang dianalisis, kecepatan angin memiliki hubungan paling kuat dengan PM2.5, dengan nilai korelasi Spearman -0,45. Saat kecepatan angin kurang dari 1 m/s, ada 65,6% hari yang PM2.5-nya melewati ambang. Sebaliknya, saat kecepatan angin lebih dari 4 m/s, persentasenya hanya 3,9%. Hasil ini menunjukkan bahwa PM2.5 cenderung lebih tinggi ketika kecepatan angin rendah.</li>
    </ol>
    <br>
    <h3 style="margin-top: 10px; font-size: 24px; color: #00C04A;"> Rekomendasi</h3>
    <ul>
        <li style="margin-bottom: 10px;">Pengendalian polusi perlu lebih diperhatikan pada bulan Oktober sampai Maret karena PM2.5 pada periode ini cenderung lebih tinggi.</li>
        <li style="margin-bottom: 10px;">Kecepatan angin dapat menjadi salah satu hal yang diperhatikan dalam peringatan dini, terutama saat musim dingin. Jika angin diperkirakan lemah, masyarakat dapat diimbau untuk mengurangi aktivitas di luar ruangan ketika kualitas udara sedang buruk.</li>
        <li style="margin-bottom: 10px;">Karena hasil pengukuran di banyak stasiun perkotaan hampir sama, penanganan polusi sebaiknya tidak hanya berfokus pada satu stasiun.</li>
        <li style="margin-bottom: 10px;">Data kualitas udara perlu terus dibandingkan dari satu periode ke periode berikutnya untuk melihat apakah kondisinya membaik atau justru meningkat kembali.</li>
    </ul>
</div>
        """,
        unsafe_allow_html=True
    )


