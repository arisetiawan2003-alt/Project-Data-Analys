
USE ecommerce_project;
-- Cek struktur semua tabel
DESCRIBE orders;
DESCRIBE products;
DESCRIBE categories;
DESCRIBE brands;
DESCRIBE platforms;
DESCRIBE cities;

-- Cek jumlah baris semua tabel
SELECT 'orders'     AS Tabel, COUNT(*) AS Baris FROM orders     UNION ALL
SELECT 'products',             COUNT(*)          FROM products   UNION ALL
SELECT 'categories',           COUNT(*)          FROM categories UNION ALL
SELECT 'brands',               COUNT(*)          FROM brands     UNION ALL
SELECT 'platforms',            COUNT(*)          FROM platforms  UNION ALL
SELECT 'cities',               COUNT(*)          FROM cities;

-- Cek sample data
SELECT * FROM orders     LIMIT 5;
SELECT * FROM products   LIMIT 5;
SELECT * FROM categories LIMIT 5;
SELECT * FROM brands     LIMIT 5;
SELECT * FROM platforms  LIMIT 5;
SELECT * FROM cities     LIMIT 5;

-- Cek NULL values di kolom penting
SELECT
    COUNT(*)                                    AS TotalBaris,
    SUM(CASE WHEN TotalAmount IS NULL THEN 1 ELSE 0 END) AS Null_TotalAmount,
    SUM(CASE WHEN Rating      IS NULL THEN 1 ELSE 0 END) AS Null_Rating,
    SUM(CASE WHEN OrderDate   IS NULL THEN 1 ELSE 0 END) AS Null_OrderDate,
    SUM(CASE WHEN ProductID   IS NULL THEN 1 ELSE 0 END) AS Null_ProductID
FROM orders;


-- ============================================================
-- 📌 SECTION 1 — EXECUTIVE SUMMARY (KPI UTAMA)
-- ============================================================

SELECT
    -- Revenue
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))             AS Total_Revenue,
    -- Order
    COUNT(o.OrderID)                                         AS Total_Order,
    -- AOV (Average Order Value)
    CONCAT('$ ', FORMAT(AVG(o.TotalAmount), 2))              AS AOV,
    -- Rating
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating,
    -- Dimensi
    COUNT(DISTINCT pl.PlatformName)                          AS Jumlah_Platform,
    COUNT(DISTINCT ct.CategoryName)                          AS Jumlah_Kategori,
    COUNT(DISTINCT c.CityName)                               AS Jumlah_Kota,
    COUNT(DISTINCT b.BrandName)                              AS Jumlah_Brand,
    COUNT(DISTINCT p.ProductName)                            AS Jumlah_Produk,
    -- Periode
    MIN(o.OrderDate)                                         AS Tanggal_Awal,
    MAX(o.OrderDate)                                         AS Tanggal_Akhir
FROM orders o
INNER JOIN products   p  ON o.ProductID  = p.ProductID
INNER JOIN platforms  pl ON o.PlatformID = pl.PlatformID
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
INNER JOIN cities     c  ON o.CityID     = c.CityID
INNER JOIN brands     b  ON p.BrandID    = b.BrandID;


-- ============================================================
-- 📌 SECTION 2 — ANALISIS PLATFORM
-- ============================================================

-- 2A. Performa per Platform
SELECT
    pl.PlatformName                                          AS Platform,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue,
    CONCAT('$ ', FORMAT(AVG(o.TotalAmount), 2))              AS AOV,
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating,
    CONCAT(ROUND(COUNT(o.OrderID) * 100.0 /
           SUM(COUNT(o.OrderID)) OVER(), 1), '%')            AS Market_Share
FROM orders o
INNER JOIN platforms pl ON o.PlatformID = pl.PlatformID
GROUP BY pl.PlatformName
ORDER BY SUM(o.TotalAmount) DESC;

