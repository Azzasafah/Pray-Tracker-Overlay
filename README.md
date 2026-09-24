# AuraSalat Desktop Overlay (ASDO) 🕌⚡

**AuraSalat Desktop Overlay (ASDO)** adalah aplikasi desktop widget jadwal salat bergaya **HUD (Heads-Up Display) / Hardware Monitor** ala *MSI Afterburner* yang transparan, modern, dan *always-on-top*. 

Dirancang khusus untuk gamer, programmer, dan profesional PC di Indonesia agar dapat memantau waktu salat dan hitung mundur azan berikutnya secara sekilas (*at-a-glance*) tanpa mengganggu aktivitas game maupun pekerjaan di layar.

---

## ✨ Fitur Utama

### 1. Tampilan Overlay Minimalis (HUD Style) & Mode Desktop
- **Mode Desktop Wallpaper (Tidak Menutupi Aplikasi)**: Widget dapat diatur menempel di wallpaper desktop (di bawah semua jendela kerja seperti VS Code, browser, atau game). Widget tidak akan menghalangi baris kode maupun jendela aktif!
- **Mode Ringkas (Mini Bar)**: Cukup tekan tombol `↕` atau shortcut **F8** untuk mengecilkan widget menjadi satu baris ramping horizontal (`NEXT: MAGHRIB 00:10:14 | 1/3 Malam: 00:33`).
- **Frameless & Transparent Window**: Tampilan kaca gelap transparan (*dark glassmorphism*) dengan aksen pastel atau neon.
- **Lapisan Fleksibel (Desktop / Always On Top)**: Bebas beralih antara menempel di desktop wallpaper atau mengapung di atas semua jendela dengan sekali klik pada ikon `🖥` / `📌`.
- **Click-Through Mode (Tembus Mouse)**: Mouse dapat menembus widget sehingga tidak sengaja terklik saat bermain game atau bekerja.
- **Customizable Position (Drag & Drop)**: Bebas geser ke posisi mana saja (misal pojok atas, samping taskbar, atau monitor sekunder).

### 2. Sinkronisasi Data Jadwal Salat Resmi Kemenag RI
- **Default Wilayah: Kab. Jombang, Jawa Timur**: Langsung aktif dengan jadwal akurat Kabupaten Jombang, Jawa Timur dan dapat diubah kapan saja ke 518 kota/kabupaten lain melalui menu Settings.
- **Integrasi MyQuran API (Kemenag RI)**: Mengambil data jadwal salat resmi dari Kementerian Agama Republik Indonesia.
- **Pencarian 518 Kota & Kabupaten**: Mendukung seluruh kota dan kabupaten di Indonesia dengan live-search instan.
- **Offline Caching & Auto-Update**: Data jadwal harian disimpan secara lokal (`cache_jadwal.json`). Widget tetap berjalan normal meskipun internet terputus, dan otomatis memperbarui jadwal setiap pergantian hari (tengah malam).

### 3. Indikator & Hitung Mundur Real-time (Countdown Timer)
- Menampilkan jadwal harian: **Subuh, Terbit, Dzuhur, Ashar, Maghrib, Isya** (serta opsi Imsak).
- **Perhitungan Otomatis 1/3 Malam Terakhir (Waktu Tahajjud)**: Menghitung secara presisi jam dimulainya sepertiga malam terakhir berdasarkan selisih waktu Maghrib dan Subuh (misal: 00:33 s/d 04:05 WIB). Kartu dan status bar akan otomatis menyala hijau ketika 1/3 malam sedang berlangsung!
- Kartu waktu salat aktif/mendatang disorot (*highlight*) secara dinamis.
- Hitung mundur real-time (`HH:MM:SS`) menuju azan berikutnya dengan indikator warna pintar (Kuning < 15 menit, Merah berkedip saat azan tiba).

