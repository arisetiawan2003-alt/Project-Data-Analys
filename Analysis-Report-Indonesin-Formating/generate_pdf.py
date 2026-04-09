# =============================================================
# generate_pdf.py — Buat Laporan PDF Penjualan Bulanan
# =============================================================

import os
import io
from datetime import date
import matplotlib
matplotlib.use("Agg")  # non-GUI backend untuk Windows
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config import PERUSAHAAN

# ---- Warna tema ----
BIRU_TUA  = colors.HexColor("#1a3c5e")
BIRU_MUDA = colors.HexColor("#2e86de")
ABU_MUDA  = colors.HexColor("#f0f4f8")
ABU_TUA   = colors.HexColor("#4a5568")
PUTIH     = colors.white
HIJAU     = colors.HexColor("#27ae60")
MERAH     = colors.HexColor("#e74c3c")
KUNING    = colors.HexColor("#f39c12")

W, H = A4


def format_rupiah(angka):
    if pd.isna(angka):
        return "Rp 0"
    return f"Rp {angka:,.0f}".replace(",", ".")


def buat_chart_harian(df, periode_label):
    """Bar chart penjualan per hari."""
    per_hari = df.groupby("tanggal")["total"].sum().reset_index()
    per_hari["tanggal"] = pd.to_datetime(per_hari["tanggal"])
    per_hari = per_hari.sort_values("tanggal")

    fig, ax = plt.subplots(figsize=(14, 4))
    bars = ax.bar(
        per_hari["tanggal"].dt.strftime("%d"),
        per_hari["total"] / 1_000_000,
        color="#2e86de",
        edgecolor="white",
        linewidth=0.5,
        width=0.7,
    )

    # Highlight bar tertinggi
    max_idx = per_hari["total"].idxmax()
    bars[per_hari.index.get_loc(max_idx)].set_color("#e74c3c")

    ax.set_title(f"Penjualan Harian — {periode_label}", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Tanggal", fontsize=10)
    ax.set_ylabel("Penjualan (Juta Rp)", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("white")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def buat_chart_produk(per_produk):
    """Horizontal bar chart top 10 produk."""
    top = per_produk.head(10).copy()
    top = top.sort_values("total_pendapatan", ascending=True)

    fig, ax = plt.subplots(figsize=(10, max(3, len(top) * 0.55)))
    colors_bar = ["#2e86de"] * len(top)
    colors_bar[-1] = "#e74c3c"  # highlight produk terlaris

    bars = ax.barh(
        top["nama_produk"],
        top["total_pendapatan"] / 1_000_000,
        color=colors_bar,
        edgecolor="white",
        linewidth=0.5,
        height=0.6,
    )

    for bar, val in zip(bars, top["total_pendapatan"]):
        ax.text(
            bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
            f"{val/1_000_000:.1f}M",
            va="center", fontsize=8, color="#4a5568",
        )

    ax.set_title("Top Produk berdasarkan Pendapatan", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Pendapatan (Juta Rp)", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("white")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def buat_pdf(df, ringkasan, awal, akhir):
    """
    Generate PDF laporan penjualan bulanan.
    Return: path file PDF yang dihasilkan
    """
    bulan_nama = {
        1:"Januari",2:"Februari",3:"Maret",4:"April",
        5:"Mei",6:"Juni",7:"Juli",8:"Agustus",
        9:"September",10:"Oktober",11:"November",12:"Desember",
    }
    periode_label = f"{bulan_nama[awal.month]} {awal.year}"
    filename = f"laporan_penjualan_{awal.strftime('%Y_%m')}.pdf"
    filepath = os.path.join(os.path.dirname(__file__), filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.5*cm,  bottomMargin=1.5*cm,
    )

    styles = getSampleStyleSheet()
    elemen = []

    # ---- HEADER ----
    def header_style(size, color=BIRU_TUA, align=TA_CENTER, bold=True):
        return ParagraphStyle(
            "h", fontSize=size, textColor=color,
            alignment=align, fontName="Helvetica-Bold" if bold else "Helvetica",
            spaceAfter=2,
        )

    elemen.append(Paragraph(PERUSAHAAN["nama"].upper(), header_style(16)))
    elemen.append(Paragraph(PERUSAHAAN["alamat"], header_style(9, ABU_TUA, bold=False)))
    elemen.append(Paragraph(f"Telp: {PERUSAHAAN['telpon']}", header_style(9, ABU_TUA, bold=False)))
    elemen.append(HRFlowable(width="100%", thickness=2, color=BIRU_TUA, spaceAfter=6))
    elemen.append(Paragraph(f"LAPORAN PENJUALAN BULANAN", header_style(14)))
    elemen.append(Paragraph(
        f"Periode: {awal.strftime('%d %B %Y')} s/d {akhir.strftime('%d %B %Y')}",
        header_style(10, ABU_TUA, bold=False),
    ))
    elemen.append(Paragraph(
        f"Dicetak: {date.today().strftime('%d %B %Y')}",
        header_style(9, ABU_TUA, bold=False),
    ))
    elemen.append(Spacer(1, 0.5*cm))

    # ---- RINGKASAN (KPI BOXES) ----
    kpi_data = [
        ["Total Transaksi", "Total Pendapatan", "Rata-rata/Hari", "Total Qty Terjual"],
        [
            f"{ringkasan['total_transaksi']:,}",
            format_rupiah(ringkasan["total_pendapatan"]),
            format_rupiah(ringkasan["rata_rata_harian"]),
            f"{ringkasan['total_qty']:,.0f}",
        ],
        ["transaksi", "pendapatan kotor", "per hari", "unit terjual"],
    ]

    kpi_tbl = Table(kpi_data, colWidths=[4.4*cm]*4, rowHeights=[0.7*cm, 1.1*cm, 0.6*cm])
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), BIRU_TUA),
        ("TEXTCOLOR",    (0,0), (-1,0), PUTIH),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0), 9),
        ("BACKGROUND",   (0,1), (-1,1), ABU_MUDA),
        ("FONTNAME",     (0,1), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,1), (-1,1), 12),
        ("TEXTCOLOR",    (0,1), (-1,1), BIRU_TUA),
        ("FONTNAME",     (0,2), (-1,2), "Helvetica"),
        ("FONTSIZE",     (0,2), (-1,2), 8),
        ("TEXTCOLOR",    (0,2), (-1,2), ABU_TUA),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("BOX",          (0,0), (-1,-1), 1, BIRU_MUDA),
        ("INNERGRID",    (0,0), (-1,-1), 0.5, colors.HexColor("#d0dae8")),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [None]),
    ]))
    elemen.append(kpi_tbl)
    elemen.append(Spacer(1, 0.5*cm))

    # Highlight produk & hari terlaris
    info_style = ParagraphStyle("info", fontSize=9, textColor=ABU_TUA,
                                 fontName="Helvetica", spaceAfter=3)
    bold_style = ParagraphStyle("bold", fontSize=9, textColor=BIRU_TUA,
                                 fontName="Helvetica-Bold")

    if ringkasan["hari_terlaris"]:
        ht = ringkasan["hari_terlaris"]
        elemen.append(Paragraph(
            f"📅 Hari terlaris: <b>{pd.to_datetime(ht['tanggal']).strftime('%d %B %Y')}</b> "
            f"— {format_rupiah(ht['total'])}",
            info_style,
        ))
    elemen.append(Paragraph(
        f"🏆 Produk terlaris: <b>{ringkasan['produk_terlaris']}</b>",
        info_style,
    ))
    elemen.append(Spacer(1, 0.4*cm))

    # ---- CHART HARIAN ----
    elemen.append(Paragraph("Grafik Penjualan Harian", header_style(11, BIRU_TUA, TA_LEFT)))
    elemen.append(HRFlowable(width="100%", thickness=0.5, color=BIRU_MUDA, spaceAfter=4))
    chart_harian = buat_chart_harian(df, periode_label)
    elemen.append(Image(chart_harian, width=17*cm, height=5*cm))
    elemen.append(Spacer(1, 0.4*cm))

    # ---- CHART PRODUK ----
    if ringkasan["per_produk"] is not None and not ringkasan["per_produk"].empty:
        elemen.append(Paragraph("Top Produk", header_style(11, BIRU_TUA, TA_LEFT)))
        elemen.append(HRFlowable(width="100%", thickness=0.5, color=BIRU_MUDA, spaceAfter=4))
        chart_produk = buat_chart_produk(ringkasan["per_produk"])
        n_produk = min(10, len(ringkasan["per_produk"]))
        elemen.append(Image(chart_produk, width=15*cm, height=max(3, n_produk * 0.55)*cm))
        elemen.append(Spacer(1, 0.4*cm))

    # ---- TABEL RINGKASAN PER PRODUK ----
    elemen.append(Paragraph("Ringkasan per Produk", header_style(11, BIRU_TUA, TA_LEFT)))
    elemen.append(HRFlowable(width="100%", thickness=0.5, color=BIRU_MUDA, spaceAfter=4))

    per_produk = ringkasan["per_produk"].copy()
    per_produk["total_pendapatan_fmt"] = per_produk["total_pendapatan"].apply(format_rupiah)
    per_produk["persen"] = (per_produk["total_pendapatan"] / per_produk["total_pendapatan"].sum() * 100)

    tabel_produk_data = [["No", "Nama Produk", "Qty Terjual", "Total Pendapatan", "%"]]
    for i, row in per_produk.iterrows():
        tabel_produk_data.append([
            str(per_produk.index.get_loc(i) + 1),
            row["nama_produk"],
            f"{row['total_qty']:,.0f}",
            row["total_pendapatan_fmt"],
            f"{row['persen']:.1f}%",
        ])

    col_w = [0.8*cm, 6.5*cm, 2.5*cm, 4.5*cm, 2*cm]
    tbl = Table(tabel_produk_data, colWidths=col_w, repeatRows=1)
    row_count = len(tabel_produk_data)
    row_bg = [ABU_MUDA if i % 2 == 0 else PUTIH for i in range(1, row_count)]

    style_cmds = [
        ("BACKGROUND",  (0,0), (-1,0), BIRU_TUA),
        ("TEXTCOLOR",   (0,0), (-1,0), PUTIH),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8.5),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("ALIGN",       (1,1), (1,-1), "LEFT"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWHEIGHT",   (0,0), (-1,-1), 0.65*cm),
        ("BOX",         (0,0), (-1,-1), 0.5, BIRU_MUDA),
        ("INNERGRID",   (0,0), (-1,-1), 0.3, colors.HexColor("#d0dae8")),
    ]
    for idx, bg in enumerate(row_bg):
        style_cmds.append(("BACKGROUND", (0, idx+1), (-1, idx+1), bg))

    tbl.setStyle(TableStyle(style_cmds))
    elemen.append(tbl)

    # ---- TABEL PER KATEGORI (jika ada) ----
    if ringkasan["per_kategori"] is not None:
        elemen.append(Spacer(1, 0.4*cm))
        elemen.append(Paragraph("Ringkasan per Kategori", header_style(11, BIRU_TUA, TA_LEFT)))
        elemen.append(HRFlowable(width="100%", thickness=0.5, color=BIRU_MUDA, spaceAfter=4))

        kat_data = [["Kategori", "Total Pendapatan", "%"]]
        total_kat = ringkasan["per_kategori"]["total_pendapatan"].sum()
        for _, row in ringkasan["per_kategori"].iterrows():
            kat_data.append([
                row["kategori"],
                format_rupiah(row["total_pendapatan"]),
                f"{row['total_pendapatan']/total_kat*100:.1f}%",
            ])

        tbl_kat = Table(kat_data, colWidths=[6*cm, 5*cm, 3*cm], repeatRows=1)
        tbl_kat.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BIRU_TUA),
            ("TEXTCOLOR",  (0,0), (-1,0), PUTIH),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("ALIGN",      (0,0), (-1,-1), "CENTER"),
            ("ALIGN",      (0,1), (0,-1), "LEFT"),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("ROWHEIGHT",  (0,0), (-1,-1), 0.65*cm),
            ("BOX",        (0,0), (-1,-1), 0.5, BIRU_MUDA),
            ("INNERGRID",  (0,0), (-1,-1), 0.3, colors.HexColor("#d0dae8")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [ABU_MUDA, PUTIH]),
        ]))
        elemen.append(tbl_kat)

    # ---- TABEL PER CABANG (jika ada) ----
    if ringkasan["per_cabang"] is not None:
        elemen.append(Spacer(1, 0.4*cm))
        elemen.append(Paragraph("Ringkasan per Cabang", header_style(11, BIRU_TUA, TA_LEFT)))
        elemen.append(HRFlowable(width="100%", thickness=0.5, color=BIRU_MUDA, spaceAfter=4))

        cab_data = [["Cabang", "Total Pendapatan", "%"]]
        total_cab = ringkasan["per_cabang"]["total_pendapatan"].sum()
        for _, row in ringkasan["per_cabang"].iterrows():
            cab_data.append([
                row["cabang"],
                format_rupiah(row["total_pendapatan"]),
                f"{row['total_pendapatan']/total_cab*100:.1f}%",
            ])

        tbl_cab = Table(cab_data, colWidths=[6*cm, 5*cm, 3*cm], repeatRows=1)
        tbl_cab.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), BIRU_TUA),
            ("TEXTCOLOR",  (0,0), (-1,0), PUTIH),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("ALIGN",      (0,0), (-1,-1), "CENTER"),
            ("ALIGN",      (0,1), (0,-1), "LEFT"),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("ROWHEIGHT",  (0,0), (-1,-1), 0.65*cm),
            ("BOX",        (0,0), (-1,-1), 0.5, BIRU_MUDA),
            ("INNERGRID",  (0,0), (-1,-1), 0.3, colors.HexColor("#d0dae8")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [ABU_MUDA, PUTIH]),
        ]))
        elemen.append(tbl_cab)

    # ---- DETAIL TRANSAKSI ----
    elemen.append(Spacer(1, 0.4*cm))
    elemen.append(Paragraph("Detail Transaksi", header_style(11, BIRU_TUA, TA_LEFT)))
    elemen.append(HRFlowable(width="100%", thickness=0.5, color=BIRU_MUDA, spaceAfter=4))

    detail_cols = ["tanggal", "nama_produk", "qty", "harga", "total"]
    detail_header = ["Tanggal", "Produk", "Qty", "Harga Satuan", "Total"]
    if "kategori" in df.columns:
        detail_cols.insert(2, "kategori")
        detail_header.insert(2, "Kategori")
    if "cabang" in df.columns:
        detail_cols.append("cabang")
        detail_header.append("Cabang")

    detail_data = [detail_header]
    for _, row in df.iterrows():
        baris = []
        for col in detail_cols:
            val = row.get(col, "")
            if col == "tanggal":
                baris.append(pd.to_datetime(val).strftime("%d/%m/%Y") if pd.notna(val) else "")
            elif col in ("harga", "total"):
                baris.append(format_rupiah(val))
            elif col == "qty":
                baris.append(f"{val:,.0f}" if pd.notna(val) else "")
            else:
                baris.append(str(val) if pd.notna(val) else "")
        detail_data.append(baris)

    n_col = len(detail_header)
    col_w_detail = [2.2*cm, 5*cm] + [2.2*cm] * (n_col - 2)
    tbl_detail = Table(detail_data, colWidths=col_w_detail, repeatRows=1)
    tbl_detail.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BIRU_TUA),
        ("TEXTCOLOR",  (0,0), (-1,0), PUTIH),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("ALIGN",      (1,1), (1,-1), "LEFT"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("ROWHEIGHT",  (0,0), (-1,-1), 0.55*cm),
        ("BOX",        (0,0), (-1,-1), 0.5, BIRU_MUDA),
        ("INNERGRID",  (0,0), (-1,-1), 0.2, colors.HexColor("#d0dae8")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [ABU_MUDA, PUTIH]),
    ]))
    elemen.append(tbl_detail)

    # ---- FOOTER ----
    elemen.append(Spacer(1, 0.6*cm))
    elemen.append(HRFlowable(width="100%", thickness=0.5, color=BIRU_MUDA))
    footer_style = ParagraphStyle("footer", fontSize=8, textColor=ABU_TUA,
                                   alignment=TA_CENTER, fontName="Helvetica")
    elemen.append(Paragraph(
        f"Laporan ini dibuat otomatis oleh sistem | {PERUSAHAAN['nama']} | {date.today().strftime('%d %B %Y')}",
        footer_style,
    ))

    doc.build(elemen)
    print(f"✅ PDF berhasil dibuat: {filepath}")
    return filepath