-- 2B. Order Bagus vs Jelek per Platform
SELECT
    pl.PlatformName                                                            AS Platform,
    COUNT(*)                                                                   AS Total_Order,
    SUM(CASE WHEN o.Rating >= 4 THEN 1 ELSE 0 END)                            AS Order_Bagus,
    SUM(CASE WHEN o.Rating <  4 THEN 1 ELSE 0 END)                            AS Order_Jelek,
    CONCAT(ROUND(SUM(CASE WHEN o.Rating >= 4 THEN 1 ELSE 0 END)
           * 100.0 / COUNT(*), 1), '%')                                        AS Pct_Bagus
FROM orders o
INNER JOIN platforms pl ON o.PlatformID = pl.PlatformID
GROUP BY pl.PlatformName
ORDER BY COUNT(*) DESC;

-- 2C. Revenue per Platform per Kategori (PIVOT)
SELECT
    ct.CategoryName,
    CONCAT('$ ', FORMAT(SUM(CASE WHEN pl.PlatformName = 'Souq'   THEN o.TotalAmount ELSE 0 END), 2)) AS Rev_Souq,
    CONCAT('$ ', FORMAT(SUM(CASE WHEN pl.PlatformName = 'Jumia'  THEN o.TotalAmount ELSE 0 END), 2)) AS Rev_Jumia,
    CONCAT('$ ', FORMAT(SUM(CASE WHEN pl.PlatformName = 'Amazon' THEN o.TotalAmount ELSE 0 END), 2)) AS Rev_Amazon,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))                                                       AS Total_Revenue
FROM orders o
INNER JOIN products   p  ON o.ProductID  = p.ProductID
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
INNER JOIN platforms  pl ON o.PlatformID = pl.PlatformID
GROUP BY ct.CategoryName
ORDER BY SUM(o.TotalAmount) DESC;


-- ============================================================
-- 📌 SECTION 3 — ANALISIS KATEGORI PRODUK
-- ============================================================

-- 3A. Performa per Kategori
SELECT
    ct.CategoryName                                          AS Kategori,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue,
    CONCAT('$ ', FORMAT(AVG(o.TotalAmount), 2))              AS AOV,
    CONCAT('$ ', FORMAT(MAX(o.TotalAmount), 2))              AS Revenue_Tertinggi,
    CONCAT('$ ', FORMAT(MIN(o.TotalAmount), 2))              AS Revenue_Terendah,
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating,
    -- Status kategori
    CASE
        WHEN AVG(o.Rating)    >= 4
         AND COUNT(o.OrderID) >= 2000 THEN '🏆 TOP CATEGORY'
        WHEN AVG(o.Rating)    >= 4    THEN '⭐ HIGH RATED'
        WHEN COUNT(o.OrderID) >= 2000 THEN '📦 HIGH DEMAND'
        ELSE                               '📊 AVERAGE'
    END                                                      AS Status
FROM orders o
INNER JOIN products   p  ON o.ProductID  = p.ProductID
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
GROUP BY ct.CategoryName
ORDER BY SUM(o.TotalAmount) DESC;

-- 3B. Segmentasi Order per Kategori
SELECT
    ct.CategoryName,
    SUM(CASE WHEN o.TotalAmount >= 50000 THEN 1 ELSE 0 END)  AS High_Value,
    SUM(CASE WHEN o.TotalAmount >= 20000
             AND o.TotalAmount <  50000 THEN 1 ELSE 0 END)   AS Mid_Value,
    SUM(CASE WHEN o.TotalAmount >= 5000
             AND o.TotalAmount <  20000 THEN 1 ELSE 0 END)   AS Low_Value,
    SUM(CASE WHEN o.TotalAmount <  5000  THEN 1 ELSE 0 END)  AS Micro,
    COUNT(*)                                                  AS Total_Order
FROM orders o
INNER JOIN products   p  ON o.ProductID  = p.ProductID
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
GROUP BY ct.CategoryName
ORDER BY Total_Order DESC;


-- ============================================================
-- 📌 SECTION 4 — ANALISIS PRODUK
-- ============================================================

