# =============================================================
# kirim_email.py — Kirim Email dengan Attachment PDF via Gmail
# =============================================================

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date

from config import EMAIL_CONFIG, PERUSAHAAN


def format_rupiah(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")


def buat_body_html(ringkasan, awal, akhir, periode_label):
    """Buat isi email dalam format HTML yang rapi."""

    produk_terlaris = ringkasan.get("produk_terlaris", "-")
    total_pendapatan = format_rupiah(ringkasan.get("total_pendapatan", 0))
    total_transaksi  = f"{ringkasan.get('total_transaksi', 0):,}"
    rata_harian      = format_rupiah(ringkasan.get("rata_rata_harian", 0))

    hari_terlaris_str = ""
    if ringkasan.get("hari_terlaris"):
        import pandas as pd
        ht = ringkasan["hari_terlaris"]
        hari_terlaris_str = f"{pd.to_datetime(ht['tanggal']).strftime('%d %B %Y')} ({format_rupiah(ht['total'])})"

    # Top 5 produk untuk tabel di email
    top5_rows = ""
    if ringkasan.get("per_produk") is not None:
        for i, row in ringkasan["per_produk"].head(5).iterrows():
            rank = ringkasan["per_produk"].index.get_loc(i) + 1
            top5_rows += f"""
            <tr style="background:{'#f8fafc' if rank % 2 == 0 else 'white'}">
                <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;text-align:center">{rank}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0">{row['nama_produk']}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;text-align:right">{row['total_qty']:,.0f}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;text-align:right">{format_rupiah(row['total_pendapatan'])}</td>
            </tr>"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#f0f4f8;font-family:Arial,sans-serif">

      <div style="max-width:600px;margin:24px auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1)">

        <!-- Header -->
        <div style="background:#1a3c5e;padding:28px 32px;text-align:center">
          <h1 style="margin:0;color:white;font-size:20px;letter-spacing:0.5px">
            {PERUSAHAAN['nama']}
          </h1>
          <p style="margin:6px 0 0;color:#a0bcd8;font-size:13px">
            Laporan Penjualan Bulanan — {periode_label}
          </p>
        </div>

        <!-- Intro -->
        <div style="padding:24px 32px 16px">
          <p style="margin:0;color:#4a5568;font-size:14px;line-height:1.6">
            Yth. Tim Management,<br><br>
            Berikut laporan penjualan periode
            <strong>{awal.strftime('%d %B %Y')}</strong> s/d
            <strong>{akhir.strftime('%d %B %Y')}</strong>.
            Laporan lengkap dalam format PDF terlampir.
          </p>
        </div>

        <!-- KPI Cards -->
        <div style="padding:0 32px 24px;display:flex;gap:12px">
          <table width="100%" cellspacing="8" cellpadding="0">
            <tr>
              <td width="50%" style="vertical-align:top">
                <div style="background:#f0f4f8;border-left:4px solid #2e86de;border-radius:6px;padding:14px 16px">
                  <div style="color:#718096;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Total Pendapatan</div>
                  <div style="color:#1a3c5e;font-size:18px;font-weight:bold;margin-top:4px">{total_pendapatan}</div>
                </div>
              </td>
              <td width="50%" style="vertical-align:top">
                <div style="background:#f0f4f8;border-left:4px solid #27ae60;border-radius:6px;padding:14px 16px">
                  <div style="color:#718096;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Total Transaksi</div>
                  <div style="color:#1a3c5e;font-size:18px;font-weight:bold;margin-top:4px">{total_transaksi}</div>
                </div>
              </td>
            </tr>
            <tr>
              <td style="vertical-align:top;padding-top:8px">
                <div style="background:#f0f4f8;border-left:4px solid #f39c12;border-radius:6px;padding:14px 16px">
                  <div style="color:#718096;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Rata-rata/Hari</div>
                  <div style="color:#1a3c5e;font-size:18px;font-weight:bold;margin-top:4px">{rata_harian}</div>
                </div>
              </td>
              <td style="vertical-align:top;padding-top:8px">
                <div style="background:#f0f4f8;border-left:4px solid #e74c3c;border-radius:6px;padding:14px 16px">
                  <div style="color:#718096;font-size:11px;text-transform:uppercase;letter-spacing:0.5px">Produk Terlaris</div>
                  <div style="color:#1a3c5e;font-size:15px;font-weight:bold;margin-top:4px">{produk_terlaris}</div>
                </div>
              </td>
            </tr>
          </table>
        </div>

        {"<!-- Hari Terlaris -->" + f'<div style="padding:0 32px 16px"><p style="margin:0;background:#fffbeb;border:1px solid #f6d860;border-radius:6px;padding:12px 16px;color:#744210;font-size:13px">📅 <strong>Hari terlaris:</strong> ' + hari_terlaris_str + '</p></div>' if hari_terlaris_str else ""}

        <!-- Top 5 Produk -->
        <div style="padding:0 32px 24px">
          <h3 style="margin:0 0 12px;color:#1a3c5e;font-size:14px">🏆 Top 5 Produk</h3>
          <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden">
            <thead>
              <tr style="background:#1a3c5e">
                <th style="padding:10px 12px;color:white;font-size:12px;text-align:center">#</th>
                <th style="padding:10px 12px;color:white;font-size:12px;text-align:left">Produk</th>
                <th style="padding:10px 12px;color:white;font-size:12px;text-align:right">Qty</th>
                <th style="padding:10px 12px;color:white;font-size:12px;text-align:right">Pendapatan</th>
              </tr>
            </thead>
            <tbody>{top5_rows}</tbody>
          </table>
        </div>

        <!-- Catatan lampiran -->
        <div style="padding:0 32px 24px">
          <div style="background:#ebf8ff;border:1px solid #bee3f8;border-radius:6px;padding:12px 16px">
            <p style="margin:0;color:#2c5282;font-size:13px">
              📎 Laporan lengkap beserta grafik dan detail transaksi tersedia pada lampiran PDF.
            </p>
          </div>
        </div>

        <!-- Footer -->
        <div style="background:#f7fafc;padding:16px 32px;border-top:1px solid #e2e8f0;text-align:center">
          <p style="margin:0;color:#a0aec0;font-size:11px">
            Email ini dikirim otomatis oleh sistem laporan {PERUSAHAAN['nama']}<br>
            {date.today().strftime('%d %B %Y')}
          </p>
        </div>

      </div>
    </body>
    </html>
    """
    return html


def kirim_email(pdf_path, ringkasan, awal, akhir):
    """Kirim email dengan attachment PDF laporan penjualan."""

    bulan_nama = {
        1:"Januari",2:"Februari",3:"Maret",4:"April",
        5:"Mei",6:"Juni",7:"Juli",8:"Agustus",
        9:"September",10:"Oktober",11:"November",12:"Desember",
    }
    periode_label = f"{bulan_nama[awal.month]} {awal.year}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Laporan Penjualan Bulanan — {periode_label} | {PERUSAHAAN['nama']}"
    msg["From"]    = EMAIL_CONFIG["pengirim"]
    msg["To"]      = ", ".join(EMAIL_CONFIG["penerima"])

    # Body email HTML
    html_body = buat_body_html(ringkasan, awal, akhir, periode_label)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Attach PDF
    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        nama_file = os.path.basename(pdf_path)
        part.add_header("Content-Disposition", f'attachment; filename="{nama_file}"')
        msg.attach(part)

    # Kirim via Gmail SMTP
    try:
        with smtplib.SMTP(EMAIL_CONFIG["smtp_host"], EMAIL_CONFIG["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_CONFIG["pengirim"], EMAIL_CONFIG["password"])
            server.sendmail(
                EMAIL_CONFIG["pengirim"],
                EMAIL_CONFIG["penerima"],
                msg.as_string(),
            )
        print(f"✅ Email berhasil dikirim ke: {EMAIL_CONFIG['penerima']}")
    except smtplib.SMTPAuthenticationError:
        print("❌ Gagal login Gmail. Pastikan App Password sudah benar.")
        raise
    except Exception as e:
        print(f"❌ Gagal kirim email: {e}")
        raise
