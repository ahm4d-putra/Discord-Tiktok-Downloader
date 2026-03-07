"""
Moderation commands untuk bot Discord
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import config

class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.warns = {}  # Simple memory-based warnings
    
    # ===== KICK =====
    @app_commands.command(name="kick", description="Kick user dari server")
    @app_commands.describe(user="User yang mau di-kick", reason="Alasan kick")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Tidak ada alasan"):
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ Kamu tidak bisa kick user dengan role lebih tinggi!", ephemeral=True)
            return
        
        if user.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Bot tidak bisa kick user dengan role lebih tinggi!", ephemeral=True)
            return
        
        await user.kick(reason=f"{interaction.user.name}: {reason}")
        
        embed = discord.Embed(
            title="👢 User Dikick",
            description=f"**User:** {user.mention}\n**Alasan:** {reason}\n**Oleh:** {interaction.user.mention}",
            color=config.EMBED_COLOR_ERROR,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        
        await interaction.response.send_message(embed=embed)
    
    # ===== BAN =====
    @app_commands.command(name="ban", description="Ban user dari server")
    @app_commands.describe(user="User yang mau di-ban", reason="Alasan ban", delete_messages="Hapus pesan hari terakhir (0-7)")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Tidak ada alasan", delete_messages: int = 0):
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ Kamu tidak bisa ban user dengan role lebih tinggi!", ephemeral=True)
            return
        
        if user.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Bot tidak bisa ban user dengan role lebih tinggi!", ephemeral=True)
            return
        
        # Clamp delete_messages 0-7
        delete_days = max(0, min(7, delete_messages))
        
        await user.ban(reason=f"{interaction.user.name}: {reason}", delete_message_days=delete_days)
        
        embed = discord.Embed(
            title="🔨 User Diban",
            description=f"**User:** {user.mention}\n**Alasan:** {reason}\n**Hapus pesan:** {delete_days} hari\n**Oleh:** {interaction.user.mention}",
            color=config.EMBED_COLOR_ERROR,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        
        await interaction.response.send_message(embed=embed)
    
    # ===== UNBAN =====
    @app_commands.command(name="unban", description="Unban user dari server")
    @app_commands.describe(user_id="ID user yang mau di-unban", reason="Alasan unban")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "Tidak ada alasan"):
        try:
            user_id = int(user_id)
            banned_users = [entry async for entry in interaction.guild.bans()]
            
            banned_entry = None
            for entry in banned_users:
                if entry.user.id == user_id:
                    banned_entry = entry
                    break
            
            if not banned_entry:
                await interaction.response.send_message("❌ User tidak ditemukan di ban list!", ephemeral=True)
                return
            
            await interaction.guild.unban(banned_entry.user, reason=f"{interaction.user.name}: {reason}")
            
            embed = discord.Embed(
                title="🔓 User Diunban",
                description=f"**User:** {banned_entry.user.mention}\n**Alasan:** {reason}\n**Oleh:** {interaction.user.mention}",
                color=config.EMBED_COLOR_SUCCESS,
                timestamp=datetime.utcnow()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message("❌ ID user harus angka!", ephemeral=True)
    
    # ===== TIMEOUT / MUTE =====
    @app_commands.command(name="timeout", description="Mute user sementara (timeout)")
    @app_commands.describe(user="User yang mau di-timeout", duration="Durasi (contoh: 1h, 30m, 1d)", reason="Alasan timeout")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "Tidak ada alasan"):
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ Kamu tidak bisa timeout user dengan role lebih tinggi!", ephemeral=True)
            return
        
        if user.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Bot tidak bisa timeout user dengan role lebih tinggi!", ephemeral=True)
            return
        
        # Parse duration
        try:
            time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            unit = duration[-1].lower()
            value = int(duration[:-1])
            
            if unit not in time_units:
                raise ValueError
            
            seconds = value * time_units[unit]
            
            # Max 28 hari (Discord limit)
            if seconds > 2419200:
                await interaction.response.send_message("❌ Maksimal timeout 28 hari!", ephemeral=True)
                return
            
            delta = timedelta(seconds=seconds)
            until = datetime.utcnow() + delta
            
            await user.timeout(until, reason=f"{interaction.user.name}: {reason}")
            
            embed = discord.Embed(
                title="🔇 User Di-timeout",
                description=f"**User:** {user.mention}\n**Durasi:** {duration}\n**Sampai:** <t:{int(until.timestamp())}:R>\n**Alasan:** {reason}\n**Oleh:** {interaction.user.mention}",
                color=config.EMBED_COLOR_ERROR,
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
            
            await interaction.response.send_message(embed=embed)
            
        except (ValueError, IndexError):
            await interaction.response.send_message("❌ Format durasi salah! Gunakan: `30s`, `5m`, `2h`, `1d`", ephemeral=True)
    
    # ===== REMOVE TIMEOUT =====
    @app_commands.command(name="untimeout", description="Hapus timeout user")
    @app_commands.describe(user="User yang mau di-untimeout", reason="Alasan")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def untimeout(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Tidak ada alasan"):
        if not user.is_timed_out():
            await interaction.response.send_message("❌ User tidak sedang di-timeout!", ephemeral=True)
            return
        
        await user.timeout(None, reason=f"{interaction.user.name}: {reason}")
        
        embed = discord.Embed(
            title="🔊 Timeout Dihapus",
            description=f"**User:** {user.mention}\n**Alasan:** {reason}\n**Oleh:** {interaction.user.mention}",
            color=config.EMBED_COLOR_SUCCESS,
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ===== WARN =====
    @app_commands.command(name="warn", description="Beri peringatan ke user")
    @app_commands.describe(user="User yang mau di-warn", reason="Alasan warn")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ Kamu tidak bisa warn user dengan role lebih tinggi!", ephemeral=True)
            return
        
        guild_id = str(interaction.guild_id)
        user_id = str(user.id)
        
        if guild_id not in self.warns:
            self.warns[guild_id] = {}
        
        if user_id not in self.warns[guild_id]:
            self.warns[guild_id][user_id] = []
        
        warn_data = {
            "reason": reason,
            "by": interaction.user.name,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        }
        
        self.warns[guild_id][user_id].append(warn_data)
        warn_count = len(self.warns[guild_id][user_id])
        
        embed = discord.Embed(
            title="⚠️ User Di-warn",
            description=f"**User:** {user.mention}\n**Alasan:** {reason}\n**Total warn:** {warn_count}\n**Oleh:** {interaction.user.mention}",
            color=0xFFA500,
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Auto kick/kick/ban berdasarkan warn count (opsional)
        if warn_count >= 3:
            kick_embed = discord.Embed(
                title="👢 Auto Kick",
                description=f"{user.mention} di-kick otomatis karena sudah {warn_count} warn!",
                color=config.EMBED_COLOR_ERROR
            )
            await interaction.channel.send(embed=kick_embed)
            await user.kick(reason=f"Auto kick: {warn_count} warnings")
    
    # ===== WARNINGS (LIHAT HISTORY) =====
    @app_commands.command(name="warnings", description="Lihat history warn user")
    @app_commands.describe(user="User yang mau dicek")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        guild_id = str(interaction.guild_id)
        user_id = str(user.id)
        
        user_warns = self.warns.get(guild_id, {}).get(user_id, [])
        
        if not user_warns:
            await interaction.response.send_message(f"✅ {user.mention} tidak memiliki warn!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"⚠️ Warnings - {user.name}",
            description=f"Total: **{len(user_warns)}** warn",
            color=0xFFA500,
            timestamp=datetime.utcnow()
        )
        
        for i, warn in enumerate(user_warns, 1):
            embed.add_field(
                name=f"Warn #{i}",
                value=f"**Alasan:** {warn['reason']}\n**Oleh:** {warn['by']}\n**Waktu:** {warn['time']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ===== CLEAR WARN =====
    @app_commands.command(name="clearwarn", description="Hapus semua warn user")
    @app_commands.describe(user="User yang mau di-clear warn")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clearwarn(self, interaction: discord.Interaction, user: discord.Member):
        guild_id = str(interaction.guild_id)
        user_id = str(user.id)
        
        if guild_id in self.warns and user_id in self.warns[guild_id]:
            del self.warns[guild_id][user_id]
            
            embed = discord.Embed(
                title="🗑️ Warnings Dihapus",
                description=f"Semua warn {user.mention} telah dihapus oleh {interaction.user.mention}",
                color=config.EMBED_COLOR_SUCCESS,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {user.mention} tidak memiliki warn!", ephemeral=True)
    
    # ===== CLEAR MESSAGES =====
    @app_commands.command(name="clear", description="Hapus pesan di channel")
    @app_commands.describe(amount="Jumlah pesan yang mau dihapus (1-100)", user="Hapus pesan dari user spesifik (opsional)")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int, user: discord.Member = None):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Jumlah harus antara 1-100!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        def check(msg):
            if user:
                return msg.author.id == user.id
            return True
        
        deleted = await interaction.channel.purge(limit=amount, check=check)
        
        embed = discord.Embed(
            title="🗑️ Pesan Dihapus",
            description=f"**{len(deleted)}** pesan dihapus{' dari ' + user.mention if user else ''}",
            color=config.EMBED_COLOR_SUCCESS
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ===== SLOWMODE =====
    @app_commands.command(name="slowmode", description="Atur slowmode channel")
    @app_commands.describe(seconds="Detik slowmode (0 untuk matikan)")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        if seconds < 0 or seconds > 21600:  # Max 6 jam
            await interaction.response.send_message("❌ Slowmode harus 0-21600 detik (6 jam)!", ephemeral=True)
            return
        
        await interaction.channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            embed = discord.Embed(
                title="🐇 Slowmode Dimatikan",
                description=f"Slowmode di {interaction.channel.mention} telah dimatikan oleh {interaction.user.mention}",
                color=config.EMBED_COLOR_SUCCESS
            )
        else:
            embed = discord.Embed(
                title="🐢 Slowmode Diaktifkan",
                description=f"Slowmode di {interaction.channel.mention} diatur ke **{seconds}** detik oleh {interaction.user.mention}",
                color=config.EMBED_COLOR_INFO
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ===== LOCK / UNLOCK CHANNEL =====
    @app_commands.command(name="lock", description="Kunci channel (hanya role tertentu bisa kirim pesan)")
    @app_commands.describe(reason="Alasan lock")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction, reason: str = "Tidak ada alasan"):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        
        embed = discord.Embed(
            title="🔒 Channel Dikunci",
            description=f"{interaction.channel.mention} telah dikunci!\n**Alasan:** {reason}\n**Oleh:** {interaction.user.mention}",
            color=config.EMBED_COLOR_ERROR,
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unlock", description="Buka kunci channel")
    @app_commands.describe(reason="Alasan unlock")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction, reason: str = "Tidak ada alasan"):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        
        embed = discord.Embed(
            title="🔓 Channel Dibuka",
            description=f"{interaction.channel.mention} telah dibuka!\n**Alasan:** {reason}\n**Oleh:** {interaction.user.mention}",
            color=config.EMBED_COLOR_SUCCESS,
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ===== ERROR HANDLERS =====
    @kick.error
    @ban.error
    @unban.error
    @timeout.error
    @untimeout.error
    @warn.error
    @warnings.error
    @clearwarn.error
    @clear.error
    @slowmode.error
    @lock.error
    @unlock.error
    async def mod_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permission Ditolak",
                description="Kamu tidak memiliki permission untuk command ini!",
                color=config.EMBED_COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif isinstance(error, app_commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Permission Kurang",
                description="Bot tidak memiliki permission yang diperlukan!",
                color=config.EMBED_COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        else:
            print(f"Moderation error: {error}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))