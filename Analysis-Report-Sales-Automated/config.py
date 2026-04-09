

# --- Database MySQL ---
DB_CONFIG = {
    "host":     "localhost",        
    "port":     3306,
    "user":     "root",             
    "password": "admin123", 
    "database": "ecommerce_project",         
}


TABLE_CONFIG = {
    "tabel":          "orders_backup",   
    "kolom_tanggal":  "OrderDate",     
    "kolom_produk":   "Product", 
    "kolom_qty":      "Quantity",         
    "kolom_harga":    "Price",       
    "kolom_total":    "TotalAmount",       
    "kolom_kategori": "Category",    
    "kolom_cabang":   None,      
}


EMAIL_CONFIG = {
    "pengirim":  "arilarariasti2008@gmail.com",      
    "password":  "xxxx xxxx xxxx xxxx",     
    "penerima": [
        "ariobuyan01@gmail.com",              
        # "penerima2@perusahaan.com",       
    ],
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
}


JADWAL_CONFIG = {
    "hari":   1,     
    "jam":    8,     
    "menit":  0,
    "timezone": "Asia/Jakarta",
}


PERUSAHAAN = {
    "nama":    "Data Center Indonesia",  
    "alamat":  "Jl. Pantai Indah Kapuk 2 No. 1, Palembang, Sumatera Selatan",
    "telpon":  "0811-5564-7654",
}