-- 4A. Top 10 Produk Terlaris (by Revenue)
SELECT
    p.ProductName                                            AS Produk,
    ct.CategoryName                                          AS Kategori,
    b.BrandName                                              AS Brand,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue,
    CONCAT('$ ', FORMAT(AVG(o.TotalAmount), 2))              AS AOV,
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating
FROM orders o
INNER JOIN products   p  ON o.ProductID  = p.ProductID
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
INNER JOIN brands     b  ON p.BrandID    = b.BrandID
GROUP BY p.ProductName, ct.CategoryName, b.BrandName
ORDER BY SUM(o.TotalAmount) DESC
LIMIT 10;

-- 4B. Ranking Produk per Kategori (Window Function)
SELECT
    Kategori, Produk, Total_Order, Total_Revenue,
    RANK() OVER (
        PARTITION BY Kategori
        ORDER BY Total_Revenue DESC
    ) AS Ranking_Dalam_Kategori
FROM (
    SELECT
        ct.CategoryName                  AS Kategori,
        p.ProductName                    AS Produk,
        COUNT(o.OrderID)                 AS Total_Order,
        SUM(o.TotalAmount)               AS Total_Revenue
    FROM orders o
    INNER JOIN products   p  ON o.ProductID  = p.ProductID
    INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
    GROUP BY ct.CategoryName, p.ProductName
) ranking
ORDER BY Kategori, Ranking_Dalam_Kategori;

-- 4C. Produk dengan Rating Tertinggi (min 100 order)
SELECT
    p.ProductName                                            AS Produk,
    ct.CategoryName                                          AS Kategori,
    COUNT(o.OrderID)                                         AS Total_Order,
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue
FROM orders o
INNER JOIN products   p  ON o.ProductID  = p.ProductID
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
GROUP BY p.ProductName, ct.CategoryName
HAVING COUNT(o.OrderID) >= 100
ORDER BY AVG(o.Rating) DESC
LIMIT 10;


-- ============================================================
-- 📌 SECTION 5 — ANALISIS BRAND
-- ============================================================

-- 5A. Performa per Brand
SELECT
    b.BrandName                                              AS Brand,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue,
    CONCAT('$ ', FORMAT(AVG(o.TotalAmount), 2))              AS AOV,
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating,
    -- Status brand
    CASE
        WHEN SUM(o.TotalAmount) >= 5000000
         AND AVG(o.Rating)      >= 4       THEN '🌟 STAR BRAND'
        WHEN SUM(o.TotalAmount) >= 5000000 THEN '💰 HIGH REVENUE'
        WHEN AVG(o.Rating)      >= 4       THEN '❤️ CUSTOMER FAVORITE'
        ELSE                                    '📈 NEEDS IMPROVEMENT'
    END                                                      AS Status_Brand
FROM orders o
INNER JOIN products p ON o.ProductID = p.ProductID
INNER JOIN brands   b ON p.BrandID   = b.BrandID
GROUP BY b.BrandName
ORDER BY SUM(o.TotalAmount) DESC;

-- 5B. Revenue per Brand per Platform (PIVOT)
SELECT
    b.BrandName,
    CONCAT('$ ', FORMAT(SUM(CASE WHEN pl.PlatformName = 'Souq'   THEN o.TotalAmount ELSE 0 END), 2)) AS Rev_Souq,
    CONCAT('$ ', FORMAT(SUM(CASE WHEN pl.PlatformName = 'Jumia'  THEN o.TotalAmount ELSE 0 END), 2)) AS Rev_Jumia,
    CONCAT('$ ', FORMAT(SUM(CASE WHEN pl.PlatformName = 'Amazon' THEN o.TotalAmount ELSE 0 END), 2)) AS Rev_Amazon,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))                                                       AS Total_Revenue
FROM orders o
INNER JOIN products  p  ON o.ProductID  = p.ProductID
INNER JOIN brands    b  ON p.BrandID    = b.BrandID
INNER JOIN platforms pl ON o.PlatformID = pl.PlatformID
GROUP BY b.BrandName
ORDER BY SUM(o.TotalAmount) DESC;


-- ============================================================
-- 📌 SECTION 6 — ANALISIS KOTA
-- ============================================================

