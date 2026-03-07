"""
Button interactions untuk video TikTok
"""

import discord
from discord.ui import View, Button
import config
from utils.tiktok import tiktok_downloader
import io

class VideoButtonView(View):
    def __init__(self, video_url: str, original_url: str, author_name: str, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.video_url = video_url
        self.original_url = original_url
        self.author_name = author_name
        self.download_count = 0
        
        # Add buttons
        self.add_item(DownloadAgainButton(video_url, author_name))
        self.add_item(OriginalLinkButton(original_url))
        self.add_item(DeleteButton())
    
    async def on_timeout(self):
        """Disable all buttons when timeout"""
        for item in self.children:
            item.disabled = True
        
        try:
            if hasattr(self, 'message'):
                await self.message.edit(view=self)
        except:
            pass

class DownloadAgainButton(Button):
    def __init__(self, video_url: str, author_name: str):
        super().__init__(
            label="🔄 Download Lagi",
            style=discord.ButtonStyle.primary,
            custom_id="download_again"
        )
        self.video_url = video_url
        self.author_name = author_name
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Re-download video
        video_bytes = await tiktok_downloader.download_video_bytes(self.video_url)
        
        if not video_bytes:
            await interaction.followup.send(
                "❌ Gagal mendownload ulang.", 
                ephemeral=True
            )
            return
        
        # Check file size
        if len(video_bytes) > config.MAX_FILE_SIZE_BYTES:
            await interaction.followup.send(
                f"⚠️ File terlalu besar. [Download manual]({self.video_url})", 
                ephemeral=True
            )
            return
        
        # Send file
        file = discord.File(
            fp=io.BytesIO(video_bytes),
            filename=f"tiktok_redownload_{self.author_name}_{interaction.id}.mp4"
        )
        
        await interaction.followup.send(
            content=f"🔄 **Re-download oleh** {interaction.user.mention}",
            file=file,
            ephemeral=False
        )

class OriginalLinkButton(Button):
    def __init__(self, original_url: str):
        super().__init__(
            label="🔗 Link Original",
            style=discord.ButtonStyle.link,
            url=original_url
        )

class DeleteButton(Button):
    def __init__(self):
        super().__init__(
            label="🗑️ Hapus",
            style=discord.ButtonStyle.danger,
            custom_id="delete_video"
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Cek apakah user yang klik adalah yang request atau admin
        message = interaction.message
        
        # Ambil embed untuk cek footer
        if message.embeds:
            embed = message.embeds[0]
            footer_text = embed.footer.text if embed.footer else ""
            
            # Cek apakah user ini yang request
            is_requester = f"Requested by {interaction.user.name}" in footer_text
            is_admin = interaction.user.guild_permissions.manage_messages if interaction.guild else False
            
            if is_requester or is_admin:
                await message.delete()
                await interaction.response.send_message(
                    "✅ Video dihapus.", 
                    ephemeral=True,
                    delete_after=3
                )
            else:
                await interaction.response.send_message(
                    "❌ Kamu tidak bisa menghapus video orang lain!", 
                    ephemeral=True
                )
        else:
            await message.delete()
            await interaction.response.send_message(
                "✅ Video dihapus.", 
                ephemeral=True,
                delete_after=3
            )

class StatsButtonView(View):
    """Button untuk /ttstats command"""
    def __init__(self, url: str, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.add_item(OriginalLinkButton(url))
        self.add_item(DownloadButton(url))
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        
        try:
            if hasattr(self, 'message'):
                await self.message.edit(view=self)
        except:
            pass

class DownloadButton(Button):
    def __init__(self, url: str):
        super().__init__(
            label="📥 Download Sekarang",
            style=discord.ButtonStyle.success,
            custom_id="download_from_stats"
        )
        self.url = url
    
    async def callback(self, interaction: discord.Interaction):
        
        await interaction.response.send_message(
            f"📥 Gunakan command `/tt url:{self.url}` untuk download!",
            ephemeral=True
        )