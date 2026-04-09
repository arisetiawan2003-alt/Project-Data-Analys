

import pandas as pd
import pymysql
from datetime import date
from dateutil.relativedelta import relativedelta
from config import DB_CONFIG, TABLE_CONFIG


def get_koneksi():
    """Buat koneksi ke database MySQL."""
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def get_periode_bulan_lalu():
    """Hitung awal dan akhir bulan lalu."""
    hari_ini   = date.today()
    awal       = hari_ini.replace(day=1) - relativedelta(months=1)
    akhir      = hari_ini.replace(day=1) - relativedelta(days=1)
    return awal, akhir


def _parse_tanggal(val):
    """
    Normalisasi nilai tanggal ke datetime.date.
    Menangani: datetime.datetime, datetime.date, dan berbagai format string.
    """
    if val is None:
        return None
    if hasattr(val, "date"):               # datetime.datetime → date
        return val.date()
    if isinstance(val, date):              # sudah datetime.date
        return val
    # Fallback: string dengan berbagai format umum
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
                "%Y%m%d", "%d %b %Y", "%d %B %Y"):
        try:
            return pd.to_datetime(str(val), format=fmt).date()
        except ValueError:
            continue
    # Last resort: biarkan pandas tebak sendiri
    return pd.to_datetime(str(val)).date()


def _parse_angka(val):
    """
    Normalisasi nilai numerik dari berbagai format string database.
    Menangani: int/float langsung, format ribuan (1.234 atau 1,234),
    format desimal koma (1.234,56), simbol mata uang, dll.
    """
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)

    raw = str(val).strip()
    # Hapus simbol mata uang dan spasi
    raw = raw.replace("Rp", "").replace("IDR", "").replace(" ", "").strip()

    # Format: 1.234,56 (ribuan=titik, desimal=koma) → 1234.56
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    # Format: 1,234 atau 1,234.56 (ribuan=koma) → hapus koma
    elif "," in raw and "." not in raw:
        raw = raw.replace(",", ".")
    # Format: 1.234 (titik sebagai ribuan tanpa desimal) → hapus titik
    elif "." in raw and raw.count(".") == 1:
        bagian = raw.split(".")
        if len(bagian[1]) == 3:           # titik ribuan (mis. 1.234)
            raw = raw.replace(".", "")
        # else: titik desimal biasa (mis. 1234.56) → biarkan

    try:
        return float(raw)
    except ValueError:
        return 0.0


def ambil_data_penjualan():
    """
    Ambil semua data penjualan bulan lalu.
    Return: (DataFrame pandas, date awal, date akhir)
    """
    T  = TABLE_CONFIG
    awal, akhir = get_periode_bulan_lalu()

    # Bangun kolom SELECT secara dinamis
    kolom_select = [
        f"`{T['kolom_tanggal']}` AS tanggal",
        f"`{T['kolom_produk']}` AS nama_produk",
        f"`{T['kolom_qty']}` AS qty",
        f"`{T['kolom_harga']}` AS harga",
    ]

    if T["kolom_total"]:
        kolom_select.append(f"`{T['kolom_total']}` AS total")
    else:
        kolom_select.append(f"`{T['kolom_qty']}` * `{T['kolom_harga']}` AS total")

    if T["kolom_kategori"]:
        kolom_select.append(f"`{T['kolom_kategori']}` AS kategori")

    if T["kolom_cabang"]:
        kolom_select.append(f"`{T['kolom_cabang']}` AS cabang")

    sql = f"""
        SELECT {', '.join(kolom_select)}
        FROM `{T['tabel']}`
        WHERE `{T['kolom_tanggal']}` BETWEEN %s AND %s
        ORDER BY `{T['kolom_tanggal']}` ASC
    """

    # Gunakan cursor langsung (bukan pd.read_sql) agar tidak ada
    # parsing otomatis yang salah tipe dari pandas/SQLAlchemy
    conn = get_koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (awal, akhir))
            rows = cur.fetchall()          # list of dict (DictCursor)
    finally:
        conn.close()

    df = pd.DataFrame(rows)

    if df.empty:
        return df, awal, akhir

    # --- Normalisasi kolom tanggal ---
    df["tanggal"] = df["tanggal"].apply(_parse_tanggal)

    # --- Normalisasi kolom numerik ---
    for col in ["qty", "harga", "total"]:
        if col in df.columns:
            df[col] = df[col].apply(_parse_angka)

    return df, awal, akhir


def ambil_ringkasan(df):
    """
    Hitung ringkasan statistik dari DataFrame penjualan.
    Return: dict berisi angka-angka ringkasan
    """
    ringkasan = {
        "total_transaksi":  len(df),
        "total_pendapatan": df["total"].sum(),
        "rata_rata_harian": df.groupby("tanggal")["total"].sum().mean(),
        "total_qty":        df["qty"].sum(),
        "hari_terlaris":    None,
        "produk_terlaris":  None,
        "per_produk":       None,
        "per_kategori":     None,
        "per_cabang":       None,
    }

    # Hari dengan penjualan tertinggi
    penjualan_per_hari = df.groupby("tanggal")["total"].sum()
    if not penjualan_per_hari.empty:
        ringkasan["hari_terlaris"] = {
            "tanggal": penjualan_per_hari.idxmax(),
            "total":   penjualan_per_hari.max(),
        }

    # Produk terlaris berdasarkan qty
    per_produk = df.groupby("nama_produk").agg(
        total_qty=("qty", "sum"),
        total_pendapatan=("total", "sum"),
    ).sort_values("total_pendapatan", ascending=False).reset_index()

    ringkasan["produk_terlaris"] = per_produk.iloc[0]["nama_produk"] if not per_produk.empty else "-"
    ringkasan["per_produk"]      = per_produk

    # Per kategori (jika ada)
    if "kategori" in df.columns:
        ringkasan["per_kategori"] = (
            df.groupby("kategori")["total"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
            .rename(columns={"total": "total_pendapatan"})
        )

    # Per cabang (jika ada)
    if "cabang" in df.columns:
        ringkasan["per_cabang"] = (
            df.groupby("cabang")["total"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
            .rename(columns={"total": "total_pendapatan"})
        )

    return ringkasan