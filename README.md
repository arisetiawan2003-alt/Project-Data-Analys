# 📁international-business_sales-python
## Analisis mendalam terhadap 100.000 transaksi penjualan global mencakup 185 negara, 7 region, dan 12 kategori produk selama periode 2010–2017. tetapi 2017 hanya mencakup data Januari–Juli (setengah tahun)
# tools: Python,Pandas, Numpy, Matplotlib
## CHART 1 KPI YEARLY

![alt text](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/International-Business_Sales-Python/chart1_kpi_yearly.png?raw=true)
## 2014 adalah tahun dengan revenue tertinggi ($1.787T), sedangkan 2013 mencatat profit tertinggi ($525.88B).
## Pertumbuhan revenue relatif stagnan,variasi antar tahun hanya ±2%, mengindikasikan pasar yang sudah matang dan stabil.
## Profit margin konsisten di kisaran 34% sepanjang 7 tahun, mencerminkan struktur biaya yang terkontrol dengan baik.
## Tidak ada lonjakan atau penurunan drastis  bisnis ini bersifat resilient dan tidak musiman secara tahunan.

![alt text](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/International-Business_Sales-Python/chart2_tren_bulanan.png?raw=true)
## Q1 (Jan–Mar) dan Q2 (Apr–Jun) adalah periode paling aktif revenue dan volume order mencapai puncak di bulan Maret, Mei, dan Juli.
## Q3-Q4 (Agustus–Desember) mengalami penurunan volume secara konsisten, terutama September yang menjadi titik terendah.
## Strategi promosi dan stok sebaiknya difokuskan di semester pertama untuk memaksimalkan momentum pasar

![alt text](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/International-Business_Sales-Python/chart4_region.png?raw=true)
## Sub-Saharan Africa & Europe mendominasi bersama-sama menyumbang 51.73% dari total profit global.
## Asia berada di posisi ketiga dengan volume order yang signifikan (14.547 transaksi), namun kontribusi profit masih jauh di bawah dua region teratas
## Asia berada di posisi ketiga dengan volume order yang signifikan (14.547 transaksi), namun kontribusi profit masih jauh di bawah dua region teratas
## 🇺🇸 North America adalah region paling underperforming hanya 2.21% profit share dengan volume order terendah (2.133), padahal secara kapasitas pasar seharusnya jauh lebih besar. Ini mengindikasikan penetrasi pasar yang sangat rendah atau pembatasan distribusi di wilayah tersebut.
## Margin profit konsisten di 34% di semua region  tidak ada region yang secara struktural lebih efisien dari yang lain. Perbedaan hasil murni dari volume penjualan, bukan efisiensi operasional

![alt tetx](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/International-Business_Sales-Python/chart3_item_type.png?raw=true)
## Clothes memiliki profit margin tertinggi (67.20%)  hampir 2x lipat rata-rata keseluruhan (34.33%), namun revenue-nya relatif kecil (3.42% dari total). Ini peluang scaling yang belum dioptimalkan.
## Cosmetics adalah produk paling menguntungkan secara absolut ($728.94B profit) dengan margin sehat 39.77%
## Household & Office Supplies mendominasi revenue (masing-masing 20%), namun margin-nya di bawah rata-rata (24.8% dan 19.4%) volume driver tapi bukan profit driver
## Meat adalah kategori terlemah dari sisi margin (13.56%) — perlu evaluasi strategi pricing atau cost reduction.
## Fruits berkontribusi sangat kecil (0.28% revenue) dan margin di bawah rata-rata, kandidat untuk dipertimbangkan ulang dalam portofolio produk.
## ================================================
## 📁Project-ecommerce-sales
## Dataset ini adalah laporan penjualan Amazon India untuk kategori fashion & apparel (pakaian, aksesoris, parfum). Data mencakup periode April–Juni 2022 dengan total 110.489 transaksi dan revenue 71.6 juta INR.Bisnis ini menjual produk fashion secara online melalui platform Amazon.in, dengan dua model fulfillment: dikirim langsung oleh Amazon (FBA  Fulfillment by Amazon) atau oleh Merchant (seller) sendiri. Hampir semua transaksi adalah B2C (konsumen perorangan), dengan sebagian kecil B2B (pembelian bisnis).
## Tantangan utama bisnis ini adalah bisnis ini mengalami penurunan sebesar 18.45% dalam waktu 3 bulan. 
## Produk andalan adalah T-shirt dan Shirt yang menyumbang 77% dari total revenue.
## Berikut adalah business insight report sales Amazon
![alt text](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/Project-Ecommerce-Sales/Screenshot%202026-04-11%20150746.png?raw=true)
## [Amazon Business Insight Report.pdf](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/d757e56aa62e3eb05ebad1ae828265205e27b714/Project-Ecommerce-Sales/Amazon%20Business%20Insight%20Report%20.pdf) *Klik untuk selengkapnya*

## =============================================
## 📁Project Analysis sales SQL
## [File_Project_SQL](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/project-Analysis-Sales-SQL/belajar%20sql.sql) *Klik Link Untuk Melihat*
## Struktur Database SQL
![alt text](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/project-Analysis-Sales-SQL/erd_ecommerce.png?raw=true)
## ERD (Entity Relationship Diagram) tersebut menggambarkan struktur database untuk proyek e-commerce yang telah dinormalisasi menjadi 6 tabel.
## Inti Data: Tabel orders, Tabel ini adalah pusat dari diagram (fakta transaksi). Tabel ini mencatat detail pesanan seperti jumlah barang, total harga, rating, ulasan, dan tanggal pesanan. Tabel ini menghubungkan semua entitas lainnya melalui Foreign Keys (FK).
## Dimensi Produk (products, categories, brands) Bagian ini mengelola informasi barang yang dijual:products: Menyimpan nama produk dan harga. Bergantung pada kategori dan brand.categories: Mengelompokkan produk (misalnya: Elektronik, Pakaian). brands: Menyimpan informasi merek dari produk tersebut.
## Dimensi Pendukung (platforms, cities) platforms: Mencatat asal transaksi (misalnya: Shopee, Tokopedia, atau Website sendiri).cities: Mencatat lokasi atau kota tempat pesanan dilakukan/dikirim.
## Ringkasan Relasi,Semua relasi dalam diagram ini bersifat 1-to-N (One-to-Many), yang ditunjukkan oleh garis putus-putus. Artinya:Satu kategori bisa memiliki banyak produk.Satu brand bisa memiliki banyak produk.Satu produk, satu platform, dan satu kota bisa muncul di banyak baris pesanan (orders).Secara keseluruhan, struktur ini sangat baik untuk analisis data karena memisahkan data master (seperti nama kota atau kategori) dari data transaksi, sehingga menghindari redundansi data.
## ==================================
## Project Otomatisasi Penjualan
## 📁Otomatisasi Analysis-report-sales
## Berikut adalah flowchart otomatisasi laporan Penjualan

![alt text](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/Analysis-Report-Sales-Automated/flowchart_alur_utama.png?raw=true)
## Flowchart Alur Utama — dari scheduler → MySQL → kalkulasi → PDF → Gmail, lengkap dengan decision diamond
![alt text](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/Analysis-Report-Sales-Automated/flowchart_output_pdf_email.png?raw=true)
## Struktur Output PDF-Gmail

[Business_Insight_Automated_Gmail](https://github.com/arisetiawan2003-alt/Project-Data-Analys/blob/main/Analysis-Report-Sales-Automated/laporan_penjualan_2026_03.pdf) *Klik link untuk melihat hasil laporannya*

