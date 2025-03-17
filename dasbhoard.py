import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style="dark")

## gathering
day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")

## cleansing
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

## membuat komponen filter
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://plus.unsplash.com/premium_photo-1682125270920-39b89bb20867?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjV8fGJpY3ljbGUlMjBsb2dvfGVufDB8fDB8fHww")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu", min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

## menyimpan data ke main_df
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                  (day_df["dteday"] <= str(end_date))]
main_df_tren = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                        (hour_df["dteday"] <= str(end_date))]

## data result_season
result_season = main_df.groupby(by="season").agg({"cnt": "sum"})
total_count = result_season["cnt"].sum()
result_season["Percentage"] = (result_season["cnt"] / total_count * 100).round(2).astype(str) + "%"
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
result_season["season_name"] = result_season.index.map(season_mapping)
result_season = result_season[["season_name", "cnt", "Percentage"]]

## data result_weathersit
result_weathersit = main_df.groupby(by="weathersit").agg({"cnt": "sum"})
total_count = result_weathersit["cnt"].sum()
result_weathersit["Percentage"] = (result_weathersit["cnt"] / total_count * 100).round(2).astype(str) + "%"
weathersit_mapping = {1: "Clear", 2: "Mist", 3: "Light snow/rain", 4: "Heavy rain"}
result_weathersit["weathersit_name"] = result_weathersit.index.map(weathersit_mapping)
result_weathersit = result_weathersit[["weathersit_name", "cnt", "Percentage"]]

## data tren_customer
tren_customer = main_df_tren.groupby(pd.Grouper(key="dteday", freq="M")).agg({
    "casual": "sum",
    "registered": "sum"
})
tren_customer.index = tren_customer.index.strftime("%Y-%m")


## data binning pengelompokan jam
bins = [0, 6, 9, 17, 19, 24]  
labels = ["Jam Sepi", "Jam Sibuk", "Jam Sepi", "Jam Sibuk", "Jam Sepi"]  
hour_df["Time_Category"] = pd.cut(hour_df["hr"], bins=bins, labels=labels, right=False, ordered=False)
result = hour_df.groupby("Time_Category")["cnt"].sum().reset_index()


### BAGIAN DASHBOARD
st.header("Analisis Penyewaan Sepeda :bike::bike::dollar: :dollar:\n(Data periode 2011-2012) ")

## part 1
st.subheader("1. Season and Weathersit")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 5)) 

    colors = ["lightgreen", "gold", "orange", "lightblue"]
    sns.barplot(
        y="cnt", 
        x="season_name",
        data=result_season.sort_values(by="season", ascending=True),
        palette=colors,
        ax=ax  
    )

    plt.title("Jumlah Pelanggan berdasarkan Musim", loc="center", fontsize=15)
    plt.ylabel("Jumlah Pelanggan")
    plt.xlabel("Musim")
    plt.tick_params(axis="x", labelsize=12)

    st.pyplot(fig)  

with col2:
    fig, ax = plt.subplots(figsize=(10, 5))  

    colors = ["#66CDAA", "#B0C4DE", "#ADD8E6", "#4682B4"]
    sns.barplot(
        y="cnt", 
        x="weathersit_name",
        data=result_weathersit.sort_values(by="weathersit", ascending=True),
        palette=colors,
        ax=ax  
    )

    plt.title("Jumlah Pelanggan berdasarkan Kondisi Cuaca", loc="center", fontsize=15)
    plt.ylabel("Jumlah Pelanggan")
    plt.xlabel("Kondisi Cuaca")
    plt.tick_params(axis="x", labelsize=12)

    st.pyplot(fig)  
 
## part 2
st.subheader("2. Customer Trend")

col1, col2, col3 = st.columns(3)

with col1:
    total_customer = tren_customer["casual"].sum() + tren_customer["registered"].sum()
    st.metric("Total Customer", value=f"{total_customer:,}")

with col2:
    total_casual = tren_customer["casual"].sum()
    st.metric("Casual Customer", value=f"{total_casual:,}")

with col3:
    total_registered = tren_customer["registered"].sum()
    st.metric("Registered Customer", value=f"{total_registered:,}")

fig, ax = plt.subplots(figsize=(12, 6))
plt.plot(tren_customer.index, tren_customer["casual"], label="Casual", marker="o")
plt.plot(tren_customer.index, tren_customer["registered"], label="Registered", marker="o")

plt.title("Jumlah Registered dan Casual Customer")
plt.xlabel("Tahun-Bulan")
plt.ylabel("Jumlah")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

st.pyplot(fig)  

## part 3
st.subheader("3. Binning berdasarkan Jam Kerja")

col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots()
    ax1.bar(result["Time_Category"], result["cnt"], color=["#A3C1DA", "#F9E79F"])
    ax1.set_xlabel("Kategori Waktu")
    ax1.set_ylabel("Jumlah Penyewaan")
    ax1.set_title("Jumlah Penyewaan Sepeda: Jam Sibuk vs Jam Sepi")
    st.pyplot(fig1) 

with col2:
    fig2, ax2 = plt.subplots()
    ax2.pie(result["cnt"], labels=result["Time_Category"], autopct="%1.1f%%", colors=["#A3C1DA", "#F9E79F"])
    ax2.set_title("Proporsi Penyewaan Sepeda: Jam Sibuk vs Jam Sepi")
    st.pyplot(fig2)  