### 4. Sistem Notifikasi Ringan
- **Notifikasi Visual**: Spanduk peringatan halus berkedip (*pulsing alert*) saat waktu salat telah tiba.
- **Gentle Sound Chime**: Nada dering santun 3 nada (menggunakan Windows native sound chime non-blocking, dapat di-mute).
- **Windows System Notification**: Balon notifikasi Windows saat waktu azan tiba.

### 5. Kustomisasi Tema Catppuccin & HUD
- **Tema Catppuccin (Pastel Modern)**:
  1. `Catppuccin Mocha` (Default - Soft Pastel Dark: Mauve, Lavender, Base)
  2. `Catppuccin Macchiato` (Warm Pastel Dark: Peach & Yellow)
  3. `Catppuccin Latte` (Light Pastel Clean)
- **Tema Cyber HUD / Hardware Monitor**:
  4. `Cyber Cyan` (Neon Cyan Blue)
  5. `MSI Amber` (Tactical Hardware Monitor Orange)
  6. `Emerald Matrix` (Islamic Cyber Mint Green)
  7. `Stealth Crimson` (Rogue Dark Crimson)
- **Opacity Slider**: Sesuaikan transparansi widget dari 40% hingga 100%.

---

## 🚀 Panduan Menjalankan (Quick Start)

### Prasyarat
- Windows 10 / 11
- Python 3.10+ (atau gunakan file `.exe` mandiri)

### 1. Instalasi Dependensi
Jalankan perintah berikut di terminal:
```bash
pip install -r requirements.txt
```

### 2. Menjalankan Aplikasi
```bash
python main.py
```

Overlay akan langsung muncul di layar monitor Anda dan ikon aplikasi akan aktif di **Windows System Tray** (pojok kanan bawah taskbar).

---

## 🎮 Kontrol & Navigasi

| Aksi | Cara Melakukan |
|---|---|
| **Pindah Posisi Overlay** | Klik kiri dan tahan pada area overlay, lalu geser (*drag & drop*). Posisi otomatis disimpan. |
| **Ganti Mode Lapisan (Desktop vs Top)** | Klik tombol **🖥 / 📌** pada header overlay untuk beralih antara menempel di desktop wallpaper (tidak menutupi jendela kerja) atau Always On Top. |
| **Beralih Mode Ringkas (Mini Bar)** | Klik tombol **↕** pada header overlay atau tekan tombol **F8** pada keyboard untuk mengecilkan widget menjadi satu baris ramping. |
| **Buka Pengaturan (Settings)** | Klik tombol **⚙** pada header overlay, atau tekan **F10**, atau klik kanan > *Pengaturan*, atau via menu System Tray. |
| **Kunci Mode Tembus (Click-Through)** | Klik tombol **🔒** pada header overlay, atau tekan **F9**, atau aktifkan centang *Click-Through Mode* di menu Tray. |
| **Buka Kunci Tembus (Unlock Click-Through)** | Tekan **F9**, atau klik ikon ASDO di **System Tray** > hilangkan centang *Click-Through Mode*. |
| **Sembunyikan ke Tray** | Klik tombol **🗕** pada header overlay, atau klik ganda (*double-click*) ikon di System Tray. |
| **Menu Konteks Cepat** | Klik kanan pada widget untuk mengakses menu cepat (*Refresh*, *Pilihan Lapisan*, *Mode Ringkas*, *Mute*, *Reset Posisi*). |

---

## 📦 Download & Instalasi (Windows Installer)

Tersedia file installer resmi yang memudahkan pemasangan di Windows layaknya software profesional:

### 1. Download Setup Installer (.exe)
File installer mandiri tersedia di:
- **Installer Setup**: [`dist/AuraSalatOverlay-Setup-v1.0.0.exe`](file:///e:/Development/Portfolio/Pray%20Tracker/dist/AuraSalatOverlay-Setup-v1.0.0.exe) *(~43 MB)*
- **Portable Standalone Exe**: [`dist/AuraSalatOverlay.exe`](file:///e:/Development/Portfolio/Pray%20Tracker/dist/AuraSalatOverlay.exe) *(~42 MB)*

### Fitur Installer:
- Wizard instalasi modern & bersih.
- Pembuatan pintasan (*shortcut*) otomatis di **Desktop** dan **Start Menu**.
- Opsi **Jalankan Otomatis saat Windows Startup** (*Run at Startup*).
- Dilengkapi sistem *Uninstaller* resmi (dapat di-uninstall kapan saja melalui *Windows Settings > Installed Apps*).

---

## 🔨 Membangun Installer Sendiri (Build Script)

Untuk mengompilasi ulang file `.exe` dan installer Setup secara otomatis:

```bash
python build_installer.py
```

Skrip ini akan otomatis:
1. Mengompilasi kode Python menjadi file standalone `dist/AuraSalatOverlay.exe`.
2. Menjalankan *Inno Setup Compiler* untuk menghasilkan file `dist/AuraSalatOverlay-Setup-v1.0.0.exe`.

---

## 🌐 Panduan Upload ke GitHub

### Langkah 1: Inisialisasi Git & Commit
Jalankan di terminal direktori project:
```bash
git init
git add .
git commit -m "feat: release AuraSalat Desktop Overlay v1.0.0 with installer and Catppuccin theme"
```

### Langkah 2: Hubungkan ke Repository GitHub
1. Buat repository baru di [github.com/new](https://github.com/new) (misal: `AuraSalat-Overlay`).
2. Jalankan perintah berikut (ganti `USERNAME` dengan username GitHub Anda):
```bash
git branch -M main
git remote add origin https://github.com/USERNAME/AuraSalat-Overlay.git
git push -u origin main
```

### Langkah 3: Membuat Rilis (Release) di GitHub
Ada 2 cara mudah:

#### Cara A: Otomatis via Git Tag & GitHub Actions (Direkomendasikan)
Repository ini telah dilengkapi alur kerja otomatis [`.github/workflows/build-release.yml`](file:///.github/workflows/build-release.yml). Cukup buat tag rilis:
```bash
git tag v1.0.0
git push origin v1.0.0
```
*GitHub Actions akan otomatis mengompilasi installer Windows dan mengunggahnya ke halaman Releases di repository Anda!*

#### Cara B: Manual via Web Browser
1. Buka halaman repository Anda di GitHub.
2. Klik menu **Releases** di sisi kanan > **Draft a new release**.
3. Masukkan tag: `v1.0.0`.
4. Unggah file installer yang sudah jadi:
   - `dist/AuraSalatOverlay-Setup-v1.0.0.exe`
   - `dist/AuraSalatOverlay.exe`
5. Klik **Publish release**.

---

## ⚙ Struktur Konfigurasi (`config.json`)

Pengaturan disimpan secara otomatis dalam format JSON:

```json
{
    "city_id": "1608",
    "city_name": "KAB. JOMBANG",
    "window_x": 100,
    "window_y": 100,
    "always_on_top": false,
    "window_layer": "desktop",
    "click_through": false,
    "sound_enabled": true,
    "theme": "catppuccin_mocha",
    "opacity": 0.94,
    "compact_mode": false,
    "show_imsak": false,
    "show_third_night": true
}
```

---

## 🛠 Teknologi (Tech Stack)

- **Language**: Python 3.x
- **GUI Framework**: PyQt6
- **Theme**: Catppuccin Mocha / Macchiato / Latte & Cyberpunk HUD
- **API Wrapper**: Requests (Integrasi MyQuran / Kemenag RI v2)
- **Windows Integration**: ctypes User32 API (Click-Through `WS_EX_TRANSPARENT`), Winsound
- **Packaging & Installer**: PyInstaller & Inno Setup 6
- **CI/CD**: GitHub Actions Automated Build & Release

---

*AuraSalat Desktop Overlay (ASDO) - Keep Connected to Your Faith While Staying Focused.*

*AuraSalat Desktop Overlay (ASDO) - Keep Connected to Your Faith While Staying Focused.*
