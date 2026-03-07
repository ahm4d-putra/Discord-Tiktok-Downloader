"""
Slash commands untuk download TikTok dengan BUTTONS
"""

import discord
from discord import app_commands
from discord.ext import commands
import config
from utils.tiktok import tiktok_downloader
from utils.database import db
from views.video_buttons import VideoButtonView
import io

class DownloaderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="tt", description="Download video TikTok tanpa watermark")
    @app_commands.describe(url="URL video TikTok yang ingin didownload")
    @app_commands.checks.cooldown(config.COOLDOWN_RATE, config.COOLDOWN_PER)
    async def tt(self, interaction: discord.Interaction, url: str):
        """
        Command untuk download video TikTok manual dengan BUTTONS
        """
        await interaction.response.defer(thinking=True)
        
        # Validasi URL
        if not tiktok_downloader.is_tiktok_url(url):
            embed = discord.Embed(
                title="❌ URL Tidak Valid",
                description="URL yang dimasukkan bukan URL TikTok yang valid.\n"
                           "Contoh URL yang valid:\n"
                           "• `https://tiktok.com/@user/video/123`\n"
                           "• `https://vm.tiktok.com/abc123`",
                color=config.EMBED_COLOR_ERROR
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Cek permission bot
        if not interaction.channel.permissions_for(interaction.guild.me).attach_files:
            embed = discord.Embed(
                title="❌ Permission Kurang",
                description="Bot tidak memiliki permission `Attach Files` di channel ini.",
                color=config.EMBED_COLOR_ERROR
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Download info
        video = await tiktok_downloader.download_info(url)
        
        if not video:
            embed = discord.Embed(
                title="❌ Gagal Mengambil Video",
                description="Tidak dapat mengambil informasi video. Pastikan:\n"
                           "• Video tidak private\n"
                           "• Video tidak dihapus\n"
                           "• URL benar dan valid",
                color=config.EMBED_COLOR_ERROR
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Download video bytes
        video_bytes = await tiktok_downloader.download_video_bytes(video.video_url)
        
        if not video_bytes:
            embed = discord.Embed(
                title="❌ Gagal Download",
                description="Gagal mendownload file video dari server.",
                color=config.EMBED_COLOR_ERROR
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Cek ukuran file
        if len(video_bytes) > config.MAX_FILE_SIZE_BYTES:
            embed = discord.Embed(
                title="⚠️ File Terlalu Besar",
                description=f"Ukuran video ({len(video_bytes)/1024/1024:.1f}MB) melebihi "
                           f"batas Discord ({config.MAX_FILE_SIZE_MB}MB).\n\n"
                           f"[Klik di sini untuk download manual]({video.video_url})",
                color=config.EMBED_COLOR_ERROR
            )
            embed.set_image(url=video.cover_url)
            
            # Tetap kasih button meskipun file besar
            view = VideoButtonView(
                video_url=video.video_url,
                original_url=url,
                author_name=video.author
            )
            return await interaction.followup.send(embed=embed, view=view)
        
        # Buat embed info KEREN
        embed = discord.Embed(
            title=f"🎵 {video.title[:100]}..." if len(video.title) > 100 else f"🎵 {video.title}",
            url=url,
            color=config.EMBED_COLOR_PRIMARY,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(
            name=f"@{video.author}",
            icon_url=video.author_avatar if video.author_avatar else None,
            url=f"https://tiktok.com/@{video.author}"
        )
        
        # Stats dengan progress bar visual
        stats_text = self._create_stats_bar(video.play_count, video.like_count, video.comment_count, video.share_count)
        embed.add_field(name="📊 Statistik", value=stats_text, inline=False)
        
        embed.add_field(
            name="🎶 Musik", 
            value=f"**{video.music_title}** - *{video.music_author}*", 
            inline=False
        )
        embed.add_field(name="⏱️ Durasi", value=f"`{video.duration} detik`", inline=True)
        embed.add_field(name="📁 Ukuran", value=f"`{len(video_bytes)/1024/1024:.1f} MB`", inline=True)
        
        embed.set_thumbnail(url=video.cover_url)
        embed.set_image(url=video.cover_url)  # Preview besar
        embed.set_footer(
            text=f"Requested by {interaction.user.name} • Klik tombol di bawah untuk aksi lain",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )
        
        # Kirim file dengan BUTTONS
        file = discord.File(
            fp=io.BytesIO(video_bytes),
            filename=f"tiktok_{video.author}_{interaction.id}.mp4"
        )
        
        view = VideoButtonView(
            video_url=video.video_url,
            original_url=url,
            author_name=video.author
        )
        
        message = await interaction.followup.send(embed=embed, file=file, view=view)
        view.message = message  # Simpan reference untuk timeout handler
    
    def _create_stats_bar(self, plays, likes, comments, shares):
        """Buat visual stats bar"""
        def format_num(n):
            if n >= 1_000_000:
                return f"{n/1_000_000:.1f}M"
            elif n >= 1_000:
                return f"{n/1_000:.1f}K"
            return str(n)
        
        # Tentukan "viral score"
        viral_score = min(10, int((plays / 100_000) + (likes / 10_000)))
        fire_emoji = "🔥" * (viral_score // 2) if viral_score > 0 else "❄️"
        
        return (
            f"{fire_emoji}\n"
            f"👁️ **{format_num(plays)}** views\n"
            f"❤️ **{format_num(likes)}** likes\n"
            f"💬 **{format_num(comments)}** comments\n"
            f"🔄 **{format_num(shares)}** shares"
        )
    
    @tt.error
    async def tt_error(self, interaction: discord.Interaction, error):
        """Error handler untuk command tt"""
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏱️ Cooldown",
                description=f"Command ini dalam cooldown. Coba lagi dalam `{error.retry_after:.1f}` detik.",
                color=config.EMBED_COLOR_ERROR
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            print(f"Error in tt command: {error}")

async def setup(bot: commands.Bot):
    await bot.add_cog(DownloaderCog(bot))