"""
HyprContext - Streamlit Web Dashboard
Aktivite takibi için web arayüzü.
"""

import json
import re
from datetime import datetime

import pandas as pd
import streamlit as st

from config import HISTORY_FILE

# === SAYFA AYARLARI ===
PAGE_TITLE = "HyprContext Dashboard"
PAGE_ICON = "🚀"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")


@st.cache_data(ttl=30)  # 30 saniye cache
def load_data() -> pd.DataFrame:
    """JSONL dosyasını okur ve DataFrame'e çevirir."""
    if not HISTORY_FILE.exists():
        return pd.DataFrame(columns=["timestamp", "summary", "tags"])

    data = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                summary = entry.get("summary", "")
                
                # Tag'leri ayıkla
                match = re.search(r'\[([^\]]+)\]$', summary.strip())
                tags = match.group(1) if match else "Genel"
                
                data.append({
                    "timestamp": pd.to_datetime(entry["timestamp"]),
                    "summary": summary,
                    "tags": tags
                })
            except json.JSONDecodeError:
                continue
    
    return pd.DataFrame(data)


def main():
    """Ana dashboard."""
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    st.markdown("Yapay zeka destekli kişisel hafıza ve aktivite dökümü.")

    # Veriyi yükle
    df = load_data()

    if df.empty:
        st.warning("Henüz veri bulunamadı. main.py çalışıyor mu?")
        st.stop()

    # === KENAR ÇUBUĞU (FİLTRELER) ===
    st.sidebar.header("🔍 Filtreler")

    # Arama kutusu
    search_query = st.sidebar.text_input("İçerik Ara", placeholder="Örn: Python, YouTube...")

    # Etiket filtresi
    all_tags = []
    for tag_str in df["tags"]:
        all_tags.extend([t.strip() for t in tag_str.split(",")])
    
    unique_tags = sorted(set(all_tags))
    selected_tags = st.sidebar.multiselect("Etiket Seç", unique_tags)

    # Filtreleme
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df["summary"].str.contains(search_query, case=False, na=False)
        ]

    if selected_tags:
        mask = filtered_df["tags"].apply(
            lambda x: any(tag in x for tag in selected_tags)
        )
        filtered_df = filtered_df[mask]

    # === İSTATİSTİKLER ===
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Toplam Kayıt", len(filtered_df))
    
    with col2:
        if not filtered_df.empty:
            last_active = filtered_df.iloc[0]["timestamp"].strftime("%H:%M")
            st.metric("Son Aktivite", last_active)
    
    with col3:
        st.metric("Farklı Konu", len(unique_tags))

    st.divider()

    # === GRAFİKLER ===
    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        st.subheader("📊 Saatlik Aktivite Yoğunluğu")
        if not filtered_df.empty:
            hourly_counts = filtered_df.groupby(
                filtered_df["timestamp"].dt.hour
            ).size()
            st.bar_chart(hourly_counts, color="#00FFAA")

    with col_chart2:
        st.subheader("🏷️ En Çok Geçen Konular")
        if all_tags:
            tag_series = pd.Series(all_tags)
            top_tags = tag_series.value_counts().head(7)
            st.dataframe(top_tags, use_container_width=True)

    st.divider()

    # === ZAMAN ÇİZELGESİ ===
    st.subheader("⏱️ Zaman Çizelgesi")

    if filtered_df.empty:
        st.info("Filtrelere uygun kayıt bulunamadı.")
    else:
        for _, row in filtered_df.iterrows():
            ts = row["timestamp"]
            summary = row["summary"]
            tags = row["tags"]
            
            time_display = ts.strftime("%H:%M:%S")
            date_display = ts.strftime("%d %B %Y")
            
            with st.expander(f"⏰ {time_display} | {tags}"):
                st.markdown(f"**Tarih:** {date_display}")
                st.info(summary)

    # Yenile butonu
    if st.button("🔄 Verileri Yenile"):
        st.cache_data.clear()
        st.rerun()


if __name__ == "__main__":
    main()
