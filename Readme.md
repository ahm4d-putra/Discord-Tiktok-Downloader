
# 🤖 Discord TikTok Downloader Bot

Bot Discord serbaguna untuk mengunduh video TikTok tanpa watermark dilengkapi dengan fitur moderasi server yang lengkap.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Discord.py](https://img.shields.io/badge/Discord.py-2.0%2B-blue?logo=discord)

---

## ✨ Fitur Utama

### 📥 TikTok Downloader
- **Manual Download**: `/tt <url>` - Mengunduh video spesifik.
- **Auto Download**: `/setttchannel` - Mengatur channel agar otomatis mendownload setiap ada link TikTok.
- **Watermark Free**: Video diunduh tanpa watermark.
- **Video Info**: Menampilkan informasi lengkap (Like, Share, Deskripsi).

### 🛡️ Moderasi Server
Perintah untuk menjaga ketertiban server:

| Perintah | Fungsi |
| :--- | :--- |
| `/kick` | Mengeluarkan user dari server. |
| `/ban` & `/unban` | Memblokir atau membuka akses user. |
| `/timeout` | Mute user sementara (contoh: `1h`, `30m`, `1d`). |
| `/warn` | Memberi peringatan kepada user. |
| `/warnings` | Melihat daftar peringatan user. |
| `/clearwarn` | Menghapus peringatan user. |
| `/clear` | Menghapus sejumlah pesan (Bulk Delete). |
| `/slowmode` | Mengatur slowmode channel. |
| `/lock` & `/unlock` | Mengunci atau membuka akses channel. |

### ⚙️ Utilitas Lainnya
- `/help` - Menu bantuan interaktif.
- `/ping` - Cek latency bot.

---

## 🛠️ Cara Install

Ikuti langkah-langkah berikut untuk menjalankan bot di lokal atau server kamu.

### 1. Prasyarat
Pastikan kamu sudah menginstall:
- Python 3.8 atau lebih baru.
- Git (opsional, untuk clone).

### 2. Clone Repository
```bash
git clone https://github.com/username/discord-tiktok-bot.git
cd discord-tiktok-bot
```

### 3. Install Dependencies
Install semua library yang dibutuhkan via pip.
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Token
Buat file `.env` di root folder atau edit `config.py`.

**Menggunakan `.env` (Rekomendasi):**
```env
DISCORD_TOKEN=token_bot_kamu_disini
```

**Atau langsung di `config.py`:**
```python
BOT_TOKEN = "token_bot_kamu_disini"
```

### 5. Jalankan Bot
```bash
python bot.py
```

---

## 📂 Struktur Folder

Agar mudah dikelola, struktur project dibagi sebagai berikut:

```
discord-tiktok-bot/
├── bot.py              # Entry point utama bot
├── config.py           # Konfigurasi token & variabel
├── requirements.txt    # Daftar library Python
├── database.json       # Penyimpanan data (Auto generate)
│
├── commands/           # Folder Slash Commands
│   ├── downloader.py   # Logika download TikTok
│   ├── moderation.py   # Logika moderasi (kick/ban/warn)
│   ├── setup.py        # Setup auto-channel
│   └── help.py         # Tampilan menu help
│
├── utils/              # Helper Functions
│   ├── database.py     # Handler baca/tulis JSON
│   └── tiktok.py       # Scraper/API TikTok
│
└── views/              # UI Components (Buttons/Dropdown)
    ├── help_dropdown.py
    └── video_buttons.py
```

---

## 🔑 Permission Bot

Saat menginvite bot ke server, gunakan scope:
- `bot`
- `applications.commands`

**Permissions yang dibutuhkan:**
- Send Messages
- Attach Files
- Embed Links
- Manage Messages (untuk `/clear`)
- Kick Members
- Ban Members
- Moderate Members (untuk Timeout)
- Manage Channels (untuk Lock/Unlock)

> Link Invite Generator: `https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands`

---

## 📝 Catatan Penting

- **Limit File:** Maksimal ukuran file video adalah **25MB** (batasan Discord).
- **Cooldown:** Terdapat delay 5 detik per command untuk mencegah spam.
- **Database:** Menggunakan file JSON lokal (`database.json`).
- **Keamanan:** Jangan lupa masukkan `.env` dan `database.json` ke dalam `.gitignore` agar data tidak ter-upload ke GitHub.

---

## ❓ Troubleshooting

**Slash command tidak muncul?**
1. Pastikan bot di-invite dengan scope `applications.commands`.
2. Coba restart Discord client (Ctrl+R).
3. Tunggu beberapa menit (1-5 menit) karena command butuh waktu sinkronisasi.

**Error "ModuleNotFound"?**
Jalankan command berikut untuk install manual:
```bash
pip install discord.py requests python-dotenv aiohttp
```

**Token Invalid?**
- Reset token kamu di **Discord Developer Portal**.
- Update token di file `.env` atau `config.py`.

---

## 🙏 Credits

- [discord.py](https://github.com/Rapptz/discord.py)
- API Provider: [tikwm.com](https://tikwm.com/)
```
