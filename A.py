import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Menyiapkan Data
# Anda bisa mengganti angka-angka di bawah ini sesuai data saham yang Anda inginkan
data = {
    'Ticker': ['ASII', 'BBRI', 'BBCA', 'TLKM', 'UNVR'],
    'EPS': [809.4, 401.0, 450.0, 240.0, 120.0],
    'PER': [8.25, 10.05, 22.5, 11.5, 25.0],
    'PBV': [0.93, 1.87, 4.80, 2.50, 20.0],
    'ROA (%)': [6.46, 3.02, 3.50, 10.5, 30.0],
    'ROE (%)': [11.27, 18.61, 23.0, 18.5, 80.0],
    'DER': [0.74, 5.17, 0.20, 0.45, 2.50],
    'RPS': [7985, 1328, 1000, 1500, 1000],
    'Earning Yield (%)': [12.12, 9.95, 4.44, 8.70, 4.00]
}

df = pd.DataFrame(data)

# 2. Pengaturan Tampilan Dashboard
# Membuat grid 4 baris x 2 kolom untuk menampung 8 chart
metrics = ['EPS', 'PER', 'PBV', 'ROA (%)', 'ROE (%)', 'DER', 'RPS', 'Earning Yield (%)']
fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(15, 22))
axes = axes.flatten()

# Mengatur tema warna
sns.set_theme(style="whitegrid")
palette = "viridis"

# 3. Looping untuk membuat setiap chart secara otomatis
for i, metric in enumerate(metrics):
    # Mengurutkan data berdasarkan metrik yang sedang diproses agar chart lebih rapi
    df_sorted = df.sort_values(by=metric, ascending=False)
    
    sns.barplot(x='Ticker', y=metric, data=df_sorted, ax=axes[i], palette=palette)
    
    # Menambahkan Judul dan Label
    axes[i].set_title(f'Perbandingan {metric}', fontsize=14, fontweight='bold', pad=15)
    axes[i].set_ylabel(metric)
    axes[i].set_xlabel('Kode Saham')
    
    # Menambahkan label angka di atas setiap batang (bar)
    for p in axes[i].patches:
        axes[i].annotate(format(p.get_height(), '.2f'), 
                         (p.get_x() + p.get_width() / 2., p.get_height()), 
                         ha = 'center', va = 'center', 
                         xytext = (0, 9), 
                         textcoords = 'offset points',
                         fontsize=10, fontweight='bold')

# 4. Finalisasi dan Menyimpan Hasil
plt.tight_layout()
plt.subplots_adjust(hspace=0.4) # Memberi jarak antar baris chart

# Simpan sebagai gambar
plt.savefig('dashboard_saham.png', dpi=300)

# Ekspor data ke CSV
df.to_csv('data_saham.csv', index=False)

print("Dashboard berhasil dibuat! File: 'dashboard_saham.png' dan 'data_saham.csv'")
plt.show()

