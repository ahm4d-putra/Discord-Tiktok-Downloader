"""
Utility untuk download video TikTok menggunakan API tikwm.com
"""

import re
import requests
import aiohttp
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
import config

@dataclass
class TikTokVideo:
    """Data class untuk informasi video TikTok"""
    title: str
    author: str
    author_avatar: str
    duration: int
    play_count: int
    like_count: int
    comment_count: int
    share_count: int
    video_url: str
    music_title: str
    music_author: str
    cover_url: str
    wm_video_url: Optional[str] = None
    
    def format_stats(self) -> str:
        """Format statistik video"""
        def format_number(num: int) -> str:
            if num >= 1_000_000:
                return f"{num / 1_000_000:.1f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.1f}K"
            return str(num)
        
        return (
            f"👁️ {format_number(self.play_count)} | "
            f"❤️ {format_number(self.like_count)} | "
            f"💬 {format_number(self.comment_count)} | "
            f"🔄 {format_number(self.share_count)}"
        )

class TikTokDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        })
    
    def extract_tiktok_url(self, text: str) -> Optional[str]:
        """Extract URL TikTok dari text menggunakan regex"""
        for pattern in config.TIKTOK_URL_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def is_tiktok_url(self, text: str) -> bool:
        """Cek apakah text mengandung URL TikTok"""
        return self.extract_tiktok_url(text) is not None
    
    async def download_info(self, url: str) -> Optional[TikTokVideo]:
        """
        Download informasi video TikTok dari API
        
        Args:
            url: URL TikTok video
            
        Returns:
            TikTokVideo object atau None jika gagal
        """
        api_url = config.TIKTOK_API_URL
        params = {
            "url": url,
            **config.TIKTOK_API_PARAMS
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=30) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    
                    if data.get("code") != 0 or not data.get("data"):
                        return None
                    
                    video_data = data["data"]
                    
                    return TikTokVideo(
                        title=video_data.get("title", "No Title"),
                        author=video_data.get("author", {}).get("nickname", "Unknown"),
                        author_avatar=video_data.get("author", {}).get("avatar", ""),
                        duration=video_data.get("duration", 0),
                        play_count=video_data.get("play_count", 0),
                        like_count=video_data.get("digg_count", 0),
                        comment_count=video_data.get("comment_count", 0),
                        share_count=video_data.get("share_count", 0),
                        video_url=video_data.get("play", ""),
                        music_title=video_data.get("music_info", {}).get("title", "Unknown"),
                        music_author=video_data.get("music_info", {}).get("author", "Unknown"),
                        cover_url=video_data.get("cover", ""),
                        wm_video_url=video_data.get("wmplay", "")
                    )
                    
        except Exception as e:
            print(f"Error downloading TikTok: {e}")
            return None
    
    async def download_video_bytes(self, video_url: str) -> Optional[bytes]:
        """
        Download video bytes dari URL
        
        Args:
            video_url: URL video
            
        Returns:
            Video bytes atau None jika gagal
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, timeout=60) as response:
                    if response.status == 200:
                        return await response.read()
                    return None
        except Exception as e:
            print(f"Error downloading video bytes: {e}")
            return None

# Singleton instance
tiktok_downloader = TikTokDownloader()