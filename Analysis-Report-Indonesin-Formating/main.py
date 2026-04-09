# =============================================================
# main.py — Entry Point & Scheduler Bulanan
# =============================================================
#
# CARA PAKAI:
#   1. Jalankan sekali untuk test langsung:
#        python main.py --test
#
#   2. Jalankan scheduler (berjalan terus di background):
#        python main.py
#
#   3. Untuk jalan otomatis saat Windows startup:
#      → lihat README.md bagian "Autostart di Windows"
# =============================================================

import sys
import logging
import os
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from config import JADWAL_CONFIG
from query import ambil_data_penjualan, ambil_ringkasan
from generate_pdf import buat_pdf
from kirim_email import kirim_email

# ---- Setup logging ----
LOG_FILE = os.path.join(os.path.dirname(__file__), "laporan.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def jalankan_laporan():
    """
    Fungsi utama: ambil data → buat PDF → kirim email.
    Dipanggil oleh scheduler atau --test flag.
    """
    logger.info("=" * 60)
    logger.info("Memulai proses laporan penjualan bulanan...")

    try:
        # 1. Ambil data dari MySQL
        logger.info("Mengambil data dari database...")
        df, awal, akhir = ambil_data_penjualan()

        if df.empty:
            logger.warning("⚠️  Tidak ada data penjualan untuk periode ini. Email tidak dikirim.")
            return

        logger.info(f"Data berhasil diambil: {len(df)} baris | {awal} s/d {akhir}")

        # 2. Hitung ringkasan
        logger.info("Menghitung ringkasan statistik...")
        ringkasan = ambil_ringkasan(df)
        logger.info(f"Total pendapatan: Rp {ringkasan['total_pendapatan']:,.0f}")

        # 3. Generate PDF
        logger.info("Membuat laporan PDF...")
        pdf_path = buat_pdf(df, ringkasan, awal, akhir)
        logger.info(f"PDF dibuat: {pdf_path}")

        # 4. Kirim email
        logger.info("Mengirim email...")
        kirim_email(pdf_path, ringkasan, awal, akhir)

        logger.info("✅ Proses selesai!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        raise


def listener_job(event):
    """Log hasil eksekusi job scheduler."""
    if event.exception:
        logger.error(f"Job gagal: {event.exception}")
    else:
        logger.info("Job selesai dengan sukses.")


def mulai_scheduler():
    """Jalankan APScheduler dengan jadwal bulanan dari config."""
    scheduler = BlockingScheduler(timezone=JADWAL_CONFIG["timezone"])

    scheduler.add_job(
        jalankan_laporan,
        trigger="cron",
        day=JADWAL_CONFIG["hari"],
        hour=JADWAL_CONFIG["jam"],
        minute=JADWAL_CONFIG["menit"],
        id="laporan_bulanan",
        name="Laporan Penjualan Bulanan",
        misfire_grace_time=3600,  # toleransi 1 jam jika PC mati saat jadwal
    )

    scheduler.add_listener(listener_job, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    logger.info("🚀 Scheduler aktif!")
    logger.info(
        f"   Laporan akan dikirim setiap tanggal {JADWAL_CONFIG['hari']} "
        f"pukul {JADWAL_CONFIG['jam']:02d}:{JADWAL_CONFIG['menit']:02d} WIB"
    )
    logger.info("   Tekan Ctrl+C untuk menghentikan.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler dihentikan.")
        scheduler.shutdown()


# ---- Entry Point ----
if __name__ == "__main__":
    if "--test" in sys.argv:
        logger.info("MODE TEST: menjalankan laporan sekarang...")
        jalankan_laporan()
    else:
        mulai_scheduler()
