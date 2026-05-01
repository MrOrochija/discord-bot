import disnake
from disnake.ext import commands
import datetime

token = "ВАШ_ТОКЕН_ЗДЕСЬ" # Замените на токен из Discord Developer Portal

LOG_CHANNEL_ID = 0000000000000000000 # Твой ID канала для логов

bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all())

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен и готов к работе!")

async def send_log(title, member, moderator, reason, color):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = disnake.Embed(
            title=title,
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Участник", value=f"{member.mention} ({member.id})", inline=False)
        embed.add_field(name="Модератор", value=moderator.mention, inline=True)
        embed.add_field(name="Причина", value=reason, inline=True)
        await channel.send(embed=embed)

@bot.slash_command(description="Выгнать пользователя с сервера")
@commands.has_permissions(kick_members=True)
async def kick(inter, member: disnake.Member, *, reason: str = "Причина не указана"):
    await member.kick(reason=reason)
    await inter.response.send_message(f"Пользователь {member.display_name} изгнан.", ephemeral=True)
    await send_log("🛑 Изгнание (KICK)", member, inter.author, reason, disnake.Color.orange())

@bot.slash_command(description="Забанить пользователя")
@commands.has_permissions(ban_members=True)
async def ban(inter, member: disnake.Member, *, reason: str = "Причина не указана"):
    await member.ban(reason=reason)
    await inter.response.send_message(f"Пользователь {member.display_name} забанен.", ephemeral=True)
    await send_log("🔴 Блокировка (BAN)", member, inter.author, reason, disnake.Color.red())

@kick.error
@ban.error
async def action_error(inter, error):
    if isinstance(error, commands.MissingPermissions):
        await inter.response.send_message("У вас недостаточно прав для этого действия!", ephemeral=True)
    else:
        await inter.response.send_message(f"Произошла ошибка: {error}", ephemeral=True)

@bot.slash_command(description="Очистить сообщения в канале")
@commands.has_permissions(manage_messages=True)
async def clear(
    inter, 
    amount: int = commands.Param(ge=1, le=100),
    member: disnake.Member = None
):
    await inter.response.defer(ephemeral=True)

    if member:
        def check(message):
            return message.author == member

        deleted = await inter.channel.purge(limit=amount, check=check)
        msg_text = f"Удалено **{len(deleted)}** сообщений от {member.mention}."
    else:
        deleted = await inter.channel.purge(limit=amount)
        msg_text = f"Удалено **{len(deleted)}** сообщений."

    await inter.edit_original_response(content=msg_text)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = disnake.Embed(
            title="🧹 Очистка сообщений",
            color=disnake.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Канал", value=inter.channel.mention, inline=True)
        embed.add_field(name="Модератор", value=inter.author.mention, inline=True)
        embed.add_field(name="Кол-во (макс)", value=amount, inline=True)
        if member:
            embed.add_field(name="Фильтр по юзеру", value=member.mention, inline=False)
        
        await log_channel.send(embed=embed)

@clear.error
async def clear_error(inter, error):
    if isinstance(error, commands.MissingPermissions):
        await inter.response.send_message("У вас нет прав на управление сообщениями!", ephemeral=True)

if __name__ == "__main__":
    bot.run(token)