-- 6A. Performa per Kota
SELECT
    c.CityName                                               AS Kota,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue,
    CONCAT('$ ', FORMAT(AVG(o.TotalAmount), 2))              AS AOV,
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating,
    CONCAT(ROUND(COUNT(o.OrderID) * 100.0 /
           SUM(COUNT(o.OrderID)) OVER(), 1), '%')            AS Market_Share
FROM orders o
INNER JOIN cities c ON o.CityID = c.CityID
GROUP BY c.CityName
ORDER BY SUM(o.TotalAmount) DESC;

-- 6B. Performa Kota per Kategori
SELECT
    c.CityName,
    ct.CategoryName,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue,
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating,
    CASE
        WHEN COUNT(o.OrderID)   >= 300
         AND SUM(o.TotalAmount) >= 1000000 THEN '🔥 EXCELLENT'
        WHEN COUNT(o.OrderID)   >= 300     THEN '📦 HIGH VOLUME'
        WHEN SUM(o.TotalAmount) >= 1000000 THEN '💵 HIGH VALUE'
        ELSE                                    '📊 NORMAL'
    END                                                      AS Performa
FROM orders o
INNER JOIN products   p  ON o.ProductID  = p.ProductID
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
INNER JOIN cities     c  ON o.CityID     = c.CityID
GROUP BY c.CityName, ct.CategoryName
ORDER BY SUM(o.TotalAmount) DESC
LIMIT 20;


-- ============================================================
-- 📌 SECTION 7 — ANALISIS TREN WAKTU
-- ============================================================

-- 7A. Revenue & Order per Bulan
SELECT
    DATE_FORMAT(o.OrderDate, '%Y-%m')                        AS Bulan,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue,
    CONCAT('$ ', FORMAT(AVG(o.TotalAmount), 2))              AS AOV,
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating
FROM orders o
GROUP BY DATE_FORMAT(o.OrderDate, '%Y-%m')
ORDER BY Bulan;

-- 7B. Revenue per Bulan per Platform
SELECT
    DATE_FORMAT(o.OrderDate, '%Y-%m')                        AS Bulan,
    pl.PlatformName                                          AS Platform,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue
FROM orders o
INNER JOIN platforms pl ON o.PlatformID = pl.PlatformID
GROUP BY DATE_FORMAT(o.OrderDate, '%Y-%m'), pl.PlatformName
ORDER BY Bulan, SUM(o.TotalAmount) DESC;

-- 7C. Running Total Revenue per Bulan (Window Function)
SELECT
    Bulan,
    Total_Order,
    Total_Revenue,
    CONCAT('$ ', FORMAT(
        SUM(Total_Revenue) OVER (ORDER BY Bulan), 2)
    )                                                        AS Running_Total
FROM (
    SELECT
        DATE_FORMAT(o.OrderDate, '%Y-%m')  AS Bulan,
        COUNT(o.OrderID)                   AS Total_Order,
        SUM(o.TotalAmount)                 AS Total_Revenue
    FROM orders o
    GROUP BY DATE_FORMAT(o.OrderDate, '%Y-%m')
) bulanan
ORDER BY Bulan;

-- 7D. Perbandingan Revenue Bulan Ini vs Bulan Lalu (LAG)
SELECT
    Bulan,
    CONCAT('$ ', FORMAT(Total_Revenue, 2))                   AS Revenue,
    CONCAT('$ ', FORMAT(LAG(Total_Revenue) OVER
           (ORDER BY Bulan), 2))                             AS Revenue_BulanLalu,
    CONCAT(ROUND((Total_Revenue - LAG(Total_Revenue)
           OVER (ORDER BY Bulan))
           / LAG(Total_Revenue) OVER (ORDER BY Bulan)
           * 100, 1), '%')                                   AS Growth_MoM
FROM (
    SELECT
        DATE_FORMAT(OrderDate, '%Y-%m')    AS Bulan,
        SUM(TotalAmount)                   AS Total_Revenue
    FROM orders
    GROUP BY DATE_FORMAT(OrderDate, '%Y-%m')
) bulanan
ORDER BY Bulan;


-- ============================================================
-- 📌 SECTION 8 — SEGMENTASI ORDER (CASE WHEN)
-- ============================================================

