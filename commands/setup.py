"""
Slash commands untuk setup bot (Admin only)
"""

import discord
from discord import app_commands
from discord.ext import commands
import config
from utils.database import db

class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="setttchannel", description="Set channel ini sebagai auto TikTok downloader")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True, send_messages=True, attach_files=True)
    async def setttchannel(self, interaction: discord.Interaction):
        """
        Set channel saat ini sebagai auto downloader channel
        """
        await interaction.response.defer(ephemeral=True)
        
        # Simpan ke database
        await db.set_auto_channel(interaction.guild_id, interaction.channel_id)
        
        embed = discord.Embed(
            title="✅ Auto Downloader Aktif",
            description=f"Channel {interaction.channel.mention} telah di-set sebagai "
                       f"channel auto TikTok downloader.\n\n"
                       f"**Cara penggunaan:**\n"
                       f"1. Kirim link TikTok di channel ini\n"
                       f"2. Bot akan otomatis mendownload video\n"
                       f"3. Video dikirim tanpa watermark",
            color=config.EMBED_COLOR_SUCCESS
        )
        embed.add_field(
            name="⚙️ Untuk menonaktifkan",
            value="Gunakan command `/unsetttchannel`",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Kirim notifikasi publik
        public_embed = discord.Embed(
            title="🎵 TikTok Auto Downloader Aktif",
            description="Channel ini sekarang dapat mendeteksi dan mendownload "
                       "video TikTok secara otomatis!",
            color=config.EMBED_COLOR_PRIMARY
        )
        public_embed.add_field(
            name="Cara pakai",
            value="Kirim link TikTok apa saja di channel ini",
            inline=False
        )
        await interaction.channel.send(embed=public_embed)
    
    @app_commands.command(name="unsetttchannel", description="Nonaktifkan auto TikTok downloader di server ini")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unsetttchannel(self, interaction: discord.Interaction):
        """
        Hapus auto downloader channel
        """
        await interaction.response.defer(ephemeral=True)
        
        # Cek apakah ada setting
        current_channel = await db.get_auto_channel(interaction.guild_id)
        
        if not current_channel:
            embed = discord.Embed(
                title="ℹ️ Tidak Ada Setting",
                description="Belum ada channel auto downloader yang di-set di server ini.",
                color=config.EMBED_COLOR_INFO
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Hapus dari database
        success = await db.remove_auto_channel(interaction.guild_id)
        
        if success:
            embed = discord.Embed(
                title="✅ Auto Downloader Dinonaktifkan",
                description=f"Channel <#{current_channel}> sudah tidak lagi "
                           f"channel auto TikTok downloader.",
                color=config.EMBED_COLOR_SUCCESS
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Gagal",
                description="Terjadi kesalahan saat menghapus setting.",
                color=config.EMBED_COLOR_ERROR
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @setttchannel.error
    @unsetttchannel.error
    async def setup_error(self, interaction: discord.Interaction, error):
        """Error handler untuk setup commands"""
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permission Ditolak",
                description="Kamu memerlukan permission `Manage Channels` untuk menggunakan command ini.",
                color=config.EMBED_COLOR_ERROR
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        
        elif isinstance(error, app_commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Permission Kurang",
                description="Bot memerlukan permission `Manage Channels`, `Send Messages`, dan `Attach Files`.",
                color=config.EMBED_COLOR_ERROR
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        
        else:
            print(f"Setup error: {error}")

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))