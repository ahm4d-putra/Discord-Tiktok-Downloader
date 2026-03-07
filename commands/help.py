"""
Slash command help dengan dropdown menu
"""

import discord
from discord import app_commands
from discord.ext import commands
import config
from views.help_dropdown import HelpView

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Menampilkan menu bantuan bot")
    async def help(self, interaction: discord.Interaction):
        """
        Command help dengan dropdown menu interaktif
        """
        # Embed awal
        embed = discord.Embed(
            title="📚 TikTok Downloader Bot - Help Menu",
            description=(
                "Selamat datang! Bot ini membantu mendownload video TikTok tanpa watermark.\n\n"
                "**🚀 Fitur Utama:**\n"
                "• Download manual dengan `/tt`\n"
                "• Auto-detect link di channel tertentu\n"
                "• Video tanpa watermark (HD)\n"
                "• Embed dengan statistik lengkap\n\n"
                "**📂 Pilih kategori di dropdown di bawah untuk melihat commands:**"
            ),
            color=config.EMBED_COLOR_PRIMARY
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text=f"Server: {interaction.guild.name}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        # Buat view dengan dropdown
        view = HelpView(timeout=300)  # 5 menit timeout
        
        await interaction.response.send_message(embed=embed, view=view)
        
        # Simpan reference ke message untuk timeout handler
        view.message = await interaction.original_response()

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))