-- 8A. Distribusi Segmen
SELECT
    CASE
        WHEN TotalAmount >= 50000 THEN '💎 HIGH VALUE'
        WHEN TotalAmount >= 20000 THEN '🥇 MID VALUE'
        WHEN TotalAmount >= 5000  THEN '🥈 LOW VALUE'
        ELSE                          '🥉 MICRO'
    END                                                      AS Segmen,
    COUNT(*)                                                 AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(TotalAmount), 2))                AS Total_Revenue,
    CONCAT('$ ', FORMAT(AVG(TotalAmount), 2))                AS AOV,
    ROUND(AVG(Rating), 2)                                    AS Avg_Rating,
    CONCAT(ROUND(COUNT(*) * 100.0 /
           SUM(COUNT(*)) OVER(), 1), '%')                    AS Pct_Order
FROM orders
GROUP BY Segmen
ORDER BY SUM(TotalAmount) DESC;

-- 8B. Segmentasi Rating
SELECT
    CASE
        WHEN Rating >= 4.5 THEN '⭐ Excellent (4.5-5)'
        WHEN Rating >= 3.5 THEN '👍 Good (3.5-4.4)'
        WHEN Rating >= 2.5 THEN '😐 Average (2.5-3.4)'
        WHEN Rating >  0   THEN '👎 Poor (< 2.5)'
        ELSE                    '❓ No Rating'
    END                                                      AS Label_Rating,
    COUNT(*)                                                 AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(TotalAmount), 2))                AS Total_Revenue,
    CONCAT(ROUND(COUNT(*) * 100.0 /
           SUM(COUNT(*)) OVER(), 1), '%')                    AS Pct_Order
FROM orders
GROUP BY Label_Rating
ORDER BY SUM(TotalAmount) DESC;


-- ============================================================
-- SECTION 9 — ANALISIS LANJUT (CTE + WINDOW FUNCTION)
-- ============================================================

-- 9A. Top 3 Produk per Kategori (Window Function)
SELECT Kategori, Ranking, Produk, Total_Order, Total_Revenue
FROM (
    SELECT
        ct.CategoryName                                      AS Kategori,
        p.ProductName                                        AS Produk,
        COUNT(o.OrderID)                                     AS Total_Order,
        CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))          AS Total_Revenue,
        RANK() OVER (
            PARTITION BY ct.CategoryName
            ORDER BY SUM(o.TotalAmount) DESC
        )                                                    AS Ranking
    FROM orders o
    INNER JOIN products   p  ON o.ProductID  = p.ProductID
    INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
    GROUP BY ct.CategoryName, p.ProductName
) ranked
WHERE Ranking <= 3
ORDER BY Kategori, Ranking;

-- 9B. Platform di atas rata-rata revenue (CTE)
WITH revenue_platform AS (
    SELECT
        pl.PlatformName,
        SUM(o.TotalAmount)   AS Total_Revenue,
        COUNT(o.OrderID)     AS Total_Order
    FROM orders o
    INNER JOIN platforms pl ON o.PlatformID = pl.PlatformID
    GROUP BY pl.PlatformName
),
rata_global AS (
    SELECT AVG(Total_Revenue) AS Rata_Revenue
    FROM revenue_platform
)
SELECT
    rp.PlatformName,
    CONCAT('$ ', FORMAT(rp.Total_Revenue, 2))                AS Total_Revenue,
    CONCAT('$ ', FORMAT(rg.Rata_Revenue,  2))                AS Rata_Global,
    CASE
        WHEN rp.Total_Revenue > rg.Rata_Revenue THEN '✅ Di Atas Rata-rata'
        ELSE                                         '❌ Di Bawah Rata-rata'
    END                                                      AS Status
FROM revenue_platform rp
JOIN rata_global rg ON 1=1
ORDER BY rp.Total_Revenue DESC;

-- 9C. Produk yang belum pernah dipesan (EXISTS)
SELECT
    p.ProductName,
    ct.CategoryName,
    b.BrandName,
    CONCAT('$ ', FORMAT(p.Price, 2))                         AS Harga
FROM products p
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
INNER JOIN brands     b  ON p.BrandID    = b.BrandID
WHERE NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.ProductID = p.ProductID
);

