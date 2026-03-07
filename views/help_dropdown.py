"""
Discord UI Components untuk Help Command
"""

import discord
from discord.ui import View, Select
import config

class HelpCategorySelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="📥 Downloader Commands",
                description="Commands untuk mendownload video TikTok",
                value="downloader",
                emoji="📥"
            ),
            discord.SelectOption(
                label="⚙️ Setup Commands",
                description="Commands untuk konfigurasi bot",
                value="setup",
                emoji="⚙️"
            ),
            discord.SelectOption(
                label="ℹ️ Information Commands",
                description="Commands informasi dan bantuan",
                value="info",
                emoji="ℹ️"
            ),
            discord.SelectOption(
                label="📋 All Commands",
                description="Tampilkan semua commands",
                value="all",
                emoji="📋"
            )
        ]
        
        super().__init__(
            placeholder="Pilih kategori help...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="help_category_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = self.get_embed_for_category(category)
        
        # Edit message dengan embed baru
        await interaction.response.edit_message(embed=embed, view=self.view)
    
    def get_embed_for_category(self, category: str) -> discord.Embed:
        """Generate embed berdasarkan kategori yang dipilih"""
        
        if category == "downloader":
            embed = discord.Embed(
                title="📥 Downloader Commands",
                description="Commands untuk mendownload video TikTok",
                color=config.EMBED_COLOR_PRIMARY
            )
            embed.add_field(
                name="`/tt <url>`",
                value="Download video TikTok secara manual\n"
                      "**Contoh:** `/tt https://tiktok.com/@user/video/123`\n"
                      "**Cooldown:** 5 detik per user",
                inline=False
            )
            embed.add_field(
                name="Auto Download",
                value="Kirim link TikTok di channel yang sudah di-set untuk download otomatis",
                inline=False
            )
            
        elif category == "setup":
            embed = discord.Embed(
                title="⚙️ Setup Commands",
                description="Commands untuk konfigurasi bot (Admin only)",
                color=config.EMBED_COLOR_INFO
            )
            embed.add_field(
                name="`/setttchannel`",
                value="Set channel saat ini sebagai auto TikTok downloader\n"
                      "**Permission:** Manage Channels",
                inline=False
            )
            embed.add_field(
                name="`/unsetttchannel`",
                value="Nonaktifkan auto downloader di server ini\n"
                      "**Permission:** Manage Channels",
                inline=False
            )
            
        elif category == "info":
            embed = discord.Embed(
                title="ℹ️ Information Commands",
                description="Commands informasi tentang bot",
                color=config.EMBED_COLOR_SUCCESS
            )
            embed.add_field(
                name="`/help`",
                value="Menampilkan menu bantuan ini dengan dropdown",
                inline=False
            )
            embed.add_field(
                name="📌 Tips Penggunaan",
                value="• Bot akan otomatis mendeteksi link TikTok\n"
                      "• Video diambil tanpa watermark\n"
                      "• Maksimal ukuran file: 25MB\n"
                      "• Gunakan `/tt` untuk download manual",
                inline=False
            )
            
        else:  # all
            embed = discord.Embed(
                title="📋 Semua Commands",
                description="Daftar lengkap semua commands",
                color=config.EMBED_COLOR_PRIMARY
            )
            embed.add_field(
                name="📥 Downloader",
                value="`/tt <url>` - Download manual\n"
                      "Auto-detect - Kirim link di channel set",
                inline=False
            )
            embed.add_field(
                name="⚙️ Setup (Admin)",
                value="`/setttchannel` - Set auto channel\n"
                      "`/unsetttchannel` - Hapus auto channel",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Info",
                value="`/help` - Menu bantuan",
                inline=False
            )
        
        embed.set_footer(text="Gunakan dropdown di bawah untuk navigasi")
        return embed

class HelpView(View):
    def __init__(self, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.add_item(HelpCategorySelect())
    
    async def on_timeout(self):
        """Disable view saat timeout"""
        for item in self.children:
            item.disabled = True
        
        # Try to edit message jika masih ada
        try:
            if hasattr(self, 'message'):
                await self.message.edit(view=self)
        except:
            pass