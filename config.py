"""
Konfigurasi Bot Discord TikTok Downloader
"""

import os

# Bot Configuration - EDIT LANGSUNG DISINI
BOT_TOKEN = "YOUR_TOKEN"

# Validasi token (update juga bagian ini)
if BOT_TOKEN == "MASUKKAN_TOKEN_BOT_DISCORD_KAMU_DISINI" or not BOT_TOKEN:
    print("❌ ERROR: Token belum di-set!")
    print("Edit file config.py dan ganti token dengan yang benar")

BOT_PREFIX = '!'
BOT_DESCRIPTION = 'Discord Bot untuk mendownload video TikTok'

# API Configuration
TIKTOK_API_URL = "https://www.tikwm.com/api/"
TIKTOK_API_PARAMS = {
    "hd": "1"
}

# Bot Settings
COOLDOWN_RATE = 1  # Command per user
COOLDOWN_PER = 5   # Seconds

# Embed Colors
EMBED_COLOR_PRIMARY = 0xFE2C55      # TikTok Red
EMBED_COLOR_SUCCESS = 0x00FF00        # Green
EMBED_COLOR_ERROR = 0xFF0000        # Red
EMBED_COLOR_INFO = 0x00BFFF         # Deep Sky Blue

# File Size Limits (Discord)
MAX_FILE_SIZE_MB = 25
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Regex Patterns
TIKTOK_URL_PATTERNS = [
    r'https?://(?:www\.)?tiktok\.com/@[\w.]+/video/\d+',
    r'https?://(?:www\.)?tiktok\.com/t/\w+',
    r'https?://vm\.tiktok\.com/\w+',
    r'https?://vt\.tiktok\.com/\w+',
    r'https?://(?:www\.)?tiktok\.com/v/\d+',
]