-- 9D. Grand Total dengan ROLLUP
SELECT
    COALESCE(ct.CategoryName, '📊 GRAND TOTAL')              AS Kategori,
    COALESCE(b.BrandName,     '— Subtotal')                  AS Brand,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount), 2))              AS Total_Revenue
FROM orders o
INNER JOIN products   p  ON o.ProductID  = p.ProductID
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
INNER JOIN brands     b  ON p.BrandID    = b.BrandID
GROUP BY ct.CategoryName, b.BrandName WITH ROLLUP
ORDER BY ct.CategoryName, SUM(o.TotalAmount) DESC;


-- ============================================================
-- 📌 SECTION 10 — LAPORAN FINAL EKSEKUTIF
-- ============================================================

-- Laporan lengkap semua dimensi dalam 1 query
SELECT
    ct.CategoryName                                          AS Kategori,
    b.BrandName                                              AS Brand,
    pl.PlatformName                                          AS Platform,
    c.CityName                                               AS Kota,
    COUNT(o.OrderID)                                         AS Total_Order,
    CONCAT('$ ', FORMAT(SUM(o.TotalAmount),  2))             AS Total_Revenue,
    CONCAT('$ ', FORMAT(AVG(o.TotalAmount),  2))             AS AOV,
    CONCAT('$ ', FORMAT(MAX(o.TotalAmount),  2))             AS Tertinggi,
    CONCAT('$ ', FORMAT(MIN(o.TotalAmount),  2))             AS Terendah,
    ROUND(AVG(o.Rating), 2)                                  AS Avg_Rating,
    SUM(CASE WHEN o.Rating >= 4 THEN 1 ELSE 0 END)           AS Order_Bagus,
    SUM(CASE WHEN o.Rating <  4 THEN 1 ELSE 0 END)           AS Order_Jelek,
    CONCAT(ROUND(SUM(CASE WHEN o.Rating >= 4 THEN 1 ELSE 0 END)
           * 100.0 / COUNT(*), 1), '%')                      AS Pct_Order_Bagus,
    -- Status performa
    CASE
        WHEN AVG(o.Rating)    >= 4
         AND COUNT(o.OrderID) >= 500 THEN '🏆 EXCELLENT'
        WHEN AVG(o.Rating)    >= 4   THEN '⭐ HIGH RATED'
        WHEN COUNT(o.OrderID) >= 500 THEN '📦 HIGH DEMAND'
        ELSE                              '📊 NORMAL'
    END                                                      AS Status
FROM orders o
INNER JOIN products   p  ON o.ProductID  = p.ProductID
INNER JOIN categories ct ON p.CategoryID = ct.CategoryID
INNER JOIN brands     b  ON p.BrandID    = b.BrandID
INNER JOIN platforms  pl ON o.PlatformID = pl.PlatformID
INNER JOIN cities     c  ON o.CityID     = c.CityID
GROUP BY ct.CategoryName, b.BrandName, pl.PlatformName, c.CityName
ORDER BY SUM(o.TotalAmount) DESC
LIMIT 50;


-- ============================================================
-- RINGKASAN MATERI YANG DIPAKAI DI PROJECT INI
-- ============================================================
-- Section 0  : DESCRIBE, COUNT, UNION ALL, NULL check
-- Section 1  : JOIN 5 tabel, KPI summary, MIN/MAX
-- Section 2  : GROUP BY, FORMAT, Conditional SUM, PIVOT
-- Section 3  : CASE WHEN + GROUP BY, HAVING, segmentasi
-- Section 4  : TOP N, RANK() OVER, PARTITION BY, HAVING
-- Section 5  : PIVOT, StatusBrand logic
-- Section 6  : Market share, multi-kondisi CASE WHEN
-- Section 7  : DATE_FORMAT, Running Total, LAG() MoM Growth
-- Section 8  : Segmentasi nilai & rating, Window OVER()
-- Section 9  : CTE (WITH AS), EXISTS, NOT EXISTS, ROLLUP
-- Section 10 : Full JOIN 5 tabel, laporan eksekutif lengkap
-- ============================================================