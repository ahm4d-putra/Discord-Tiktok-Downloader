"""
Discord Bot - TikTok Downloader with Buttons & Moderation
Main entry point
"""

import discord
from discord.ext import commands
import config
from utils.database import db
from utils.tiktok import tiktok_downloader
import asyncio
import io

# Intents
intents = discord.Intents.default()
intents.message_content = True  # Wajib untuk baca link di pesan
intents.guilds = True
intents.messages = True

class TikTokBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.BOT_PREFIX,
            intents=intents,
            description=config.BOT_DESCRIPTION
        )
        self.synced = False
    
    async def setup_hook(self):
        """Load semua cogs saat startup"""
        # Load commands
        await self.load_extension("commands.downloader")
        await self.load_extension("commands.setup")
        await self.load_extension("commands.help")
        await self.load_extension("commands.moderation")
        
        print("✅ All cogs loaded successfully")
    
    async def on_ready(self):
        """Event saat bot siap"""
        print(f"🤖 Logged in as {self.user.name} (ID: {self.user.id})")
        print(f"📊 Connected to {len(self.guilds)} guilds")
        
        # Force sync untuk guild tertentu (instant)
        if not self.synced:
            for guild in self.guilds:
                try:
                    synced = await self.tree.sync(guild=guild)
                    print(f"🔄 Synced {len(synced)} commands to {guild.name}")
                except Exception as e:
                    print(f"❌ Error syncing to {guild.name}: {e}")
            
            # Global sync (butuh waktu hingga 1 jam)
            try:
                synced = await self.tree.sync()
                print(f"🌐 Global synced: {len(synced)} commands")
                self.synced = True
            except Exception as e:
                print(f"❌ Global sync error: {e}")
        
        # Set presence
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="/help | TikTok Downloader 🔥"
            )
        )
        print("🚀 Bot is ready!")
    
    async def on_guild_join(self, guild: discord.Guild):
        """Event saat bot join guild baru"""
        print(f"➕ Joined guild: {guild.name} (ID: {guild.id})")
        
        # Sync commands ke guild baru
        try:
            synced = await self.tree.sync(guild=guild)
            print(f"🔄 Synced {len(synced)} commands to new guild {guild.name}")
        except Exception as e:
            print(f"❌ Error syncing to new guild: {e}")
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Event saat bot leave guild"""
        print(f"➖ Left guild: {guild.name} (ID: {guild.id})")
        # Cleanup database
        await db.remove_auto_channel(guild.id)
    
    async def on_message(self, message: discord.Message):
        """Event saat ada pesan baru - untuk auto-detect TikTok link dengan BUTTONS"""
        # Import di sini untuk avoid circular import
        from views.video_buttons import VideoButtonView
        
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Ignore DM
        if not message.guild:
            return
        
        # Cek apakah channel ini adalah auto-downloader channel
        auto_channel = await db.get_auto_channel(message.guild.id)
        
        if not auto_channel or message.channel.id != auto_channel:
            return
        
        # Cek apakah pesan mengandung link TikTok
        if not tiktok_downloader.is_tiktok_url(message.content):
            return
        
        # Cek permission
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        if not message.channel.permissions_for(message.guild.me).attach_files:
            await message.reply("❌ Bot tidak memiliki permission `Attach Files` di channel ini.", delete_after=10)
            return
        
        # Extract URL
        url = tiktok_downloader.extract_tiktok_url(message.content)
        
        # Typing indicator
        async with message.channel.typing():
            # Download info
            video = await tiktok_downloader.download_info(url)
            
            if not video:
                await message.reply("❌ Gagal mengambil video. Pastikan link valid dan video tidak private.", delete_after=15)
                return
            
            # Download video
            video_bytes = await tiktok_downloader.download_video_bytes(video.video_url)
            
            if not video_bytes:
                await message.reply("❌ Gagal mendownload file video.", delete_after=10)
                return
            
            # Cek ukuran file
            if len(video_bytes) > config.MAX_FILE_SIZE_BYTES:
                embed = discord.Embed(
                    title="⚠️ File Terlalu Besar",
                    description=f"Ukuran video ({len(video_bytes)/1024/1024:.1f}MB) melebihi batas.\n"
                               f"[Download manual]({video.video_url})",
                    color=config.EMBED_COLOR_ERROR
                )
                embed.set_image(url=video.cover_url)
                
                # Kasih button meskipun file besar
                view = VideoButtonView(
                    video_url=video.video_url,
                    original_url=url,
                    author_name=video.author
                )
                await message.reply(embed=embed, view=view)
                return
            
            # Buat embed KEREN
            embed = discord.Embed(
                title=f"🎵 {video.title[:100]}..." if len(video.title) > 100 else f"🎵 {video.title}",
                url=url,
                color=config.EMBED_COLOR_PRIMARY,
                timestamp=message.created_at
            )
            embed.set_author(
                name=f"@{video.author}",
                icon_url=video.author_avatar if video.author_avatar else None,
                url=f"https://tiktok.com/@{video.author}"
            )
            
            # Stats dengan visual
            def format_num(n):
                if n >= 1_000_000:
                    return f"{n/1_000_000:.1f}M"
                elif n >= 1_000:
                    return f"{n/1_000:.1f}K"
                return str(n)
            
            viral_score = min(10, int((video.play_count / 100_000) + (video.like_count / 10_000)))
            fire_emoji = "🔥" * (viral_score // 2) if viral_score > 0 else "❄️"
            
            embed.add_field(
                name="📊 Statistik",
                value=f"{fire_emoji}\n"
                      f"👁️ **{format_num(video.play_count)}** views\n"
                      f"❤️ **{format_num(video.like_count)}** likes\n"
                      f"💬 **{format_num(video.comment_count)}** comments\n"
                      f"🔄 **{format_num(video.share_count)}** shares",
                inline=False
            )
            embed.add_field(
                name="🎶 Musik",
                value=f"**{video.music_title}** - *{video.music_author}*",
                inline=False
            )
            embed.add_field(name="⏱️ Durasi", value=f"`{video.duration} detik`", inline=True)
            embed.add_field(name="📁 Ukuran", value=f"`{len(video_bytes)/1024/1024:.1f} MB`", inline=True)
            
            embed.set_thumbnail(url=video.cover_url)
            embed.set_footer(
                text=f"Auto-detect • Requested by {message.author.name} • Klik tombol di bawah",
                icon_url=message.author.avatar.url if message.author.avatar else None
            )
            
            # Kirim file dengan BUTTONS
            file = discord.File(
                fp=io.BytesIO(video_bytes),
                filename=f"tiktok_{video.author}_{message.id}.mp4"
            )
            
            view = VideoButtonView(
                video_url=video.video_url,
                original_url=url,
                author_name=video.author
            )
            
            sent_message = await message.reply(embed=embed, file=file, view=view, mention_author=False)
            view.message = sent_message

def main():
    """Main function"""
    bot = TikTokBot()
    
    # Error handler global
    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏱️ Cooldown",
                description=f"Command ini dalam cooldown. Coba lagi dalam `{error.retry_after:.1f}` detik.",
                color=config.EMBED_COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            print(f"Unhandled command error: {error}")
    
    # Run bot
    try:
        bot.run(config.BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid token! Please check your DISCORD_TOKEN in config.py or .env file")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()