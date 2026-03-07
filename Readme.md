```markdown
# Discord TikTok Downloader Bot

Bot Discord buat download video TikTok tanpa watermark, plus fitur moderasi server.

---

## Fitur

**TikTok Downloader**
- `/tt <url>` - Download manual
- `/setttchannel` - Auto download di channel tertentu
- Auto detect link TikTok
- Video tanpa watermark + info lengkap

**Moderation**
- `/kick`, `/ban`, `/unban` - Kick/ban user
- `/timeout <user> <duration>` - Mute sementara (1h, 30m, 1d)
- `/warn`, `/warnings`, `/clearwarn` - Sistem warn
- `/clear <amount>` - Hapus pesan
- `/slowmode`, `/lock`, `/unlock` - Manage channel

**Lainnya**
- `/help` - Menu bantuan
- `/ping` - Cek latency

---

## Cara Install

**1. Clone repo**
```bash
git clone https://github.com/username/discord-tiktok-bot.git
cd discord-tiktok-bot
```

**2. Install dependency**
```bash
pip install -r requirements.txt
```

**3. Setup token**

Edit `config.py`:
```python
BOT_TOKEN = "token_bot_kamu_disini"
```

Atau pakai `.env`:
```env
DISCORD_TOKEN=token_bot_kamu_disini
```

**4. Jalankan**
```bash
python bot.py
```

---

## Struktur Folder

```
discord-tiktok-bot/
├── bot.py              # Main file
├── config.py           # Konfigurasi
├── requirements.txt    # Dependency
├── database.json       # Data server
│
├── commands/           # Slash commands
│   ├── downloader.py   # TikTok download
│   ├── moderation.py   # Moderation
│   ├── setup.py        # Setup channel
│   └── help.py         # Help menu
│
├── utils/              # Helper
│   ├── database.py     # Database handler
│   └── tiktok.py       # TikTok API
│
└── views/              # UI components
    ├── help_dropdown.py
    └── video_buttons.py
```

---

## Permission Bot

Invite bot dengan scope:
- `bot`
- `applications.commands`

Permission yang perlu:
- Send Messages
- Attach Files
- Embed Links
- Manage Messages
- Kick/Ban Members
- Moderate Members
- Manage Channels

---

## Catatan

- Max file size: 25MB (limit Discord)
- Cooldown: 5 detik per command
- Database pakai JSON (simple, per server)
- Jangan lupa `.env` dan `database.json` di `.gitignore`

---

## Troubleshoot

**Slash command gak muncul?**
- Re-invite bot dengan `applications.commands`
- Restart Discord client (Ctrl+R)
- Tunggu 1-5 menit setelah invite

**Bot error "ModuleNotFound"?**
```bash
pip install discord.py requests python-dotenv aiohttp
```

**Token invalid?**
- Reset token di Discord Developer Portal
- Update di `config.py`

---

## Credits

- discord.py
- tikwm.com API

---
