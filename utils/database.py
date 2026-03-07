"""
Database handler untuk menyimpan setting per server
"""

import json
import os
from typing import Optional, Dict
import asyncio
from pathlib import Path

class Database:
    def __init__(self, filepath: str = "database.json"):
        self.filepath = Path(filepath)
        self.data: Dict[str, dict] = {}
        self.lock = asyncio.Lock()
        self._load()
    
    def _load(self) -> None:
        """Load data dari file JSON"""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = {}
        else:
            self.data = {}
            self._save()
    
    def _save(self) -> None:
        """Simpan data ke file JSON"""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
    
    async def get_guild_settings(self, guild_id: int) -> Optional[dict]:
        """Ambil setting untuk guild tertentu"""
        async with self.lock:
            guild_id_str = str(guild_id)
            return self.data.get(guild_id_str)
    
    async def get_auto_channel(self, guild_id: int) -> Optional[int]:
        """Ambil channel ID auto downloader untuk guild"""
        async with self.lock:
            guild_id_str = str(guild_id)
            guild_data = self.data.get(guild_id_str)
            if guild_data:
                return guild_data.get("channel_id")
            return None
    
    async def set_auto_channel(self, guild_id: int, channel_id: int) -> None:
        """Set channel auto downloader untuk guild"""
        async with self.lock:
            guild_id_str = str(guild_id)
            if guild_id_str not in self.data:
                self.data[guild_id_str] = {}
            
            self.data[guild_id_str]["channel_id"] = channel_id
            self._save()
    
    async def remove_auto_channel(self, guild_id: int) -> bool:
        """Hapus channel auto downloader untuk guild"""
        async with self.lock:
            guild_id_str = str(guild_id)
            if guild_id_str in self.data and "channel_id" in self.data[guild_id_str]:
                del self.data[guild_id_str]["channel_id"]
                
                # Hapus entry jika kosong
                if not self.data[guild_id_str]:
                    del self.data[guild_id_str]
                
                self._save()
                return True
            return False
    
    async def guild_exists(self, guild_id: int) -> bool:
        """Cek apakah guild sudah ada di database"""
        async with self.lock:
            return str(guild_id) in self.data

# Singleton instance
db = Database()