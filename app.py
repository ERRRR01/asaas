import pandas as pd
import plotly.express as px
import streamlit as st

# Memuat data dari kedua file dan menggabungkannya
@st.cache_data
def load_data():
    # Membaca kedua file CSV
    df_part1 = pd.read_csv("Product_stok_kota_part1.csv")
    df_part2 = pd.read_csv("Product_stok_kota_part2.csv")
    
    # Menggabungkan data
    df_combined = pd.concat([df_part1, df_part2], ignore_index=True)
    return df_combined

# Load data
product_favorit_akhir = load_data()
Product_stok_kota_final = product_favorit_akhir

# Streamlit UI
st.title("E-Commerce Dataset Analysis")

# **Visualisasi 1: Produk dengan Pembelian Tertinggi dan Rating Terbaik**
st.header("1. Produk dengan Pembelian Terbanyak dan Rating Terbaik")

# Memeriksa apakah kolom yang diperlukan ada
required_columns = ["product_category_name", "review_score", "order_item_id"]
if not all(col in product_favorit_akhir.columns for col in required_columns):
    raise ValueError(f"Data harus memiliki kolom: {required_columns}")

# Mengelompokkan data berdasarkan kategori produk dan menghitung pembelian unik berdasarkan order_item_id
grouped_data = product_favorit_akhir.groupby("product_category_name").agg(
    purchase_count=("order_item_id", "sum"),  # Menghitung jumlah pembelian
    average_rating=("review_score", "mean")  # Menghitung rata-rata rating
).reset_index()

# Menyaring produk dengan pembelian terbanyak dan rating tertinggi
top_purchased_products = grouped_data.sort_values(by="purchase_count", ascending=False)
top_rated_products = grouped_data.sort_values(by="average_rating", ascending=False)

# Menampilkan produk yang ada di kedua kategori: pembelian terbanyak dan rating tertinggi
top_combined_products = pd.merge(top_purchased_products[['product_category_name', 'purchase_count']],
                                  top_rated_products[['product_category_name', 'average_rating']],
                                  on="product_category_name")

# Menyaring produk dengan purchase_count > 5000 dan average_rating > 4
filtered_products = top_combined_products[(top_combined_products['purchase_count'] > 5000) & 
                                           (top_combined_products['average_rating'] > 4)]

# Menampilkan 5 produk dengan purchase_count tertinggi yang memenuhi kriteria
top_5_purchased_products = filtered_products.head(5)

# Membuat visualisasi interaktif menggunakan Plotly
fig1 = px.bar(top_5_purchased_products,
             x='purchase_count',
             y='product_category_name',
             text='purchase_count',  # Menambahkan nilai pada bar
             hover_data={'purchase_count': True, 'average_rating': True},  # Menambahkan data saat hover
             labels={'purchase_count': 'Purchase Count', 'product_category_name': 'Product Category'},
             title="Top 5 Products with Highest Purchase Count and Rating Above 4")

# Menampilkan grafik pertama dengan interaktif
st.subheader("Top 5 Produk dengan Pembelian Terbanyak dan Rating di Atas 4")
st.plotly_chart(fig1, use_container_width=True)

# **Visualisasi 2: Produk Terbanyak di Setiap Kota**
st.header("2. Produk Terbanyak di Setiap Kota")

# Memeriksa apakah kolom yang diperlukan ada
required_columns = ["customer_city", "order_item_id", "product_category_name"]
if not all(col in Product_stok_kota_final.columns for col in required_columns):
    raise ValueError(f"Data harus memiliki kolom: {required_columns}")

# Mengelompokkan data berdasarkan kota dan menghitung jumlah total pembelian (order_item_id)
grouped_data_city = Product_stok_kota_final.groupby("customer_city").agg(
    total_purchases=("order_item_id", "count")  # Menghitung jumlah pembelian per kota
).reset_index()

# Mengurutkan data berdasarkan jumlah pembelian terbanyak
sorted_data_city = grouped_data_city.sort_values(by="total_purchases", ascending=False)

# Menampilkan 10 kota dengan jumlah pembelian terbanyak
top_10_cities = sorted_data_city.head(10)

# Menyaring data hanya untuk 10 kota teratas
top_10_cities_data = Product_stok_kota_final[Product_stok_kota_final['customer_city'].isin(top_10_cities['customer_city'])]

# Mengelompokkan data berdasarkan kota dan kategori produk, dan menghitung jumlah pembelian per kategori produk
grouped_products = top_10_cities_data.groupby(["customer_city", "product_category_name"]).agg(
    total_product_sales=("order_item_id", "count")  # Menghitung jumlah pembelian per kategori produk di setiap kota
).reset_index()

# Menyaring produk dengan pembelian terbanyak di setiap kota menggunakan nlargest
top_products_per_city = grouped_products.groupby("customer_city").apply(
    lambda x: x.nlargest(1, 'total_product_sales')
).reset_index(drop=True)

# Membuat diagram interaktif dengan Plotly
fig2 = px.bar(
    top_products_per_city,
    x='total_product_sales',
    y='customer_city',
    color='product_category_name',
    title='Top Products by City',
    labels={'total_product_sales': 'Total Product Sales', 'customer_city': 'Customer City', 'product_category_name': 'Product Category'},
    text='total_product_sales',  # Menambahkan nilai total pembelian sebagai teks di atas batang
    hover_data={'customer_city': True, 'product_category_name': True, 'total_product_sales': True}  # Menampilkan data saat hover
)

# Menampilkan plot interaktif
st.subheader("Top Products in the Top 10 Cities")
st.plotly_chart(fig2, use_container_width=True)

# Kesimpulan
st.header("Kesimpulan")
st.write("""
1. **Top 5 Produk dengan Pembelian Terbanyak dan Rating di Atas 4** menunjukkan produk-produk yang laris dengan rating yang sangat baik.
2. **Top Products by City** memberikan insight mengenai produk terlaris di masing-masing kota yang dapat membantu dalam pengelolaan stok dan permintaan.
""")
st.success("Analisis Selesai! Selamat Menggunakan Streamlit!")
